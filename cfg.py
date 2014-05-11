from random import choice

class PCFGParser:
    def __init__(self, rules='data/weighted.rule'):
        self.grammar = self.__read_grammar(rules)

    def __read_grammar(self, f):
        """Given a file containing weighted rules, f, return a dictionary of
        those rules."""

        grammar = {}
        rules = open(f, 'r')
    
        for rule in rules:
            tmp = rule.split()
            lhs = tmp[0]
            rhs = ' '.join(tmp[1:-1])
            weight = float(tmp[-1])

            if lhs in grammar:
                grammar[lhs][rhs] = weight
            else:
                grammar[lhs] = {rhs: weight}

        rules.close()

        return grammar

    def __generate_each(self, cat_pair, depth):
        """Given a list of categories to combine (e.g. ['NP', 'VP']),
        generate a sentence, phrase or word for each category and return a list
        of tokens or None, if None is generated for any category."""
        
        (left, right) = [self.generate(cat, depth) for cat in cat_pair]
        if all((left, right)):
            return left+right
        else:
            return None

    def __producers(self, rhs, prob):
        """Given the rhs of a rule (e.g. "NP VP", "president"), rhs, and
        their joint probability (or 0 in the case of a terminal), prob,
        return all possible lhs's."""

        results = []
        for (lhs, d) in self.grammar.iteritems():
            for current_rhs in d:
                if current_rhs == rhs:
                    r = (lhs, prob + d[current_rhs])
                    results.append(r)

        # Handle unseen words
        if len(rhs.split()) == 1 and not results:
            for (lhs, d) in self.grammar.iteritems():
                if '<UNK>' in d:
                    r = (lhs, d['<UNK>'])
                    results.append(r)
            
        return results

    def __to_tree(self, table, pointer, sentence, j, i, k):
        """Trace back the pointer table recursively and return the parse tree."""

        if pointer[j][i]: #not empty
            rhs = []

            #rhs1
            nj1 = pointer[j][i][k][0][0]
            ni1 = pointer[j][i][k][0][1]
            nk1 = pointer[j][i][k][0][2]
            rhs.append(self.__to_tree(table, pointer, sentence, nj1, ni1, nk1))

            #rhs2
            nj2 = pointer[j][i][k][1][0]
            ni2 = pointer[j][i][k][1][1]
            nk2 = pointer[j][i][k][1][2]
            rhs.append(self.__to_tree(table, pointer, sentence, nj2, ni2, nk2))

        else: #empty
            rhs = [sentence[i-1]]

        tree = [table[j][i][k][0]]
        tree.extend(rhs)

        return tree

    def __print_table(self, table, sentence):
        """Print the dynamic programming table. Useful for debugging.
        The leftmost column is always empty."""

        print sentence
        for row in table:
            print row[1:]

    def generate(self, cat, depth=0):
        """Given a syntactic category (e.g. S, VP, NN), cat,
        return a randomly generated sentence, phrase or word of that category.
        The variable depth tracks the recrusion depth to avoid infinite
        recursion due to randomly chosen production rules."""

        if depth > 20:
            return None
        
        # Randomly choose the rhs rule excluding <UNK>
        rhs = choice([k for k in self.grammar[cat].keys() if k != '<UNK>']).split()

        if len(rhs) == 1: # rhs is a terminal node
            return rhs
        else: # rhs is a list of two non-terminal nodes
            return self.__generate_each(rhs, depth+1)

    def parse(self, sentence):
        """The CYK parser. Given a list of words, sentence, return its parse
        tree if the sentence is in the grammar or None otherwise."""

        # Create the CYK table
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

        # Fill the diagonal of the CYK table with parts-of-speech of the words
        for k in range(1, length+1):
            table[k-1][k].extend(self.__producers(sentence[k-1], 0))

        # Fill the CYK table
        for i in range (1, length+1):
            for j in range(i-2, -1, -1):
                for k in range(j+1, i):
                    # Test all combinations of rhslist
                    for l in range(len(table[j][k])):
                        for m in range(len(table[k][i])):
                            prob = table[j][k][l][1] + table[k][i][m][1]
                            rhs = table[j][k][l][0]+' '+table[k][i][m][0]
                            lhs = self.__producers(rhs, prob)
                            if lhs:
                                table[j][i].extend(lhs)
                                pointer[j][i].extend([[[j, k, l], [k, i, m]]]*len(lhs))

        # self.__print_table(table) # Uncomment to print CYK table

        # Generate a parse tree and return it if the parse exists or
        # return None otherwise
        if table[0][length]:
            max_prob = table[0][length][0][1]
            max_idx = 0

            for i in range(1, len(table[0][length])):
                prob = table[0][length][i][1]
                if prob > max_prob:
                    max_prob = prob
                    max_idx = i
    
            return self.__to_tree(table, pointer, sentence, 0, length, max_idx)

        else:
            return None

    def to_str(self, tree):
        """Return the formatted string of a parse tree."""

        # Stringify any lists inside tree
        for i in range(len(tree)):
            if isinstance(tree[i], list):
                tree[i] = self.to_str(tree[i])

        # Turn the list of strings, tree, into a formatted string
        return "({})".format(' '.join(tree))
