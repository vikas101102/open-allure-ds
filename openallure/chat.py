'''
The Natural Language Processing component of open-allure-ds.
Based on the Chat bot class from NLTK

Modify the bottom of this file to run doc tests or to hold a conversation.

TODO::

   Fix the natural language math parsing
   - make all test cases pass

'''
import nltk
from nltk.chat.util import random
from nltk.chat import Chat as BaseChat
from nltk.chat import reflections
from nltk.corpus import wordnet

from configobj import ConfigObj

import logging
import re
import sys
import os

class Chat(BaseChat):
    def __init__(self, tuples, reflections={}):
        """
Initialize the chatbot.

tuples must contain an iterable of patterns, responses and types.

Each pattern is a regular expression matching the user's statement or question,
e.g. r'I like (.*)'.  For each such pattern a list of possible responses
is given, e.g. ['Why do you like %1', 'Did you ever dislike %1'].  Material
which is matched by parenthesized sections of the patterns (e.g. .*) is mapped
to the numbered positions in the responses, e.g. %1.

TODO: Need to mention the types that have been introduced to the tuples
math, text etc..

@type tuples: C{list} of C{tuple}
@param tuples: The patterns and responses
@type reflections: C{dict}
@param reflections: A mapping between first and second person expressions
"""

        self._tuples = [(re.compile(x, re.IGNORECASE), y, z ,ruleName) \
        for (x, y, z, ruleName) in tuples]
        self._reflections = reflections

    def respond(self, inputString):
        """
        Generate a response to the users input.

        @type inputString: C{string}
        @param inputString: The string to be mapped
        @rtype: C{string}
        """

        # check each pattern
        respType = u''
        respName = u''
        for (pattern, response, responseType, ruleName) in self._tuples:
            match = pattern.match(inputString)

            # did the pattern match?
            if match:

                logging.info( "%s rule matched: %s" % ( responseType, ruleName ) )
                respType = responseType
                respName = ruleName

                if responseType == "graph":
                    if ruleName == 'list':
                        resp = u'Confirm\nList Records\n[input];;'
                    elif ruleName == 'meta':
                        resp = u'Confirm\nShow Meta Graph\n[input];;'
                    elif ruleName == 'reset':
                        resp = u'Confirm\nReset Graph\n[input];;'
                    elif ruleName == 'hide':
                        resp = u'Confirm\Hide Graph\n[input];;'
                    elif ruleName == 'show':
                        resp = u'Confirm\nShow Graph\n[input];;'
                    elif ruleName == 'hideText':
                        resp = u'Confirm\Hide Graph Text\n[input];;'
                    elif ruleName == 'showText':
                        resp = u'Confirm\nShow Graph Text\n[input];;'
                    elif ruleName == 'hideLabels':
                        resp = u'Confirm\Hide Graph Labels\n[input];;'
                    elif ruleName == 'showLabels':
                        resp = u'Confirm\nShow Graph Labels\n[input];;'
                    elif ruleName == 'hideResp':
                        resp = u'Confirm\Hide Graph Responses\n[input];;'
                    elif ruleName == 'showResp':
                        resp = u'Confirm\nShow Graph Responses\n[input];;'
                        
                if responseType == "quit":
                    # System exit handled in openallure.py
                    resp = u'Confirm\nQuit\n[input];;'
                    pass
                        
                if responseType == "return":
                    # Return handled in openallure.py
                    resp = u'Confirm\nReturn\n[input];;'
                    pass

                if responseType == "open":
                    pos = response.find('%')
                    num = int(response[pos + 1:pos + 2])
                    sequenceToOpen = match.group(num)

                    resp = u'Confirm\nOpen ' + sequenceToOpen + \
                           ';[' + sequenceToOpen + ']\n[input];;'

                if responseType == "text":
                    if isinstance(response, tuple):
                        # pick a random response
                        resp = random.choice(response)
                    else:
                        resp = response
                    resp = self._wildcards(resp, match) # process wildcards

                if responseType == "link":
                    # follow link to question tag (jump to question)
                    resp = response
                    
                if responseType == "show":
                    if ruleName == 'source':
                        resp = response

                if responseType == "wordLookup":
                    pos = response.find('%')
                    num = int(response[pos + 1:pos + 2])
                    wordToLookup = match.group(num)
                    wordToLookup = wordToLookup.strip(',./?!;')
                    #print( wordToLookup )
                    wordToLookupSynsets = wordnet.synsets(wordToLookup)
                    try:
                        resp = wordToLookupSynsets[0].definition
                    except IndexError:
                        resp = '"' + wordToLookup + \
                        '" was not found in the dictionary. Try again.'

                if responseType == "math":
                    operands = []
                    pos = response.find('%')
                    while pos >= 0:
                        num = int(response[pos + 1:pos + 2])
                        operands.append(match.group(num))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos + 2:]
                        pos = response.find('%')
                    operator = response.split()[3]
                    errorMessage = ""
                    if operator == "add":
                        evalString = operands[0] + '+' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Adding " + " to ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    if operator == "subtract":
                        evalString = operands[0] + '-' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Subtracting " + operands[1] + " from " + \
                               operands[0] + " gives " + \
                               str(calculatedResult) + errorMessage
                    if operator == "multiply":
                        evalString = operands[0] + '*' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Multiplying " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    if operator == "divide":
                        evalString = operands[0] + '* 1.0 /' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Dividing " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage

                if responseType == "wordMath":
                    operands = []
                    pos = response.find('%')
                    while pos >= 0:
                        num = int(response[pos + 1:pos + 2])
                        numberWord = match.group(num)
                        if numberWord[0].isdigit():
                            number = eval(numberWord)
                        else:
                            number = ['zero', 'one', 'two', 'three', 'four',
                            'five', 'six', 'seven', 'eight', 'nine', 'ten',
                            'eleven', 'twelve', 'thirteen', 'fourteen',
                            'fifteen', 'sixteen', 'seventeen', 'eighteen',
                                      'nineteen', 'twenty'].index(numberWord)
                        operands.append(str(number))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos + 2:]
                        pos = response.find('%')
                    operator = response.split()[3]
                    errorMessage = ""
                    if operator == "add":
                        evalString = operands[0] + '+' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Adding " + " to ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    if operator == "subtract":
                        evalString = operands[0] + '-' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Subtracting " + operands[1] + " from " + \
                                operands[0] + " gives " + \
                                str(calculatedResult) + errorMessage
                    if operator == "multiply":
                        evalString = operands[0] + '*' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Multiplying " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    if operator == "divide":
                        evalString = operands[0] + '* 1.0 /' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Dividing " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage

                # fix munged punctuation at the end
                if resp[-2:] == '?.': resp = resp[:-2] + '.'
                if resp[-2:] == '??': resp = resp[:-2] + '?'
                return resp, respType, respName

config = ConfigObj(r"responses.cfg")
ruleTypes = config.sections
rules = []
for section in config.sections:
    for subsection in config[section].sections:
        rule = ( config[section][subsection]['re'],
                 config[section][subsection]['reply'],
                 section, subsection )
        rules.append(rule)
responses = tuple(rules)
#print responses

# fall through cases -
# Use some of Eliza's responses:
from nltk.chat import eliza
responses = responses + tuple([(x, y, 'text', 'eliza') for (x,y) in eliza.pairs[:-3]])

# when stumped, respond with generic zen wisdom
#responses = responses + tuple([(x, y, 'text') for (x,y) in \
#nltk.chat.suntsu.pairs[2:]])

responses = responses + \
((r'(.*)', ("Sorry, I don't understand that. What now?\n[input];;",), "text", "what now"),)


import unittest


class TestChat(unittest.TestCase):
    def setUp(self):
        self.chatter = Chat(responses, reflections)

    def testQuit(self):
        '''Ask the chatbot to quit'''
        response, type, name = self.chatter.respond('quit')
        self.assertEqual(type,'quit')
    def testQuit1(self):
        response, type, name = self.chatter.respond('exit')
        self.assertEqual(type,'quit')
        
    def testOpen(self):
        response, type, name = self.chatter.respond('open something')
        self.assertEqual(type,'open')
    def testOpen1(self):
        response, type, name = self.chatter.respond('opening something')
        self.assertEqual(name,'what now')
        
    def testReturn(self):
        response, type, name = self.chatter.respond('return')
        self.assertEqual(type,'return') 
    def testReturn1(self):
        response, type, name = self.chatter.respond('ret')
        self.assertEqual(type,'return')       

    def testHi(self):
        response, type, name = self.chatter.respond('hi')
        self.assertTrue(response.startswith("Welcome"))

    def testWordLookup(self):
        response, type, name = self.chatter.respond('what is cheese?')
        self.assertEqual(response, \
        'a solid food prepared from the pressed curd of milk')

    def testWordLookup2(self):
        response, type, name = self.chatter.respond('what is learning')
        self.assertEqual(response, \
        'the cognitive process of acquiring skill or knowledge')

class TestChatMath(unittest.TestCase):

    def setUp(self):
        self.chatter = Chat(responses, nltk.chat.reflections)

    def testAdditionWords1(self):
        response, type, name = self.chatter.respond('add two and three')
        self.assertTrue(response.endswith('5'))

    def testAdditionWords2(self):
        response, type, name = self.chatter.respond('add two to three')
        self.assertTrue(response.endswith('5'), \
        'Response was: %s' % response)

    def testAdditionNumbers(self):
        response, type, name = self.chatter.respond('add 2 and 3')
        self.assertTrue(response.endswith('5'), \
        'Response was: %s' % response)

    def testSubtractionWords1(self):
        response, type, name = self.chatter.respond('subtract 20 from 30')
        self.assertTrue(response.endswith('10'), \
        'Response was: %s' % response)

    def testSubtractionLargeNumbers(self):
        response, type, name = \
        self.chatter.respond('subtract 200 from 1000')
        self.assertTrue(response.endswith('800'), \
        'Response was: %s' % response)

    def testSubtractionSymbol(self):
        response, type, name = self.chatter.respond('subtract twenty minus eight')
        self.assertTrue(response.endswith('12'), \
        'Response was: %s' % response)

    def testSubtractionWords(self):
        response, type, name = self.chatter.respond('subtract two from three')
        self.assertTrue(response.endswith('1'), response)

    def testAdditionPlus(self):
        response, type, name = self.chatter.respond('add two plus three')
        self.assertTrue(response.endswith('5'), response)

    def testAdditionTo(self):
        response, type, name = self.chatter.respond('add two to three')
        self.assertTrue(response.endswith('5'), response)

    def testAdditionAnd(self):
        response, type, name = self.chatter.respond('add two and three')
        self.assertTrue(response.endswith('5'), response)

    def testMultiply(self):
        response, type, name = self.chatter.respond('multiply five and four')
        self.assertTrue(response.endswith('20'), response)

    def testhideResp(self):
        response, type, name = self.chatter.respond('hide resp')
        self.assertTrue(name == 'hideResp', name)
    def testhideText(self):
        response, type, name = self.chatter.respond('hide text')
        self.assertTrue(name == 'hideText', name)
        
    def testhide(self):
        response, type, name = self.chatter.respond('hide graph')
        self.assertTrue(name == 'hide', name)
    def testhide1(self):
        response, type, name = self.chatter.respond('hide map')
        self.assertTrue(name == 'hide', name)
    def testlist(self):
        response, type, name = self.chatter.respond('show rec')
        self.assertTrue(name == 'list', name)
    def testlist1(self):
        response, type, name = self.chatter.respond('show records')
        self.assertTrue(name == 'list', name)
    def testlist2(self):
        response, type, name = self.chatter.respond('show list')
        self.assertTrue(name == 'list', name)
    def testlist3(self):
        response, type, name = self.chatter.respond('list rec')
        self.assertTrue(name == 'list', name)
    def testlist4(self):
        response, type, name = self.chatter.respond('list records')
        self.assertTrue(name == 'list', name)
    def testmeta5(self):
        response, type, name = self.chatter.respond('show meta')
        self.assertTrue(name == 'meta', name)
    def testmeta1(self):
        response, type, name = self.chatter.respond('show meta graph')
        self.assertTrue(name == 'meta', name)
    def testmeta2(self):
        response, type, name = self.chatter.respond('where am i overall')
        self.assertTrue(name == 'meta', name)
    def testreset(self):
        response, type, name = self.chatter.respond('reset graph')
        self.assertTrue(name == 'reset', name)
    def testreset2(self):
        response, type, name = self.chatter.respond('graph reset')
        self.assertTrue(name == 'reset', name)
    def testshow(self):
        response, type, name = self.chatter.respond('show map')
        self.assertTrue(name == 'show', name)
    def testshow1(self):
        response, type, name = self.chatter.respond('show graph')
        self.assertTrue(name == 'show', name)
    def testshow2(self):
        response, type, name = self.chatter.respond('where am i')
        self.assertTrue(name == 'show', name)
    def testshowResp(self):
        response, type, name = self.chatter.respond('show resp')
        self.assertTrue(name == 'showResp', name)
    def testshowText(self):
        response, type, name = self.chatter.respond('show text')
        self.assertTrue(name == 'showText', name)
    def testhideText(self):
        response, type, name = self.chatter.respond('hide text')
        self.assertTrue(name == 'hideText', name)
    def testshowlabels(self):
        response, type, name = self.chatter.respond('show labels')
        self.assertTrue(name == 'showLabels', name)
    def testhidelabels(self):
        response, type, name = self.chatter.respond('hide labels')
        self.assertTrue(name == 'hideLabels', name)

if __name__ == "__main__":
    #test = False
    test = True
    if test:
        unittest.main()
    else:
        chatter = Chat(responses, nltk.chat.reflections)
        chatter.converse()
