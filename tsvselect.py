#!/bin/python
help_str = """Usage: tsvselect data.tsv rule1 rule2 ... > intersect.tsv
Rule format:
    [min,max];#_wanted;rpn,math,rule
Example rule:
    max;50;#5,#6,/
"""

import sys
import copy

def load_tsv(path):
    data = []
    with open(path) as fin:
        for line in fin:
            line = line.rstrip()
            if line:
                data.append(line.split('\t'))
    return data

def write_tsv(data, dest):
    for row in data:
        dest.write('{}\n'.format('\t'.join(row)))

def mul(a, b): return a*b
def add(a, b): return a+b
def sub(a, b): return a-b
def div(a, b): return a/b
def pow(a, b): return a**b
class RPNExpr:
    ops_bin = {
        '*' : mul,
        '+' : add,
        '-' : sub,
        '/' : div,
        '^' : pow}

    def __init__(self, expr):
        self.toks = expr.split(',')

    def __call__(self, row):
        stack = []
        for tok in self.toks:
            if tok in self.ops_bin:
                # operator
                n2 = stack.pop(-1)
                n1 = stack.pop(-1)
                stack.append(self.ops_bin[tok](n1, n2))
            elif tok[0] == '#':
                # column
                stack.append(float(row[int(tok[1:])-1]))
            else:
                # assume number
                stack.append(float(tok))

        return stack[-1]
                

def apply_rule(data, rule):
    reverse = None
    limit = None
    key = None

    r = rule.split(';')

    if 'min' in r[0]:
        reverse = False
    elif 'max' in r[0]:
        reverse = True
    else:
        raise RuntimeError('Invalid rule')

    if not r[1]:
        limit = None
    else:
        try:
            limit = int(r[1])
        except:
            raise RuntimeError('Invalid rule')

    key = RPNExpr(r[2])

    try:
        return sorted(data, key=key, reverse=reverse)[:limit]
    except:
        raise RuntimeError('Invalid rule')

def intersect(sets):
    res = []
    base = sets[0]
    for row in base:
        for set in sets:
            if row not in set:
                break
        else:
            res.append(row)
    return res
    
def main():
    # help message
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        global help_str
        sys.stderr.write(help_str)
        return 0

    # load data
    data = load_tsv(sys.argv[1])
    sets = []
    # process data
    for num, rule in enumerate(sys.argv[2:]):
        try:
            sets.append(apply_rule(data, rule))
        except Exception as ex:
            sys.stderr.write('On rule #{}:\n'.format(num+1))
            sys.stderr.write('{}\n'.format(str(ex)))
            return -1
    # output intersect
    write_tsv(intersect(sets), sys.stdout)
    return 0
            
if __name__ == '__main__':
    sys.exit(main())