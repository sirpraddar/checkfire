from CheckFireCore.TestPackage import TestPackage,Test
from .CFDNetworkCalculator import NetworkCalculator
import configparser
import re


class PolicyParser():
    def __init__(self,libH):
        self.testMap = {}
        self.lib = TestPackage(name=libH['LIBH']['LibraryPackage'])
        self.lib.loadFromFile()
        for key,entries in libH.items():
            if not key == "LIBH":
                self.testMap[key] = TestParser(key,self.lib,entries)

    def parseNetwork(self,network):
        networkResolver = NetworkCalculator(network)
        policies = network['Policies'].keys()
        retPack = TestPackage(name=network['NETWORK']['name'])
        count = 1
        for phrase in policies:
            negate = False
            testparser = self.__getTestFromPhrase(phrase)
            phrasecut = re.sub("[A-Za-z0-9\.\,\-]* ?can (not )?", "", phrase)
            tokens = phrase.split()

            if testparser.test not in retPack.tests:
                retPack.copyTestFromPackage(self.lib,testparser.test.name)
            test = testparser.parsePhrase(phrasecut)

            test.name = str(count) + "-" + phrasecut.split()[0]
            test.description = phrase
            if tokens[2] == "not":
                test.negate = True

            #todo: substitute network placeholders with real addresses
            for n,p in test.tparams.items():
                try:
                    test.tparams[n] = networkResolver.resolveDestAddress(p)
                except:
                    pass

            #todo: Assign test to the right worker node
            try:
                retPack.remoteToDo[networkResolver.getWorkerNode(tokens[0])].append(test.name)
            except KeyError:
                retPack.remoteToDo[networkResolver.getWorkerNode(tokens[0])] = [test.name]
            retPack.tests[test.name] = test

            count += 1
        return retPack


    def __getTestFromPhrase(self,phrase):
        phrasecut = re.sub("[A-Za-z0-9\.\,\-]* ?can (not )?","",phrase)
        #phrasecut = phrasecut.split()
        name = ""
        test = None

        for word in phrasecut:
            #name = name + " " + word
            name = name + word

            try:
                test = self.testMap[name]
                break
            except KeyError:
                pass
        if test == None:
            raise KeyError
        return test


class TestParser():
    def __init__(self,name,testLib,entries=None):
        if not entries:
            self.test = None
            self.phrase = None
            self.parser = None
            self.constparams = None
        else:
            self.test = testLib.tests[entries['test']]
            self.phrase = entries['phrase']
            try:
                self.constparams = {}
                for p in entries['params'].split():
                    pT = p.split("=")
                    self.constparams[pT[0]] = pT[1]
            except:
                pass
            self.parser = PhraseParser.buildParserTree(self.phrase)
        self.name = name

    def parsePhrase(self,phrase):
        params = self.parser.parsePhrase(phrase)
        mytest = Test(dictLoaded=self.test.toDict())
        if self.constparams:
            params.update(self.constparams)
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
            if re.match("\{[A-Za-z0-9\.\:\/\-]+\}", t):  # parameter token word found
                self.words.append((self.WORD_PARAM, t[1:-1]))
            elif re.match("\w+", t):
                self.words.append((self.WORD_LANGUAGE, t))
            else:
                print("Token error: "+t)
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
