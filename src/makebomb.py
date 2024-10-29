#!/usr/bin/python

#######################################################
# make_linklab.py - Builds a NJU:ICS link bomb 
#
# Copyright (c) 2021, Feng SU, All rights reserved.
#######################################################

import os
import sys
import string
import random
import shutil


########################################################
# Settings

PROJECT_FILES = [ 'main.c', 'phase1.c', 'phase2.c', 'phase3.c', 'phase3_patch.c', 'phase4.c', 'phase5.c', 'phase6.c', 'elfzero' ]
COMPILE_FILES = [ 'main.c', 'phase1.c', 'phase2.c', 'phase3.c', 'phase3_patch.c', 'phase4.c', 'phase5.c' ]
COMPILE_PIC_FILES = [ 'phase6.c' ]
HANDOUT_FILES = [ 'main.o', 'phase1.o', 'phase2.o', 'phase3.o', 'phase4.o', 'phase5.o', 'phase6.o' ]
HANDIN_FILES = [ 'phase1.o', 'phase2.o', 'phase3_patch.o', 'phase4.o', 'phase5.o', 'phase6.o' ]
PHASE_FILES = [ 'main.o phase1.o', 'main.o phase2.o', 'main.o phase3.o phase3_patch.o', 'main.o phase4.o', 'main.o phase5.o', 'main.o phase6.o' ]
PHASE_CMDOPTS = [ '', '', '', '', '', '' ]
SOLUTION_FILE = 'solution.txt'
SOLUTION_DIR = 'solution'
SOLUTION_PROGRAM = '_linkbomb'

PHASE5_RELOC_ITEMS = [ 'transform_code', 'encode_1' ]
PHASE5_RELOC_COUNT = 2
PHASE5_RELOC_RAND_ITEMS = [ 'generate_code', 'encoder', 'encode_2' ]
PHASE5_RELOC_RAND_COUNT = 5

PHASE6_RELOC_ITEMS = [ 'generate_code', '_GLOBAL_OFFSET_TABLE_' ]
PHASE6_RELOC_COUNT = 3
PHASE6_RELOC_RAND_ITEMS = [ 'transform_code', 'encoder' ]
PHASE6_RELOC_RAND_COUNT = 5


########################################################
# Helpers

def make_config(id, phases, file_include):

    # Declare global variables
    global PHASE5_RELOC_ITEMS, PHASE5_RELOC_RAND_ITEMS, PHASE6_RELOC_ITEMS, PHASE6_RELOC_RAND_ITEMS

    ########
    fi = open(file_include, 'w')

    #### ID ####
    fi.write(r'#define MYID ' + '"' + id + '"' + os.linesep)

    #### Randomization ####
    RAND_ARRAY_NAME = ''
    for i in range(6):
        RAND_ARRAY_NAME = RAND_ARRAY_NAME + random.choice(string.ascii_letters)
    fi.write(r'#define RAND_ARRAY_NAME ' + RAND_ARRAY_NAME + os.linesep)

    RAND_ARRAY_SIZE = random.randint(16, 128)
    fi.write(r'#define RAND_ARRAY_SIZE ' + '%d'%RAND_ARRAY_SIZE + os.linesep)

    RAND_ARRAY_INIT_VALUE = '{'
    for i in range(RAND_ARRAY_SIZE):
        num = random.randint(-32767, +32767)
        RAND_ARRAY_INIT_VALUE = RAND_ARRAY_INIT_VALUE + '%d, '%num
    RAND_ARRAY_INIT_VALUE = RAND_ARRAY_INIT_VALUE + '}'
    fi.write(r'#define RAND_ARRAY_INIT_VALUE ' + RAND_ARRAY_INIT_VALUE + os.linesep)

    RAND_STRING_NAME = ''
    for i in range(8):
        RAND_STRING_NAME = RAND_STRING_NAME + random.choice(string.ascii_letters)
    fi.write(r'#define RAND_STRING_NAME ' + RAND_STRING_NAME + os.linesep)

    RAND_STRING_SIZE = random.randint(4, 32)
    fi.write(r'#define RAND_STRING_SIZE ' + '%d'%RAND_STRING_SIZE + os.linesep)

    RAND_STRING_INIT_VALUE = '"'
    for i in range(RAND_STRING_SIZE):
        RAND_STRING_INIT_VALUE = RAND_STRING_INIT_VALUE + random.choice(string.ascii_letters)
    RAND_STRING_INIT_VALUE = RAND_STRING_INIT_VALUE + '"'
    fi.write(r'#define RAND_STRING_INIT_VALUE ' + RAND_STRING_INIT_VALUE + os.linesep)

    #### Buffer (PHASE 1/5/6) ####
    BUFVAR = ''
    for i in range(0,8):
        BUFVAR = BUFVAR + random.choice(string.ascii_letters)
    fi.write(r'#define BUFVAR ' + BUFVAR + os.linesep)

    BUFLEN = random.randint(64, 256)

    BUFDAT = '"'
    charbook = string.ascii_letters + string.digits + " \t";
    for i in range(0,BUFLEN):
        BUFDAT = BUFDAT + random.choice(charbook)
    BUFDAT = BUFDAT + '"'
    fi.write(r'#define BUFDAT ' + BUFDAT + os.linesep)

    BUFPOS = random.randint(0, round(BUFLEN/2))
    fi.write(r'#define BUFPOS ' + str(BUFPOS) + os.linesep)

    fi.write(r'#define BUFLEN ' + str(BUFLEN-BUFPOS-1) + os.linesep)

    #### PHASE 2 ####
    OUTPUT_FUNC_NAME = ''
    for i in range(0,8):
        OUTPUT_FUNC_NAME = OUTPUT_FUNC_NAME + random.choice(string.ascii_letters)
    fi.write(r'#define OUTPUT_FUNC_NAME ' + OUTPUT_FUNC_NAME + os.linesep)

    DECOY_FUNC_NAME = ''
    for i in range(0,10):
        DECOY_FUNC_NAME = DECOY_FUNC_NAME + random.choice(string.ascii_letters)
    fi.write(r'#define DECOY_FUNC_NAME ' + DECOY_FUNC_NAME + os.linesep)

    PHASE2_KEYSTR = ''
    for i in range(0,7):
        PHASE2_KEYSTR = PHASE2_KEYSTR + random.choice(string.ascii_letters)
    fi.write(r'#define PHASE2_KEYSTR ' + r'"' + PHASE2_KEYSTR + r'"' + os.linesep)

    PHASE2_COOKIE = '"'
    charbook = string.ascii_letters + string.digits + " \t";
    for i in range(random.randint(4,64)):
        PHASE2_COOKIE = PHASE2_COOKIE + random.choice(charbook)
    PHASE2_COOKIE = PHASE2_COOKIE + '"'
    fi.write(r'#define PHASE2_COOKIE ' + PHASE2_COOKIE + os.linesep)

    #### PHASE 3 ####
    PHASE3_COOKIE = ''
    for c in random.sample(string.ascii_lowercase,len(id)):
        PHASE3_COOKIE = PHASE3_COOKIE + c
    fi.write(r'#define PHASE3_COOKIE ' + r'"' + PHASE3_COOKIE + r'"' + os.linesep)

    PHASE3_CODEBOOK = ''
    for i in range(0,10):
        PHASE3_CODEBOOK = PHASE3_CODEBOOK + random.choice(string.ascii_letters)
    fi.write(r'#define PHASE3_CODEBOOK ' + PHASE3_CODEBOOK + os.linesep)

    PHASE3_CODEBOOK_DAT = [' ' for x in range(256)]
    for i in range(0,len(PHASE3_COOKIE)):
        PHASE3_CODEBOOK_DAT[ord(PHASE3_COOKIE[i])] = id[i]
    PHASE3_CODEBOOK_STR = '{'
    for c in PHASE3_CODEBOOK_DAT:
        PHASE3_CODEBOOK_STR = PHASE3_CODEBOOK_STR + "'" + c + "',"
    PHASE3_CODEBOOK_STR = PHASE3_CODEBOOK_STR + '}'
    fi.write(r'#define PHASE3_CODEBOOK_DAT ' + PHASE3_CODEBOOK_STR + os.linesep)

    PHASE3_FUNCNAME = ''
    for i in range(0,10):
        PHASE3_FUNCNAME = PHASE3_FUNCNAME + random.choice(string.ascii_letters)
    fi.write(r'#define PHASE3_FUNCNAME ' + PHASE3_FUNCNAME + os.linesep)

    #### PHASE 4 ####
    PHASE4_COOKIE = ''
    for c in random.sample(string.ascii_uppercase,len(id)):
        PHASE4_COOKIE = PHASE4_COOKIE + c
    fi.write(r'#define PHASE4_COOKIE ' + r'"' + PHASE4_COOKIE + r'"' + os.linesep)

    PHASE4_CASES = list(range(0,len(string.ascii_uppercase)))
    random.shuffle(PHASE4_CASES)
    for i in range(0,len(PHASE4_CASES)):
        fi.write(r'#define CASE_' + string.ascii_uppercase[i] + r" '" + string.ascii_uppercase[PHASE4_CASES[i]] + r"'" + os.linesep)

    PHASE4_DO_CASES = ['' for i in range(len(PHASE4_CASES))]
    for i in range(0,len(PHASE4_DO_CASES)):
        PHASE4_DO_CASES[i] = r"{ c = " + str(random.randint(0x3A,0x7E)) + r"; break; }"
    DIGIT = 0x30
    for i in random.sample(range(0,len(PHASE4_DO_CASES)), 10):
        PHASE4_DO_CASES[i] = r"{ c = " + str(DIGIT) + r"; break; }"
        DIGIT = DIGIT + 1
    random.shuffle(PHASE4_DO_CASES)
    for i in range(0,len(PHASE4_DO_CASES)):
        fi.write(r'#define DO_CASE_' + string.ascii_uppercase[i] + r" " + PHASE4_DO_CASES[i] + os.linesep)

    #### PHASE 5 ####
    PHASE5_COOKIE = random.randint(128, 255)
    fi.write(r'#define PHASE5_COOKIE ' + str(PHASE5_COOKIE) + os.linesep)

    CODE = ''
    for i in range(0,6):
        CODE = CODE + random.choice(string.ascii_letters)
    fi.write(r'#define CODE ' + CODE + os.linesep)

    CODE_TRAN_ARRAY = ''
    for i in range(6):
        CODE_TRAN_ARRAY = CODE_TRAN_ARRAY + random.choice(string.ascii_letters)
    fi.write(r'#define CODE_TRAN_ARRAY ' + CODE_TRAN_ARRAY + os.linesep)

    CODE_TRAN_ARRAY_SIZE = random.randint(8, 16)
    CODE_TRAN_ARRAY_INIT_VALUE = '{'
    for i in range(CODE_TRAN_ARRAY_SIZE):
        num = random.randint(-32767, +32767)
        CODE_TRAN_ARRAY_INIT_VALUE = CODE_TRAN_ARRAY_INIT_VALUE + '%d, '%num
    CODE_TRAN_ARRAY_INIT_VALUE = CODE_TRAN_ARRAY_INIT_VALUE + '}'
    fi.write(r'#define CODE_TRAN_ARRAY_INIT_VALUE ' + CODE_TRAN_ARRAY_INIT_VALUE + os.linesep)

    FDICT = ''
    for i in range(6):
        FDICT = FDICT + random.choice(string.ascii_letters)
    fi.write(r'#define FDICT ' + FDICT + os.linesep)

    RDICT = ''
    for i in range(6):
        RDICT = RDICT + random.choice(string.ascii_letters)
    fi.write(r'#define RDICT ' + RDICT + os.linesep)

    sdict = list(range(32,127))
    random.shuffle(sdict)
    fdict = list(range(0,128))
    fdict[32:127] = sdict
    rdict = list(range(0,128))
    for i in range(32,127):
        rdict[fdict[i]] = i

    FDICTDAT = '{' + str(fdict[0])
    RDICTDAT = '{' + str(rdict[0])
    #dictbook = string.ascii_letters + string.digits + string.punctuation;
    for i in range(1,128):
        FDICTDAT = FDICTDAT + ',' + str(fdict[i])
        RDICTDAT = RDICTDAT + ',' + str(rdict[i])
    FDICTDAT = FDICTDAT + '}'
    RDICTDAT = RDICTDAT + '}'
    fi.write(r'#define FDICTDAT ' + FDICTDAT + os.linesep)
    fi.write(r'#define RDICTDAT ' + RDICTDAT + os.linesep)

    ENCODER_ID = random.randint(0, 1)
    fi.write(r'#define ENCODER_ID ' + str(ENCODER_ID) + os.linesep)

    #### PHASE 6 ####
    PHASE6_COOKIE = random.randint(128, 255)
    fi.write(r'#define PHASE6_COOKIE ' + str(PHASE6_COOKIE) + os.linesep)

    ########
    fi.close()

    # Update global variables
    PHASE5_RELOC_ITEMS = PHASE5_RELOC_ITEMS + [ BUFVAR ]
    PHASE5_RELOC_RAND_ITEMS = PHASE5_RELOC_RAND_ITEMS + [ CODE_TRAN_ARRAY, CODE, FDICT ]
  
    PHASE6_RELOC_ITEMS = PHASE6_RELOC_ITEMS + [ FDICT ]
    PHASE6_RELOC_RAND_ITEMS = PHASE6_RELOC_RAND_ITEMS + [ BUFVAR, CODE_TRAN_ARRAY, CODE ]


def compile_object(compile_flags, source_files, source_pic_files):

    for file in source_files:
        command = 'gcc -fno-pie -fcommon -O0 ' + compile_flags + ' -c ' + file
        os.system(command)

    for file in source_pic_files:
        command = 'gcc -fno-pie -fcommon -O0 ' + compile_flags + ' -fPIC -c ' + file
        os.system(command)


def patch_relocation(obj_file, reloc_items, reloc_count, item_to_randomized = False):

    reloc_item_set = reloc_items
    if item_to_randomized and len(reloc_items)>reloc_count:
        reloc_item_set = random.sample(reloc_items, reloc_count)

    reloc_indices = []
    for reloc_item in reloc_item_set:
        command = './elfzero rq ' + reloc_item + ' ' + obj_file

        pf = os.popen(command)
        output = pf.read()
        pf.close()

        indices = output.split()
        reloc_indices = reloc_indices + indices

    reloc_index_set = reloc_indices
    if len(reloc_indices) > reloc_count:
        reloc_index_set = random.sample(reloc_indices, reloc_count)

    for reloc_index in reloc_index_set:
        command = './elfzero rz ' + reloc_index + ' ' + obj_file
        os.system(command)

    return reloc_index_set


########################################################
# Interfaces

def make_bomb(bomb_id, src_dir, bomb_dir, bomb_datapack):

    if not os.path.isdir(src_dir):
        return False

    if not os.path.isfile(os.path.join(src_dir,'elfzero')):
        command = r'gcc -o ' + os.path.join(src_dir,'elfzero') + r' ' + os.path.join(src_dir,'elfzero.c')
        os.system(command)

    #Prepare & copy source files and tools
    if not os.path.isdir(bomb_dir):
        os.makedirs(bomb_dir)

    for file in PROJECT_FILES:
        shutil.copy2(os.path.join(src_dir,file), bomb_dir)

    make_config(bomb_id, [0,1,2,3,4,5,6,7], os.path.join(bomb_dir,'config.h'))

    ####################################################
    #Record current working directory for later restoration
    cwd_path = os.getcwd()
    os.chdir(bomb_dir)

    #Generate target files
    compile_object('', COMPILE_FILES, COMPILE_PIC_FILES)

    #Patch target files
    patch_relocation('phase5.o', PHASE5_RELOC_ITEMS, PHASE5_RELOC_COUNT, True)
    patch_relocation('phase5.o', PHASE5_RELOC_RAND_ITEMS, PHASE5_RELOC_RAND_COUNT, False)

    patch_relocation('phase6.o', PHASE6_RELOC_ITEMS, PHASE6_RELOC_COUNT, True)
    patch_relocation('phase6.o', PHASE6_RELOC_RAND_ITEMS, PHASE6_RELOC_RAND_COUNT, False)

    #Generate solution file (for autograding)
    os.makedirs(SOLUTION_DIR)

    for file in COMPILE_FILES+COMPILE_PIC_FILES:
        shutil.copy2(file, SOLUTION_DIR)

    cwd_path_bomb = os.getcwd()
    os.chdir(SOLUTION_DIR)

    compile_object('-I.. -D_SOLUTION_', COMPILE_FILES, COMPILE_PIC_FILES)

    command = r'cat /dev/null > ' + SOLUTION_FILE
    os.system(command)
    for phase in range(0,len(PHASE_FILES)):
        command = r'gcc -fcommon -fno-pie -no-pie -o ' + SOLUTION_PROGRAM + r' ' + PHASE_FILES[phase]
        os.system(command)

        command = r'./' + SOLUTION_PROGRAM + r' ' + PHASE_CMDOPTS[phase] + r' >> ' + SOLUTION_FILE
        os.system(command)

    os.chdir(cwd_path_bomb)

    shutil.copy2(os.path.join(SOLUTION_DIR,SOLUTION_FILE), '.')

    #Clean up
    for file in os.listdir(SOLUTION_DIR):
        if file not in HANDIN_FILES:
            os.remove(os.path.join(SOLUTION_DIR,file))

    #Restore original working directory
    os.chdir(cwd_path)
	####################################################

    # Pack handout
    file_set = ''
    for file in HANDOUT_FILES:
        file_set = file_set + r' ' + file

    command = 'tar cf ' + bomb_datapack + ' -C ' + bomb_dir + file_set
    os.system(command)

    return os.path.isfile(bomb_datapack)


if __name__ == "__main__":
    random.seed(17)

    status = make_bomb(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    if status:
        sys.exit(0)
    else:
        sys.exit(1)
