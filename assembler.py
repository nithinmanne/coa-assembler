'''Assembler for the CPU designed in COA Lab'''
import argparse
import re
import json

PATTERN = r'\A(?:(?P<label>\w+) *: *)?(?:(?P<opc>\w+)(?: +(?P<arg>\w+))?)?\Z'

def mkargparser():
    '''Argument Parse function'''
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Assembly file to be converted')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    parsed = runcode(args.file, args.verbose)
    print(*parsed)

def runcode(file, verbose):
    '''Runs the assembler code'''
    with open('config.json') as filep:
        config = json.load(filep)
    with open(file) as filep:
        file = filep.read().split('\n')
    file = list(map(lambda x: x.strip(), file))
    match = re.compile(PATTERN)
    future, parsed = [], []
    labels = {}
    curline = 0
    for i, j in enumerate(file):
        reres = match.search(j)
        if reres is None:
            raise ValueError("Error at Line {}. Unknown Format\r\n{}".format(i+1, j))
        reresgd = reres.groupdict()
        if reresgd['label'] is not None:
            if reresgd['label'] in labels:
                raise ValueError("Duplicate Labels at Line {}\r\n{}".format(i+1, j))
            labels[reresgd['label']] = curline
        if reresgd['opc'] is None:
            continue
        curline += 1
        if reresgd['opc'] not in config:
            raise ValueError("Unknown function {} at Line {}\r\n{}".format(
                reresgd['arg'], i+1, j))
        cmd = config[reresgd['opc']]
        if 'x' in cmd:
            if reresgd['arg'] is None:
                raise ValueError("Unknown function {} at Line {}\r\n{}".format(
                    reresgd['arg'], i+1, j))
            elif reresgd['arg'] not in labels:
                future.append((len(parsed), reresgd, j))
            else:
                val = labels[reresgd['arg']] - curline
                cmd = cmd.replace('x'*cmd.count('x'), bindigits(val, cmd.count('x')))
        elif 'y' in cmd:
            try:
                val = int(reresgd['arg'])
            except:
                raise ValueError("Unknown function {} at Line {}\r\n{}".format(
                    reresgd['arg'], i+1, j))
            cmd = cmd.replace('y'*cmd.count('y'), bindigits(val, cmd.count('y')))
        elif 'r' in cmd:
            val = int(reresgd['arg'][1:])
            cmd = cmd.replace('r'*cmd.count('r'), bindigits(val, cmd.count('r')))
        parsed.append(cmd)
    for i, reresgd, j in future:
        if reresgd['arg'] not in labels:
            raise ValueError("Unknown label at Line {}\r\n{}".format(i+1, j))
        else:
            val = labels[reresgd['arg']] - curline
            parsed[i] = parsed[i].replace('x'*parsed[i].count('x'), bindigits(val, parsed[i].count('x')))
    if verbose:
        print('Number of actual Lines:', curline)
        print('Labels:', labels)
    return parsed


def parse(file, actlines, tags, verbose):
    '''Parse all functions and convert to bits'''
    parsed = []
    with open('config.json') as filep:
        config = json.load(filep)
    for i, _ in enumerate(file):
        if i != len(file)-1 and actlines[i] == actlines[i+1]:
            continue
        if verbose:
            print(file[i], actlines[i])
        remlbl = file[i].strip().split(':')
        if len(remlbl) > 2:
            raise ValueError("Error at Line {}\r\nMultiple ':'".format(i+1))
        com = remlbl[-1].strip().split()
        if len(com) == 1:
            com = com[0]
        else:
            com, par = com
        if com not in config:
            raise ValueError("Error at Line {}\r\nUnknown Command".format(i+1))
        cmd = config[com]
        if 'x' in cmd:
            if par not in tags:
                raise ValueError("Error at Line {}\r\nUnknown Label".format(i+1))
            val = tags[par] - actlines[i] - 1
            rtag = bindigits(val, 12)
            cmd = cmd[:cmd.find('x')] + rtag
        elif 'y' in cmd:
            val = int(par)
            val = bindigits(val, 12)
            cmd = cmd[:cmd.find('y')] + val
        elif 'r' in cmd:
            val = int(par[1:])
            val = bindigits(val, 3)
            cmd = cmd[:cmd.find('r')] + val
            cmd += '0'*(16-len(cmd))
        parsed.append(cmd)
    return parsed

def bindigits(num, bits):
    '''Decimal to Binary'''
    if bits <= 0:
        return ''
    binf = bin(num & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(binf)

if __name__ == '__main__':
    mkargparser()
