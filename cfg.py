import sys
from random import choice

def getgrammar(file):
    """Given a file containing weighted rules, return a dictionary of
    weighted rules"""
    grammar = {}
    rules = open(file, 'r').readlines()
    
    for rule in rules:
        tmp = rule.split()
        lhs = tmp[0]
        rhs = ' '.join(tmp[1:-1])
        weight = float(tmp[-1])

        if lhs in grammar:
            if rhs in grammar[lhs]: print 'Weird!'
            else: grammar[lhs][rhs] = weight
        else:
            grammar[lhs] = {rhs: weight}

    return grammar

def generate(phrase):
    "Generate a random sentence or phrase"
    if isinstance(phrase, list): 
        return mappend(generate, phrase)
    elif phrase in grammar:
        return generate(choice(grammar[phrase]))
    else: return [phrase]
    
def generate_tree(phrase):
    """Generate a random sentence or phrase,
     with a complete parse tree."""
    if isinstance(phrase, list): 
        return map(generate_tree, phrase)
    elif phrase in grammar:
        return [phrase] + generate_tree(choice(grammar[phrase]))
    else: return [phrase]

def mappend(fn, list):
    "Append the results of calling fn on each element of list."
    return reduce(lambda x,y: x+y, map(fn, list))

def producers(constprob):
    """Argument is a list containing the rhs of some rule; return all possible
    lhs's"""
    constituent = constprob[0]
    prob1 = constprob[1]

    results = []
    for (lhs, rhsdict) in grammar.items():
	for rhs in rhsdict:
            prob2 = rhsdict[rhs]
	    if rhs == constituent:
                #print lhs, prob1+prob2
                lhsprob = (lhs, prob1+prob2)
		results.append(lhsprob)

    #Handle unseen words and unknown non-terminal rules
    if len(constituent.split()) == 1 and not results:
        for (lhs, rhsdict) in grammar.items():
            if '<UNK>' in rhsdict:
                prob2 = rhsdict['<UNK>']
                lhsprob = (lhs, prob1+prob2)
                results.append(lhsprob)
            
    return results

def printtable(table, wordlist):
    "Print the dynamic programming table.  The leftmost column is always empty."
    print "    ", wordlist
    for row in table:
	print row

def parsetree(table, pointer, wordlist, j, i, k):
    if pointer[j][i]: #not empty
        rhs = []

        #rhs1
        nj1 = pointer[j][i][k][0][0]
        ni1 = pointer[j][i][k][0][1]
        nk1 = pointer[j][i][k][0][2]
        rhs.append(parsetree(table, pointer, wordlist, nj1, ni1, nk1))

        #rhs2
        nj2 = pointer[j][i][k][1][0]
        ni2 = pointer[j][i][k][1][1]
        nk2 = pointer[j][i][k][1][2]
        rhs.append(parsetree(table, pointer, wordlist, nj2, ni2, nk2))

    else: #empty
        rhs = [wordlist[i-1]]

    tree = [table[j][i][k][0]]
    tree.extend(rhs)
    return tree

def parse(sentence):
    """The CYK parser.  Return True if sentence is in the grammar;
    False otherwise"""
    
    # Create the table; index j for rows, i for columns
    length = len(sentence)
    table = [None] * (length)
    for j in range(length):
	table[j] = [None] * (length+1)
	for i in range(length+1):
	    table[j][i] = []

    # Create a pointer table
    pointer = [None] * (length)
    for j in range(length):
        pointer[j] = [None] * (length+1)
        for i in range(length+1):
            pointer[j][i] = []

    # Fill the diagonal of the table with the parts-of-speech of the words
    for k in range(1,length+1):
	table[k-1][k].extend(producers((sentence[k-1], 0)))
        #print table[k-1][k]
        #pointer[]
        #print table[k-1][k]

    # Fill CYK table
    for i in range (1, length+1):
        for j in range(i-2, -1, -1):
            for k in range(j+1, i):
                # Test all combinations of rhslist
                for l in range(len(table[j][k])):
                    for m in range(len(table[k][i])):
                        rhslist = (table[j][k][l][0]+' '+table[k][i][m][0], table[j][k][l][1]+table[k][i][m][1])
                        lhs = producers(rhslist)
                        #print lhs
                        if lhs:
                            table[j][i].extend(lhs)
                            pointer[j][i].extend([[[j, k, l], [k, i, m]]]*len(lhs))
        #if not table[j][i]: print 'Cell', j, i, 'is empty'
                            

    # Print the table
    #printtable(table, sentence)
    #printtable(pointer, sentence)

    # Print tree
    #print table[0][length]
    if table[0][length]:
        maxprob = table[0][length][0][1]
        maxidx = 0

        for i in range(1, len(table[0][length])):
            prob = table[0][length][i][1]
            if prob > maxprob:
                maxprob = prob
                maxidx = i
    
        return parsetree(table, pointer, sentence, 0, length, maxidx)
    else: return None

def printlanguage ():
    file = open('languageoutput.txt', 'w')

    "Randomly generate many sentences, saving and printing the unique ones"
    language = {}
    size = 0
    for i in range(10000):
	sentencestr = ' '.join(generate('S'))
	language[sentencestr] = 1
	if len(language) > size:
	    size = len(language)
	    #print '+',
	else:
	    #print '.',
	    sys.stdout.flush()

    for s in language.keys():
	print s
        file.write(s + '\n')
    print size
    file.write(str(size))
    #print generate_tree('S')
    #print generate('S')

    file.close()

def printsentence ():
    print ' '.join(generate('S'))
        
def printtest():
    sentences = open('data/tst.raw', 'r').readlines()
    fout = open('data/tst.parse.my', 'w')
    out = ''
    count = 1
    for sent in sentences:
        tree = parse(sent.split())
        if tree is not None:
            treestr = str(tree).replace('\'','').replace(',', '')
            treestr = treestr.replace('[', '(').replace(']', ')')
            out += treestr + '\n'
            print 'successfully parsed', count, 'out of 96 test sentences'
            count += 1
        else: print 'parsing unsuccessful'

    fout.write(out)

grammar = getgrammar('data/weighted.rule')
printtest()

#parse('Not much of a trip'.split())
#parse('These people had flesh injuries'.split())
#print producers(['Det', 'N'])
#printsentence()
#sent1 = parse('the man with the pickles hit the red ball'.split())
#sent2 = parse('the dog with a party thinks that a ball sees the light'.split())
#sent3 = parse('the school with the pickles hits the red ball'.split())
#sent4 = parse('the ball that pickles the dogs liked skinny goggles with the red light'.split())
#sent5 = parse('ball pickles the skinny ball'.split())
#print str(sent1) + ' ' + str(sent2) + ' ' + str(sent3) + ' ' + str(sent4) + ' ' +str(sent5)
#printlanguage()
