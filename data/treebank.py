# -------------------------------------------------------
# Treebank APIs
# author     : Jinho D. Choi
# last update: 09/08/2011
# -------------------------------------------------------
import re
from lang_en import *

PTAG_TOP  = 'TOP'
PTAG_NONE = '-NONE-'

LANG_EN = 'en'

##### BEGIN: Class TBNode ###########################################
# MEMBER INSTANCES
# pTag   - pos/phrase tag : String
# fTags  - set of function tags : Set of String
# cIndex - co-index  (default=-1)
# gIndex - gap-index (default=-1)
# form   - word-form : String
#
# parent     - parent of this node : TBNode
# children   - children of this node : List of TBNode
# antecedent - antecedent of this node : TBNode
#
# pbLoc      - [terminalId, height] (default=None) : List of Integer
# siblingId  - index of this node among its siblings : Integer
# terminalId - index of this node among all terminals : Integer
class TBNode:
    RE_DELIM = re.compile('([-=])')

    # tags (e.g., 'NP-LOC-PRD-1=2') : String
    # parent : TBNode
    def __init__(self, tags, parent=None):
        self.setTags(tags)
        self.form       = None
        self.pbLoc      = None
        self.siblingId  = -1
        self.terminalId = -1
        self.tokenId    = -1
        self.parent     = parent
        self.children   = list()
        self.antecedent = None

########################### TBNode:getters ###########################

    # returns all tags (e.g., 'NP-LOC-PRD-1=2') : String
    def getTags(self):
        ls = [self.pTag]
        
        for fTag in self.fTags:
            ls.append('-')
            ls.append(fTag)
        
        if self.cIndex != -1:
            ls.append('-')
            ls.append(str(self.cIndex))
        
        if self.gIndex != -1:
            ls.append('=')
            ls.append(str(self.gIndex))
        
        return ''.join(ls)
    
    # return the PropBank location of this node : String
    def getPBLoc(self):
        return ':'.join(map(str, self.pbLoc))
    
    # kwargs - see descriptions in 'isTag()'.
    # returns the first child matching 'kwargs' : TBNode
    def getFirstChild(self, **kwargs):
        for child in self.children:
            if child.isTag(**kwargs):
                return child
        
        return None
    
    # kwargs - see descriptions in 'isTag()'.
    # returns the last child matching 'kwargs' : TBNode
    def getLastChild(self, **kwargs):
        for child in reversed(self.children):
            if child.isTag(**kwargs):
                return child
        
        return None

    # kwargs - see descriptions in 'isTag()'.
    # returns the left-nearest sibling matching 'kwargs' : TBNode
    def getPrevSibling(self, **kwargs):
        if not self.parent: return None
        siblings = self.parent.children

        for i in range(self.siblingId-1,-1,-1):
            prev = siblings[i]
            if prev.isTag(**kwargs):
                return prev
        
        return None
        
    # kwargs - see descriptions in 'isTag()'.
    # returns the right-nearest sibling matching 'kwargs' : TBNode
    def getNextSibling(self, **kwargs):
        if not self.parent: return None
        siblings = self.parent.children
        
        for i in range(self.siblingId+1,len(siblings)):
            next = siblings[i]
            if next.isTag(**kwargs):
                return next
        
        return None

    # kwargs - see descriptions in 'isTag()'.
    # returns the nearest ancestor matching 'kwargs' : TBNode
    def getNearestAncestor(self, **kwargs):
        node = self.parent
        while node:
            if node.isTag(**kwargs): return node
            node = node.parent
        
        return None

    # ecForm - regular expression of an empty category form (e.g., '\*ICH\*.*')
    # returns the empty category in the subtree of this node : TBNode
    def getIncludedEmptyCategory(self, regex):
		return self.__getIncludedEmptyCategory(regex, self)
	
	# called by 'getIncludedEmptyCategory()'.
    def __getIncludedEmptyCategory(self, regex, curr):
        if curr.isEmptyCategory() and re.match(regex, curr.form):
            return curr
		
        for child in curr.children:
            ec = self.__getIncludedEmptyCategory(regex, child)
            if ec: return ec
		
        return None

    # returns sub-terminals of this node : List of TBNode
    def getSubTerminals(self):
        ls = list()
        self.__getSubTerminals(self, ls)
        
        return ls
    
    # called by 'getSubTermninals'
    def __getSubTerminals(self, curr, ls):
        if not curr.children:
            ls.append(curr)
        else:
            for child in curr.children:
                self.__getSubTerminals(child, ls)

    # returns a set of sub-terminal IDs : Set of Integer
    def getSubTerminalIdSet(self):
        s = set()
        
        for node in self.getSubTerminals():
        	s.add(node.terminalId)
        
        return s

    # PRE: English
    # returns the complementizer belongs to this node : TBNode
    def getComplementizer(self):
        if not self.pTag.startswith('WH'):
            return None

        whNode = self
        while True:
            tmp = whNode.getFirstChild(pRex='WH.*')
            if tmp: whNode = tmp
            else  : break

        terminals = whNode.getSubTerminals()

        for node in terminals:
            if node.isComplementizer():
                return node
                
        for node in terminals:
            if RE_COMP_FORM.match(node.form.lower()):
                return node
        
        return None

    # PRE: English
    # returns the lowest coindexed wh-node (including self) : TBNode
    def getCoIndexedWHNode(self):
        curr = self.parent
		
        while curr:
            if not curr.pTag.startswith('WH'): break
            if curr.cIndex != -1: return curr
        		
            curr = curr.parent
		
        return None

    # PRE: English
    # returns the subject of this node : TBNode
    def getSubject(self):
        pred = self
        while pred.parent.pTag == PTAG_VP:
            pred = pred.parent
        
        return pred.getPrevSibling(pTag=PTAG_NP, fTag=FTAG_SBJ)

    # PRE: English
    # PRE: this node is a verb predicate (e.g., 'say')
    # returns the nearest PRN node if this node is a True if this node is in PRN and has an external argument : Boolean
    def getPredPRN(self):
        s = self.getNearestAncestor(pRex='^S.*')
        
        if s and s.parent.pTag == PTAG_PRN:
            next = self.getNextSibling(pRex='^(S|SBAR)$')
            if next:
                ec = next.__getEmptySentence()
                if ec: return (s.parent, ec)
            
        return None

    # called by 'getPredPRN()'.
    def __getEmptySentence(self):
        if self.pTag == PTAG_SBAR:
            if len(self.children) == 2 and \
               self.children[0].pTag == PTAG_NONE and self.children[0].form == '0' and \
               self.children[1].isEmptyCategory(recursive=True):
                return self.children[1].getIncludedEmptyCategory('^\*(\?|T)\*')
        elif self.pTag == PTAG_S:
            if self.isEmptyCategory(recursive=True):
                return self.children[0].getIncludedEmptyCategory('^\*(\?|T)\*')
        
        return None

    # PRE: English
    # returns the empty category of passive construction : TBNode
    def getPassiveEmptyCategory(self):
        if self.parent and self.parent.pTag == PTAG_VP and \
           self.siblingId > 0 and self.parent.children[self.siblingId-1].pTag.startswith('VB') and \
           self.pTag == PTAG_NP and not self.fTags and \
           self.isEmptyCategory(recursive=True):
            return self.getIncludedEmptyCategory('^(\*|\*-\\d)$')

########################### TBNode:setters ###########################

    # tags : String (e.g., 'NP-LOC-PRD-1=2')
    def setTags(self, tags):
        if tags[0] != '-': ls = self.RE_DELIM.split(tags)
        else             : ls = [tags]
        
        self.pTag   = ls[0]
        self.fTags  = set()
        self.cIndex = -1
        self.gIndex = -1
        
        for i in range(2, len(ls), 2):
            t = ls[i-1]
            v = ls[i]
            
            if v.isdigit():
                if t == '-': self.cIndex = int(v)
                else       : self.gIndex = int(v)
            else:
                self.fTags.add(v)
    
    # child : TBNode
    def addChild(self, child):
        child.siblingId = len(self.children)
        self.children.append(child)

    # terminalId, height : Integer
    def setPBLoc(self, terminalId, height):
        self.pbLoc = [terminalId, height]
 
########################### TBNode:boolean ###########################

    # kwargs['pRex'] - regular expression of pTag : String
    # kwargs['pTag'] - phrase/pos tag : String
    # kwargs['fTag'] - function tag : String
    # returns True if this node matches all 'kwargs' : Boolean
    def isTag(self, **kwargs):
        if ('pRex' not in kwargs or re.match(kwargs['pRex'], self.pTag)) and \
           ('pTag' not in kwargs or kwargs['pTag'] == self.pTag) and \
           ('fTag' not in kwargs or kwargs['fTag'] in self.fTags):
            return True
        else:
            return False

    # returns true if this node contains child matching 'kwargs' : Boolean
    def contains(self, **kwargs):
        for child in self.children:
            if child.isTag(**kwargs):
                return True
        
        return False

    # recursive - check if this node contains only empty category recursively : Boolean
    # returns True if this node is an empty category : Boolean
    def isEmptyCategory(self, recursive=False):
        if recursive:
            return self.__isEmptyCategoryRec(self)
        else:
            return self.pTag == PTAG_NONE

    # called by 'isEmptyCategory(True)'
    def __isEmptyCategoryRec(self, curr):
        if not curr.children:
            return curr.isEmptyCategory()
        
        if len(curr.children) > 1:
            return False
        
        return self.__isEmptyCategoryRec(curr.children[0])

    # pTag : String
    # ancestor : TBNode
    # returns True if this node is a descendent of 'pTag' or 'ancestor' : Boolean
    def isDescendentOf(self, pTag, ancestor=None):
        node = self
        while node.parent:
            node = node.parent
            if node.pTag == pTag or node == ancestor:
                return True
        
        return False
    
    # PRE: English
	# returns True if this node is a complementizer : Boolean
    def isComplementizer(self):
    	if not self.form: return False
    	return RE_COMP_POS.match(self.pTag) or (self.pTag == PTAG_NONE and self.form == '0')

########################### TBNode:helpers ###########################

    # returns forms of subtree : String
    def toForms(self, includeEC=True):
        ls = list()
        self.__toForms(includeEC, self, ls)

        return ' '.join(ls)

    # called by 'toForms'.
    def __toForms(self, includeEC, curr, ls):
        if curr.form and (includeEC or not curr.isEmptyCategory()):
            ls.append(curr.form)

        for child in curr.children:
            self.__toForms(includeEC, child, ls)

    # returns this node in the Penn Treebank format : String
    def toParseTree(self, numbered=False):
        lTree = list()
        self.__toParseTree(self, lTree, '', numbered)

        return '\n'.join(lTree)
        
    # called by 'toParseTree'.
    def __toParseTree(self, curr, lTree, sTags, numbered):
        if not curr.children:
            tag = sTags + '('+curr.getTags()+' '+curr.form+')'
            if numbered: tag = '%4d: ' % (len(lTree)) + tag
            lTree.append(tag)
        else:
            sTags += '('+curr.getTags()+' '
            sNull  = re.sub('.', ' ', sTags)
            
            self.__toParseTree(curr.children[0], lTree, sTags, numbered)
            
            for child in curr.children[1:]:
                self.__toParseTree(child, lTree, sNull, numbered)
            
            lTree[-1] += ')'

##### BEGIN: Class TBTree ############################################
# MEMBER INSTANCES
# self.nd_root     - root node (TOP) : TBNode
# self.ls_terminal - list of terminal nodes : List of TBNode
class TBTree:
    RE_NORM = re.compile('\\*(ICH|RNR|PPA)\\*')
    
    # root : TBNode
    def __init__(self, root):
        self.nd_root     = root
        self.ls_terminal = list()
        self.dc_token    = dict()
        
########################### TBTree:getters ###########################

    def getNonTerminalTags(self):
        s = set()
        self.getNonTerminalTagsAux(self.nd_root, s)
        s.remove('TOP')
        return s
        
    def getNonTerminalTagsAux(self, node, s):
        children = node.children
        
        if children:
            s.add(node.pTag)
            
            for child in children:
                self.getNonTerminalTagsAux(child, s)

    def getPhraseRules(self):
        ls = list()
        self.getPhraseRulesAux(self.nd_root, ls)
        return ls
        
    def getPhraseRulesAux(self, node, ls):
        l = list()
        l.append(node.pTag)

        children = node.children
        
        if children:
            for child in children:
                l.append(child.pTag)
                self.getPhraseRulesAux(child, ls)
        else:
            l.append(node.form)

        if node.pTag != 'TOP': ls.append(l)

    def getTerminalTags(self):
        s = set()
        
        for node in self.ls_terminal:
            s.add(node.pTag)
        
        return s

    # beginId, endId - terminal IDs (both inclusive) : String
    # returns the node whose span is 'beginId - endId' : TBNode
    def getNodeBySpan(self, beginId, endId):
        bNode = self.ls_terminal[beginId]

        while bNode:
            sId = bNode.getSubTerminalIdSet()
            m   = max(sId)
            if  m == endId: return bNode
            elif m > endId: break
            
            bNode = bNode.parent
        
        return None

    # EXPERIMENTAL
    # forms : String
    # returns the PropBank location covering 'forms' : String
    def getPBLoc(self, terminalId, forms):
        node = self.ls_terminal[terminalId]
        size = len(forms)
         
        while True:
            s = node.toForms()
            if s == forms   : return node.getPBLoc()
            if len(s) > size: break
            if node.parent  : node = node.parent
            else            : break

        return None

    # terminalId, height : Integer
    # returns the node in 'terminalId:height' : TBNode
    def getNode(self, terminalId, height=0):
        node = self.ls_terminal[terminalId]
        for i in range(height):
            node = node.parent
        
        return node

    # tokenId : Integer
    # returns the 'tokenId'th token : TBNode
    def getToken(self, tokenId):
        return self.dc_token[tokenId]

    # coIndex : Integer
    # returns the antecedent of 'coIndex' : TBNode
    def getAntecedent(self, coIndex):
        return self.__getAntecedent(coIndex, self.nd_root)
    
    # called by 'getAntecendet'
    def __getAntecedent(self, coIndex, curr):
        if curr.cIndex == coIndex:
            return curr
        
        for child in curr.children:
            ante = self.__getAntecedent(coIndex, child)
            if ante: return ante
        
        return None

    # returns a dictionary of co-index and list of corresponding nodes : Dictionary
    def getCoIndexDict(self):
        d = dict()
        self.__getCoIndexDict(self.nd_root, d)
        
        return d
    
    # called by 'getCoIndexDict'
    def __getCoIndexDict(self, curr, d):
        if not curr.children: return
        coIndex = curr.cIndex
        
        if coIndex != -1:
            if coIndex in d:
                l = d[coIndex]
            else:
                l = list()
                d[coIndex] = l
            
            l.append(curr)
        
        for child in curr.children:
            self.__getCoIndexDict(child, d)

    # terminalId : Integer
    # delim : String
    # returns all previous token forms (including self) without space : String
    def getPrevTokenForms(self, terminalId, delim=''):
        node = self.getNode(terminalId)
        l    = list()
        
        for i in range(node.tokenId+1):
            l.append(self.dc_token[i].form)
        
        return delim.join(l)
    
    # prevTokenForms - returned by getPrevTokenForms(delim) : String
    # delim : String
    # return the token of 'prevForms' : Token
    def getTokenByPrevForms(self, prevTokenForms, delim=''):
        l = list()
        
        for i in range(len(self.dc_token)):
            token = self.dc_token[i]
            l.append(token.form)
            s = delim.join(l)

            if s == prevTokenForms:
                return token
            elif len(s) > len(prevTokenForms):
                break
        
        return None

    def getPrevTerminalForms(self, terminalId, delim=''):
        l = list()
        
        for i in range(terminalId+1):
            node = self.ls_terminal[i]

            if node.isEmptyCategory(): l.append('*NULL*')
            else                     : l.append(node.form)
        
        return delim.join(l)
    
    def getTerminalByPrevForms(self, prevTerminalForms, delim=''):
        l = list()
        
        for i in range(len(self.ls_terminal)):
            node = self.ls_terminal[i]
            if node.isEmptyCategory(): l.append('*NULL*')
            else                     : l.append(node.form)
            s = delim.join(l)
        
            if s == prevTerminalForms:
                return self.ls_terminal[i]
            elif len(s) > len(prevTerminalForms):
                break
        
        return None
            
########################### TBTree:setters ###########################

    # node : TBNode
    def addTerminal(self, node):
        self.ls_terminal.append(node)
    
    # node : TBNode
    def addToken(self, tokenId, node):
        self.dc_token[tokenId] = node
    
    # initializes antecedents of all empty categories.
    def setAntecedents(self):
        for node in self.ls_terminal:
            if not node.isEmptyCategory(): continue
            coIndex = node.form[node.form.rfind('-')+1:]
            if coIndex.isdigit():
	            node.antecedent = self.getAntecedent(int(coIndex))

    # assigns PropBank locations to all nodes.
    def setPBLocs(self):
        for node in self.ls_terminal:
            terminalId = node.terminalId
            height     = 0
            node.setPBLoc(terminalId, height)
            
            while node.parent and not node.parent.pbLoc:
                node = node.parent
                height += 1
                node.setPBLoc(terminalId, height)

    # normalizes all co-indices and gap-indices
    def normalizeIndices(self):
        dIndex = self.getCoIndexDict()
        if not dIndex: return
        
        dGap = dict()
        keys = dIndex.keys()
        keys.sort()
        coIndex = 1

        for key in keys:
            l = dIndex[key]
            l.reverse()
            isAnteFound = False
            
            for i,node in enumerate(l):
                if node.isEmptyCategory(True):
                    ec = self.ls_terminal[node.pbLoc[0]]
                    
                    if i == 0 or isAnteFound or self.RE_NORM.match(ec.form):
                        node.cIndex = -1
                    else:
                        node.cIndex = coIndex
                        coIndex += 1
                        
                    if isAnteFound or i < len(l) - 1:
                        ec.form += '-'+str(coIndex)
                elif isAnteFound:
                    print 'Error: too many antecedents of co-index', key
                    node.cIndex = -1
                else:
                    dGap[key]   = coIndex
                    node.cIndex = coIndex
                    isAnteFound = True
            
            coIndex += 1
        
        self.__remapGapIndices(dGap, coIndex)

    # called by 'normalizeIndices'
    def __remapGapIndices(self, dGap, lastIndex):
        self.__remapGapIndicesAux(dGap, [lastIndex], self.nd_root)
    
    # called by '__remapGapIndices()'.
    def __remapGapIndicesAux(self, dGap, lastIndex, curr):
        gapIndex = curr.gIndex
        
        if gapIndex in dGap:
            curr.gIndex = dGap[gapIndex]
        elif curr.gIndex != -1:
            dGap[gapIndex] = lastIndex[0]
            curr.gIndex    = lastIndex[0]
            lastIndex[0] += 1
        
        for child in curr.children:
            self.__remapGapIndicesAux(dGap, lastIndex, child)

    # PRE: English
    # initializes antecedents of all complementizers.
    def setWHAntecedents(self):
        self.__setWHAntecedents(self.nd_root)

    # called by 'setWHAntecedents()'.
    def __setWHAntecedents(self, curr):
        if RE_COMP_ANTE.match(curr.pTag):
            comp = curr.getComplementizer()
            sbar = self.__getHighestSBAR(curr)

            if comp and sbar:
                p = sbar.parent
                if not p: return
                
                if p.pTag == PTAG_NP:
                    ante = sbar.getPrevSibling(pTag=PTAG_NP)
                    if ante: comp.antecedent = ante
                elif p.pTag == PTAG_WHNP:
                    ante = sbar.getPrevSibling(pTag=PTAG_WHNP)
                    if ante: comp.antecedent = ante
                elif p.pTag == PTAG_VP:
                    ante = p.getFirstChild(fTag=FTAG_PRD)
                    if ante and (ante.pTag == PTAG_NP or (curr.pTag == PTAG_WHPP and ante.pTag == PTAG_PP)):
                        comp.antecedent = ante
            #   elif FTAG_PRD in p.fTags:
            #       ante = p.getSubject()
            #       if ante: comp.antecedent = ante
            
            return
        
        for child in curr.children:
            self.__setWHAntecedents(child)

    # called by '__setWHAntecedents()'.
    def __getHighestSBAR(self, whNode):
        sbar = whNode
        while sbar.parent.pTag == PTAG_SBAR:
            sbar = sbar.parent

        if sbar.pTag == PTAG_SBAR:
            if sbar.cIndex != -1:
                for i in range(whNode.pbLoc[0]-1,-1,-1):
                    node = self.ls_terminal[i]
                    if node.isEmptyCategory():
                        t = node.form.split('-')
                        if len(t) > 1 and t[1].isdigit() and sbar.cIndex == int(t[1]):
                            return self.__getHighestSBAR(node)
            
            return sbar

        return None

    # PRE: English
    # initializes antecedent of all '*' for passive construction.
    def setPassiveAntecedents(self):
        self.__setPassiveAntecedents(self.nd_root)
    
    # called by 'setPassiveAntecedents().'
    def __setPassiveAntecedents(self, curr):
        ec = curr.getPassiveEmptyCategory()
        
        if ec and ec.form == '*':
            vp = curr.parent
            while vp.parent.pTag == PTAG_VP: vp = vp.parent
            
            if vp.parent.pTag == PTAG_NP:
                ante = vp.getPrevSibling(pTag=PTAG_NP)
                if ante: ec.antecedent = ante
        else:
            for child in curr.children:
                self.__setPassiveAntecedents(child)
    
########################### TBTree:helpers ###########################

    # returns the number of terminals : Integer
    def countTerminals(self):
        return len(self.ls_terminal)
    
    # returns the number of tokens : Integer
    def countTokens(self):
        return len(self.dc_token)

    # returns all terminal forms : String
    def toForms(self, includeEC=True):
        ls = list()
        
        for node in self.ls_terminal:
            if includeEC or not node.isEmptyCategory():
                ls.append(node.form)
        
        return ' '.join(ls)

    # returns this tree in the Penn Treebank format : String
    def toParseTree(self, numbered=False):
        return self.nd_root.toParseTree(numbered)

##### BEGIN: Class TBReader #########################################
# USAGE 1
# reader = TBReader()
# reader.open('treeFile')
# tree = reader.getTree()
# for tree in reader: do something
#
# USAGE 2
# reader = TBReader('byteFile')
# tree = getTree(int(treeId))
class TBReader:
    # tree delimiters: '(', ')', white spaces
    re_delim   = re.compile('([()\s])')
  # re_comment = re.compile('<.*>')
    
    # byteFile - gerneated by 'generate-byte-index.py' : String
    def __init__(self, byteFile=None, **kwargs):
        if byteFile: self.d_byte = self.__getByteDict(byteFile)
        else       : self.d_byte = None
        
        if 'lang' in kwargs: self.setLanguage(kwargs['lang'])
        else               : self.setLanguage(LANG_EN)
        if 'ante' in kwargs: self.b_ante = kwargs['ante']
        else               : self.b_ante = False

    # byteFile : String
    # returns a dictionary containing byte indices : Dictionary
    def __getByteDict(self, byteFile):
        fin   = open(byteFile)
        dByte = dict()
        
        for line in fin:
            l        = line.split()
            treeFile = l[0]
            lByte    = list()
            
            dByte[treeFile] = lByte
            for byte in l[1:]: lByte.append(int(byte))

        return dByte

    # returns iteration.
    def __iter__(self):
        return self
    
    # returns the next tree : TBTree
    def next(self):
        tree = self.getTree()
        if tree: return tree
        else   : raise StopIteration

########################## TBReader:getters ##########################

    # treeId : Integer
    # if 'treeId' is None, returns the next tree : TBTree
    # else returns the 'treeId'th tree : TBTree
    def getTree(self, treeId=None):
        del self.ls_tokens[:]

        if treeId:
            self.f_tree.seek(self.l_byte[treeId])
            token = self.__nextToken()    # tok = '('
        else:
            while True:
                token = self.__nextToken()
                if   not token   : return None    # end of the file
                elif token == '(': break          # loop until '(' is found

        root       = TBNode(PTAG_TOP, None)       # dummy head
        tree       = TBTree(root)
        curr       = root 
        nBrackets  = 1
        terminalId = 0
        tokenId    = 0
        
        while True:
            token = self.__nextToken()
            if nBrackets == 1 and token == PTAG_TOP: continue
            
            if token == '(':      # token_0 = '(', token_1 = 'tags'
                nBrackets += 1
                tags = self.__nextToken()
                node = TBNode(tags, curr)
                curr.addChild(node)
                curr = node
            elif token == ')':    # token_0 = ')'
                nBrackets -= 1
                curr = curr.parent
            else:                 # token_0 = 'form'
                curr.form = token
                curr.terminalId = terminalId
                tree.addTerminal(curr)
                terminalId += 1
                if curr.pTag != PTAG_NONE:
                    curr.tokenId = tokenId
                    tree.addToken(tokenId, curr)
                    tokenId += 1
            
            if nBrackets == 0:    # the end of the current tree
                tree.setPBLocs()
                
                if self.b_ante:
                    tree.setAntecedents()
                    
                    if self.s_language == LANG_EN:
                        tree.setPassiveAntecedents()
                        tree.setWHAntecedents()

                return tree
       
        return None
    
    # called by 'getTree()'.
    def __nextToken(self):
        if not self.ls_tokens:
            line = self.f_tree.readline()           # get tokens from the next line
            
            if not line:                            # end of the file
                self.close()
                return None
            if not line.strip():                    # blank line
                return self.__nextToken()
            
            for tok in self.re_delim.split(line):   # skip white-spaces
                if tok.strip(): self.ls_tokens.append(tok)
            
        return self.ls_tokens.pop(0)

########################## TBReader:setters ##########################

    def setLanguage(self, language):
        self.s_language = language

########################## TBReader:helpers ##########################

    # treeFile : String
    # opens 'treeFile'.
    def open(self, treeFile):
        self.f_tree    = open(treeFile)
        self.ls_tokens = list()
        
        if self.d_byte:
            self.l_byte = self.d_byte[treeFile]

    # closes the current Treebank file.
    def close(self):
        self.f_tree.close()

    # PRE: 'byteFile' must have been initialized.
    # treeFile : String
    # returns the number of trees in the current Treebank file : Integer
    def countTrees(self, treeFile=None):
        if treeFile:
            return len(self.d_byte[treeFile])
        else:
            return len(self.l_byte)





# lTag - list of pTags : List of String
def pTagsToRegex(lTag):
    return '^(' + '|'.join(lTag) + ')$'


