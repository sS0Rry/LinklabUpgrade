#!/usr/bin/python

#######################################################
# make_linklab.py - Builds a NJU:ICS link bomb 
#
# Copyright (c) 2018, Feng SU, All rights reserved.
#######################################################

import os
import sys
import random
import shutil


########################################################
# Settings


########################################################
# Helpers


########################################################
# Interfaces

def process(bomb_id, src_dir, bomb_dir, bomb_datapack):
 
    if len(bomb_id.strip()) <= 0:
        return False

    # bomb_id, src_dir, bomb_dir, bomb_datapack
    command = r'python3 ' + os.path.join(src_dir,'makebomb.py') + r' ' + bomb_id + r' ' + src_dir + r' ' + bomb_dir + r' ' + bomb_datapack
    os.system(command)

    return os.path.isfile(bomb_datapack)


def batch_process(file_list, src_dir, bombroot_dir):
    status = True

    #Prepare tools
    command = r'gcc -o ' + os.path.join(src_dir,'elfzero') + r' ' + os.path.join(src_dir,'elfzero.c')
    os.system(command)

    lf = open(file_list)
    for line in lf:
        linedata = line.rstrip()
        record = linedata.split(',')

        id = record[0]
        if len(id.strip()) <= 0:
            continue
        bomb_dir = os.path.join(bombroot_dir,id)
        bomb_datapack = os.path.join(bombroot_dir,id+'.tar')
        
        result = process(id, src_dir, bomb_dir, bomb_datapack)
        if not result:
            print('ERROR: Failed to generate lab data for ID: <' + id + '>!')
            status = False
        else:
            print('Lab data for ID: <' + id + '> has been generated.')
    lf.close()

    return status


if __name__ == "__main__":
    random.seed()

    status = True
    if os.path.isfile(sys.argv[1]):
        status = batch_process(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        status = process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    if status:
        print('OK: Data have been generated.')
    else:
        print('ERROR: Failed to generate data!')
