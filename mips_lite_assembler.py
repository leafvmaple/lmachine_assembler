import os
import sys
import re

REGISTER = {
    "$zero" : 0,
    "$v0"   : 2,
    "$v1"   : 3,
    "$s0"   : 16
}

I_TYPE = {
    'ori': {"opcode" : "001101", "r1" : 2, "r2": 1, "i" : 3},
    'lw' : {"opcode" : "100011", "r1" : 3, "r2": 1, "i" : 2},
    'sw' : {"opcode" : "101011", "r1" : 3, "r2": 1, "i" : 2},
}


R_TYPE = {
    'add': {"funct" : "100000", "r1" : 2, "r2": 3, "r3" : 1},
    'sub': {"funct" : "100010"},
    'and': {"funct" : "100100"},
    'or' : {"funct" : "100101"}
}


J_TYPE = {
    'j': {"opcode" : "000010"}
}


def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


dp0 = cur_file_dir() + "\\"


def check_comment(line):
    return line.startswith(';')


def get_comment(line):
    if check_comment(line):
        return line[1:].strip()


def parse(f):
    symbols = {}
    progs = []

    asm_type = get_comment(f.readline())
    if asm_type != "MIPS Lite":
        return

    for line in f:
        if check_comment(line):
            continue

        line = line.lower().strip()
        if line == "":
            continue

        label_groups = re.match(r'^(.+):(.*)$', line)
        if label_groups:
            symbols[label_groups.group(1)] = len(progs)
            line = label_groups.group(2).strip()
            if line is not None and line != "":
                progs.append(line)
        else:
            progs.append(line)

    return symbols, progs


def code(progs, symbols):
    for line in progs:
        binary_string = ""

        keys = [v for v in re.split('[\n, \(\)]', line.lower()) if v != '']
        for i, key in enumerate(keys):
            if key in symbols:
                keys[i] = symbols[key]
        
        print(keys)
        key = keys[0]
        if key in I_TYPE:
            opr = I_TYPE[key]
            r1  = REGISTER[keys[opr["r1"]]]
            r2  = REGISTER[keys[opr["r2"]]]
            num = int(keys[opr["i"]])
            binary_string = opr["opcode"] + '{:0>5b}'.format(r1) + '{:0>5b}'.format(r2) + '{:0>16b}'.format(num)

        elif key in R_TYPE:
            opr = R_TYPE[key]
            r1  = REGISTER[keys[opr["r1"]]]
            r2  = REGISTER[keys[opr["r2"]]]
            r3  = REGISTER[keys[opr["r3"]]]
            binary_string = '000000{:0>5b}'.format(r1) + '{:0>5b}'.format(r2) + '{:0>5b}00000'.format(r3) + opr["funct"]

        elif key in J_TYPE:
            opr = J_TYPE[key]
            binary_string = opr["opcode"] + '{:0>26b}'.format(int(keys[1]))

        print(binary_string)



for root, dirs, files in os.walk(dp0):
    for i, file in enumerate(files):
        if '.asm' in file and 'L.asm' not in file:
            splitext = os.path.splitext(file)
            file_path = os.path.join(root, file)
            print(file_path)

            f = open(file_path)
            symbols, progs = parse(f)
            f.close()

            code(progs, symbols)