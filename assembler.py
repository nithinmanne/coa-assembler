'''Assembler for the CPU designed in COA Lab'''
import argparse
import json

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
    with open(file) as filep:
        file = filep.read().split('\n')
    file = list(map(lambda x: x.strip(), file))
    file.append('finalendhopeyoudontusethisstupidlabel:b finalendhopeyoudontusethisstupidlabel')
    actlines = getactline(file)
    if verbose:
        print('Number of actual Lines: {}'.format(actlines[-1]))
    tags = getlabel(file, actlines)
    if verbose:
        print('Detected Labels: ', tags)
    parsed = parse(file, actlines, tags)
    return parsed

def getactline(file):
    '''Get actual PC code lines for each line'''
    actlines = []
    count = 0
    for j in file:
        if ':' in j:
            actlines.append(count)
            if len(j.split(':')) == 1:
                continue
        else:
            actlines.append(count)
            if j == '':
                continue
        count += 1
    return actlines

def getlabel(file, actlines):
    '''Gets labels from code'''
    labels = {}
    for i, j in enumerate(file):
        if ':' not in j:
            continue
        label = j.split(':')
        if label[0].strip() in labels:
            raise ValueError("Duplicate Labels")
        labels[label[0].strip()] = actlines[i]
    return labels

def parse(file, actlines, tags):
    '''Parse all functions and convert to bits'''
    parsed = []
    with open('config.json') as filep:
        config = json.load(filep)
    for i, _ in enumerate(file):
        if i != len(file)-1 and actlines[i] == actlines[i+1]:
            continue
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
            rtag = tags[par] - actlines[i] - 1
            rtag = bindigits(rtag, 12)
            cmd = cmd[:cmd.find('x')] + rtag
        elif 'y' in cmd:
            val = int(par)
            val = bindigits(val, 12)
            cmd = cmd[:cmd.find('y')] + val
        elif 'r' in cmd:
            rval = int(par[1:])
            rval = bindigits(rval, 3)
            cmd = cmd[:cmd.find('r')] + rval
            cmd += '0'*(16-len(cmd))
        parsed.append(cmd)
    return parsed

def bindigits(num, bits):
    '''Decimal to Binary'''
    binf = bin(num & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(binf)

if __name__ == '__main__':
    mkargparser()
