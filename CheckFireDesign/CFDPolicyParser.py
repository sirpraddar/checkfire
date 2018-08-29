from CheckFireCore.TestPackage import TestPackage,Test
import configparser
import re


class PolicyParser():
    def __init__(self,libH):
        self.testMap = {}
        self.lib = TestPackage(name=libH['LIBH']['LibraryPackage'])
        self.lib.loadFromFile()

        for key,entries in libH.items():
            if not key == "DEFAULT":
                self.testMap[key] = TestParser(key,self.lib,entries)

    def parseNetwork(self,network):
        policies = network['Policies'].split()
        retPack = TestPackage(name=network['NETWORK']['name'])

        for phrase in policies:
            test = self.__getTestFromPhrase(phrase)
            test.parsePhrase(phrase)
            retPack.tests[test.name] = test

        return retPack


    def __getTestFromPhrase(self,phrase):
        phrasecut = re.sub("[A-Za-z0-9\.\,\-]* ?can (not )?","",phrase)
        name = ""
        test = None
        for word in phrasecut:
            name = name + word
            try:
                test = self.testMap[name]
            except ValueError:
                pass

        return test


class TestParser():
    def __init__(self,name,testLib,entries=None):
        if not entries:
            self.test = None
            self.phrase = None
            self.parser = None
        else:
            self.test = testLib.tests[entries['test']]
            self.phrase = entries['phrase']
            self.parser = PhraseParser(self.phrase)
        self.name = name

    def parsePhrase(self,phrase):
        params = self.parser.parsePhrase(phrase)
        mytest = Test(self.test.toDict())
        mytest.tparams = params
        return mytest


class PhraseParser():
    WORD_PARAM = 1
    WORD_LANGUAGE = 2
    WORD_OPTIONAL = 128

    def __init__(self, phrase, subparsers=None):
        if subparsers is None:
            self.subParsers = []
        else:
            self.subParsers = subparsers
        self.words = []
        self.phrase = phrase
        self.__initParser()

    def __initParser(self):
        tokens = self.phrase.split()
        self.words = []
        for t in tokens:
            if re.match("\{\w+\}", t):  # parameter token word found
                self.words.append((self.WORD_PARAM, t[1:-1]))
            elif re.match("\w+", t):
                self.words.append((self.WORD_LANGUAGE, t))
            else:
                raise ValueError

    def parsePhrase(self, phrase):
        params, _ = self.__parsePhraseRecursive(phrase.split())
        return params

    def __parsePhraseRecursive(self, tokens):
        mytokens = tokens[0:len(self.words)]
        params = {}
        for t, w in zip(mytokens, self.words):
            if w[0] == self.WORD_LANGUAGE and not t == w[1]:
                raise ValueError
            elif w[0] == self.WORD_PARAM:
                params[w[1]] = t
        othertokens = tokens[len(self.words):]
        errors = 0
        for p in self.subParsers:
            try:
                subparams, index = p.__parsePhraseRecursive(othertokens)
                params.update(subparams)
                othertokens = othertokens[index:]
            except:
                errors = errors + 1
        if len(self.subParsers) > 0 and errors == len(self.subParsers):
            raise ValueError
        return params, len(self.words)

    def printSubParsers(self, indent=0):
        print("")
        for w in self.words:
            print(" " * indent + "({},{})".format(w[0], w[1]))
        for i in self.subParsers:
            i.printSubParsers(indent + 3)

    @staticmethod
    def buildParserTree(phrase):
        groups = PhraseParser.__generateGroups(phrase)
        tree, _ = PhraseParser.__buildRecursive(groups, 0)
        stree = PhraseParser.__encodePhrase(phrase, tree)
        return PhraseParser.__generateParsers(stree)

    @staticmethod
    def __buildRecursive(groups, index):
        thisgroup = groups[index]
        index = index + 1
        end = thisgroup[1]
        childs = [thisgroup]
        try:
            while (groups[index][0] < end):
                gruppo, index = PhraseParser.__buildRecursive(groups, index)
                childs.append(gruppo)
        except IndexError:
            pass
        return childs, index

    @staticmethod
    def __generateGroups(phrase):
        # frase = '[' + frase + ']'
        squares = []
        groups = []
        for i in re.finditer("[\[\]]{1}", phrase):
            if i.group() == '[':
                squares.append(i.span()[1])
            elif i.group() == ']':
                groups.append((squares.pop(), i.span()[0]))
        groups.append((0, len(phrase)))
        groups.sort()
        return groups

    @staticmethod
    def __encodePhrase(phrase, tree):
        thislevel = []
        node = tree[0]
        nodes = phrase[node[0]:node[1]]

        for i in tree:
            if not isinstance(i, list):
                continue
            thislevel.append(PhraseParser.__encodePhrase(phrase, i))
        nodes = re.sub("\[.*\]", "", nodes)
        nodes = nodes.strip()
        thislevel.insert(0, nodes)
        return thislevel

    @staticmethod
    def __generateParsers(trees):
        parsers = []
        for i in trees:
            if isinstance(i, list):
                parsers.append(PhraseParser.__generateParsers(i))

        me = PhraseParser(trees[0], parsers)
        return me
