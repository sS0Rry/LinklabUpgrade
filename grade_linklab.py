#!/usr/bin/python

#######################################################
# grade_linklab.py - Autograding script for NJU:ICS linklab 
#
# Copyright (c) 2018, Feng SU, All rights reserved.
#######################################################

#
# Note: please run this script as an unprivileged user,
# as the script will link and run user-provided program.
#

import os
import sys
import tempfile
import shutil
import subprocess


PROGRAM_FILE = 'linkbomb'
SOLUTION_FILE = 'solution.txt'
TOOL_FILES = [ 'elfzero' ]
SOURCE_FILES = [ 'main.o', 'phase2.o' ]
PHASE_FILES = [ ['main.o', 'phase1.o'], ['main.o', 'phase2.o', 'phase2_patch.o'], ['main.o', 'phase3.o'] ]
PHASE_HANDIN = [ ['phase1.o'], ['phase2.o'], ['phase2_patch.o'], ['phase3.o']]
CHECK_FILES = [ 'phase1.o', 'phase2.o', 'phase3.o']
REFERENCE_DIR = 'reference'


########################################################
# Helpers

def check_phase_files(phase_files):

    for file in phase_files:
        if not os.path.isfile(file):
            return False
    return True


def copy_grading_files(dir_bomb, dir_work, file_list):
    result = ''
    for file_name in file_list:
        src_file_path = os.path.join(dir_bomb, file_name)
        if not os.path.isfile(src_file_path):
            result = 'ERROR: Source file ' + file_name + ' cannot be located in ' + dir_bomb
            print('ERROR: Source file ' + file_name + ' cannot be located in ' + dir_bomb)
            return False, result

        dst_file_path = os.path.join(dir_work, file_name)
        if os.path.isfile(dst_file_path):
            os.remove(dst_file_path)  # 删除已存在的文件

        try:
            shutil.copy2(src_file_path, dst_file_path)
        except Exception as e:
            result = 'ERROR: Failed to copy ' + file_name + ' to ' + dir_work + '. ' + str(e)
            print('ERROR: Failed to copy ' + file_name + ' to ' + dir_work + '. ' + str(e))
            return False, result

        if not os.path.isfile(dst_file_path):
            result = 'ERROR: Destination file ' + file_name + ' cannot be created in ' + dir_work
            print('ERROR: Destination file ' + file_name + ' cannot be created in ' + dir_work)
            return False, result

    return True, result


########################################################
# Interfaces

# file_handin: tarball containing user-submiited bomb result
# dir_bomb: directory containing user-specific original bomb data
# dir_src: directory containing 'template' sources of all bombs
scores = {}

def process(work_id, file_handin, dir_bomb, dir_src):

    grade = []
    result = ''
    #Check naming & typing of handin files
    pl = os.path.basename(file_handin).split('.')
    if len(pl) < 2:
        result = 'ERROR: <' + file_handin + '> is not typed!'
        print('ERROR not typed')
        return grade, result

    work_type = pl[len(pl)-1]
    if work_type.upper() != 'TAR':
        result = 'ERROR: <' + file_handin + '> is wrongly typed!'
        print('error wrong')
        return grade, result

    #Extract handin files
    dir_work = tempfile.mkdtemp()
    if not os.path.isdir(dir_work):
        result = 'ERROR: CANNOT create temporary directory for grading!'
        print('error cannot')
        return grade, result
    else:
        os.chmod(dir_work, 0o755)

    command = 'tar xf "' + file_handin + '" -C "' + dir_work + '"'
    os.system(command)

    #Collect files in deep directories
    command = "find '" + dir_work + "' -mindepth 2 -type f -exec mv '{}' '" + dir_work + "/' \;"
    os.system(command)

    #Prepare tool files
    for tool_file in TOOL_FILES:
        tool_path = os.path.join(dir_src, tool_file)
        if not os.path.isfile(tool_path):
            command = 'gcc -o "' + tool_path + '" "' + tool_path + '.c"'
            os.system(command)
            if not os.path.isfile(tool_path):
                shutil.rmtree(dir_work, True)

                result = 'ERROR: Tool <' + tool_file + '> is unavailable!'
                print('error unavailable')
                return grade, result

    copy_succeed, copy_result = copy_grading_files(dir_src, dir_work, TOOL_FILES)
    if not copy_succeed:
        shutil.rmtree(dir_work, True)
        print('error copy fail')
        result = copy_result
        return grade, result

    #Prepare grading files
    dir_reference = os.path.join(dir_work, REFERENCE_DIR)
    if os.path.isdir(dir_reference):
        shutil.rmtree(dir_reference, True)
    os.makedirs(dir_reference)
    if not os.path.isdir(dir_reference):
        shutil.rmtree(dir_work, True)
        print('ERROR: Reference directory cannot be created!')
        result = 'ERROR: Reference directory cannot be created!'
        return grade, result

    copy_succeed, copy_result = copy_grading_files(dir_bomb, dir_reference, CHECK_FILES)
    if not copy_succeed:
        shutil.rmtree(dir_work, True)
        print('ERROR: copy directory cannot be created!')
        result = copy_result
        return grade, result

    copy_succeed, copy_result = copy_grading_files(dir_bomb, dir_work, SOURCE_FILES)
    if not copy_succeed:
        shutil.rmtree(dir_work, True)
        print('ERROR: copy directory cannot be created!')
        result = copy_result
        return grade, result

    #Load solutions
    sf = open(os.path.join(dir_bomb,SOLUTION_FILE), 'r')
    solution_lines = sf.readlines()
    sf.close()

    #####################################################
    #Record current working directory for later restoration
    cwd_path = os.getcwd()
    os.chdir(dir_work)

    #Grading
    for phase in range(len(PHASE_FILES)):
        if os.path.isfile(PROGRAM_FILE):
            os.remove(PROGRAM_FILE)
        if not check_phase_files(PHASE_FILES[phase]):
            continue

        command = 'gcc -fno-pie -no-pie -o ' + PROGRAM_FILE
        for file in PHASE_FILES[phase]:
            command = command + r' ' + file
        compile_status = os.system(command)
        if compile_status != 0:
            print(f"Compilation failed for phase {phase + 1}. Command: {command}")
            continue
        if not os.path.isfile(PROGRAM_FILE):
            continue
        else:
            os.chmod(PROGRAM_FILE, 0o755)

        # Match with solution string
        command = './' + PROGRAM_FILE
        pf = os.popen(command)
        output = pf.read()
        pf.close()

        result = result + '\n\n' + output

        if output != solution_lines[phase]:
            continue

        grade.append(phase + 1)

    #Clean up
    if os.path.isfile(PROGRAM_FILE):
        os.remove(PROGRAM_FILE)

    #Restore original working directory
    os.chdir(cwd_path)
    ######################################################

    #Clean up
    shutil.rmtree(dir_work, True)

    #Restore score
    scores[work_id] = {
        'len(grade)' : len(grade),
        'grade' : grade
    }

    return grade, result


# dir_grade: root directory containing submiited bomb results of all users
# dir_bomb: root directory containing bomb data of all users
# dir_src: directory containing 'template' sources of all bombs
def batch_process(dir_handin, dir_bomb, dir_src, file_grade):

    scores = {}
    results = {}

    ####
    gf = open(file_grade, 'w')

    error_list = []
    for file_name in sorted(os.listdir(dir_handin)):
        pl = file_name.split('.')
        if len(pl) < 2:
            error_list.append(file_name)
            #print('ERROR: <' + file_name + '> contains no ID!')
            continue

        work_id = pl[len(pl)-2]

        #Grade handin file
        file_handin = os.path.join(dir_handin, file_name)

        grade, result = process(work_id, file_handin, os.path.join(dir_bomb,work_id), dir_src)

        # Collect
        scores[work_id] = grade
        gf.write(work_id + r',' + str(len(grade)) + r',' + str(grade) + '\n')

        results[work_id] = result

    # Log errors
    for error in error_list:
        gf.write(r'ERROR: ' + error + '\n')

    gf.close()
    return scores, results


if __name__ == "__main__":
    scores = {}
    if os.path.isdir(sys.argv[1]):
        scores, results = batch_process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        scores[sys.argv[1]], result = process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    ids = sorted(scores.keys())
    for id in ids:
        grade = scores[id]
        print(id + r': ' + str(len(grade)) + r' @ ' + str(grade))

