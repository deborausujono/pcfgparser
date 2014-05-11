#!/usr/bin/python
# -------------------------------------------------------
# author     : Jinho D. Choi
# modified by: Debora Sujono
# last update: 5/9/2014
# -------------------------------------------------------
import sys
import re
import os
import operator
from lib.treebank import *
from math import log

# Reads a parse file, extract phrase structure rules, and prints the rules to an output file
def printRules(parseFile, ruleFile):
    reader = TBReader()
    reader.open(parseFile)
    fout = open(ruleFile, 'w')

    for tree in reader:
        for rule in tree.getPhraseRules():
            fout.write(' '.join(rule)+'\n')

# Reads phrase structure rules from a rule file and returns a dictionary containing the rules
# The dictionary takes a non-terminal as a key and a sub-dictionary as a value.
# The sub-dictionary takes the righthand side of the non-terminal as a key, and its count as a value
# e.g., the returned map = {'S': {'NP VP': 1}, 'VP': {'VP NP': 2}}
def getRules(ruleFile):
    fin   = open(ruleFile)
    rules = dict()
    
    for rule in fin:
        tmp = rule.split()
        lhs = tmp[0]
        rhs = ' '.join(tmp[1:])
        
        if lhs in rules:
            r = rules[lhs]
            if rhs in r: r[rhs] += 1
            else       : r[rhs]  = 1
        else:
            rules[lhs] = {rhs: 1}

    # Turns the count of words that occur only once into <UNK> count
    # to handle unseen terminals and delete non-terminal rules that occur
    # only once to improve rule accuracy
    for lhs in rules.keys():
        r = rules[lhs]
        for rhs in r.keys():
            if r[rhs] == 1:
                del r[rhs]
                if len(rhs.split()) == 1:
                    if '<UNK>' in r: r['<UNK>'] += 1
                    else: r['<UNK>'] = 1
    
    return rules
    
# Converts counts in the rules dictionary into probabilities
def toProbabilities(rules):
    for lhs in rules:
        r = rules[lhs]
        t = 0
        for rhs in r:
            t += r[rhs]
        
        for rhs in r:
            r[rhs] = log(float(r[rhs]) / t)

def printDict(rules, weightFile):
    fout = open(weightFile, 'w')

    for lhs in rules:
        r = rules[lhs]
        for rhs in r:
            print '%4s -> %16s %8.6f' % (lhs, rhs, r[rhs])
            fout.write(lhs + ' ' + rhs + ' ' + str(r[rhs]) + '\n')

def main():
    PARSE_FILE = 'data/trn.parse'
    RULE_FILE  = 'data/unweighted.rule'
    WEIGHT_FILE = 'data/weighted.rule'

    printRules(PARSE_FILE, RULE_FILE)
    rules = getRules(RULE_FILE)
    toProbabilities(rules)
    printDict(rules, WEIGHT_FILE)

if __name__ == '__main__':
    main()
