'''
The Natural Language Processing component of open-allure-ds.
Based on the Chat bot class from NLTK

Modify the bottom of this file to run doc tests or to hold a conversation.

TODO::

   Fix the natural language math parsing
   - make all test cases pass
   
'''

from nltk.chat.util import random
from nltk.chat import Chat as BaseChat
from nltk.chat import reflections
from nltk.corpus import wordnet

from configobj import ConfigObj

import logging
import re

class Chat(BaseChat):
    def __init__(self, tuples, reflections={}):
        """
        Initialize the chatbot.
        
        tuples must contain an iterable of patterns, responses, types and rule names. 
        
        Each pattern is a regular expression matching the user's statement or question,
        e.g. r'I like (.*)'.  For each such pattern a list of possible responses
        may be given, e.g. ['Why do you like %1', 'Did you ever dislike %1'].  Material
        which is matched by parenthesized sections of the patterns (e.g. .*) is mapped to
        the numbered positions in the responses, e.g. %1.
        
        See responses.cfg for documentation on the available types.

        @type tuples: C{list} of C{tuple}
        @param tuples: The patterns and responses with types and rule names
        @type reflections: C{dict}
        @param reflections: A mapping between first and second person expressions
        """

        self._tuples = [(re.compile(x, re.IGNORECASE),y,z,ruleName) for (x,y,z,ruleName) in tuples]
        self._reflections = reflections

    def respond(self, inputString):
        """
        Generate a response to the users input.

        @type inputString: C{string}
        @param inputString: The string to be mapped
        @rtype: C{string}
        """

        # check each pattern
        for (pattern, response, responseType, ruleName) in self._tuples:
            match = pattern.match(inputString)

            # did the pattern match?
            if match:
            
                logging.info( "%s rule matched: %s" % ( responseType, ruleName ) )
                
                if responseType == "quit":
                    #TODO: Make this more polite
                    raise SystemExit

                if responseType == "open":
                    pos = response.find('%')
                    num = int(response[pos+1:pos+2])
                    sequenceToOpen = match.group(num)

                    resp = 'Confirm\nOpen ' + sequenceToOpen + \
                           ';[' + sequenceToOpen + ']'

                if responseType == "text":
                    if isinstance(response,tuple):
                        resp = random.choice(response)    # pick a random response
                    else:
                        resp = response
                    resp = self._wildcards(resp, match) # process wildcards

                if responseType == "link":
                    # follow link to question tag (jump to question)
                    resp = response
                    
                if responseType == "wordLookup":
                    pos = response.find('%')
                    num = int(response[pos+1:pos+2])
                    wordToLookup = match.group(num)
                    wordToLookup = wordToLookup.strip(',./?!;')
                    #print( wordToLookup )
                    wordToLookupSynsets = wordnet.synsets( wordToLookup )
                    try:
                       resp =wordToLookupSynsets[0].definition
                    except IndexError:
                        resp = '"'+ wordToLookup + '" was not found in the dictionary. Try again.'

                if responseType == "math":
                    operands = []
                    pos = response.find('%')
                    while pos >= 0:
                        num = int(response[pos+1:pos+2])
                        operands.append(match.group(num))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos+2:]
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
                       resp = "Adding " + " to ".join(operands) + " gives " + \
                               str(calculatedResult) + errorMessage
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
                       resp = "Multiplying " + " by ".join(operands) + " gives " + \
                               str(calculatedResult) + errorMessage
                    if operator == "divide":
                       evalString = operands[0] + '* 1.0 /' + operands[1]
                       try:
                           calculatedResult = eval(evalString)
                       except SyntaxError:
                           calculatedResult = 0
                           errorMessage = " (due to syntax error)"
                       resp = "Dividing " + " by ".join(operands) + " gives " + \
                               str(calculatedResult) + errorMessage

                if responseType == "wordMath":
                    operands = []
                    pos = response.find('%')
                    while pos >= 0:
                        num = int(response[pos+1:pos+2])
                        numberWord = match.group(num)
                        if numberWord[0].isdigit():
                            number = eval( numberWord )
                        else:
                            number = ['zero','one','two','three','four','five','six','seven','eight','nine','ten',
                                      'eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen',
                                      'nineteen','twenty'].index(numberWord)
                        operands.append(str(number))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos+2:]
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
                       resp = "Adding " + " to ".join(operands) + " gives " + \
                               str(calculatedResult) + errorMessage
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
                       resp = "Multiplying " + " by ".join(operands) + " gives " + \
                               str(calculatedResult) + errorMessage
                    if operator == "divide":
                       evalString = operands[0] + '* 1.0 /' + operands[1]
                       try:
                           calculatedResult = eval(evalString)
                       except SyntaxError:
                           calculatedResult = 0
                           errorMessage = " (due to syntax error)"
                       resp = "Dividing " + " by ".join(operands) + " gives " + \
                               str(calculatedResult) + errorMessage

                # fix munged punctuation at the end
                if resp[-2:] == '?.': resp = resp[:-2] + '.'
                if resp[-2:] == '??': resp = resp[:-2] + '?'
                return resp

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
print responses

# fall through cases -
# Use some of Eliza's responses:
from nltk.chat import eliza
responses = responses + tuple([(x, y, 'text', 'eliza') for (x,y) in eliza.pairs[:-3]])

# when stumped, respond with generic zen wisdom
#responses = responses + tuple([(x, y, 'text', 'zen') for (x,y) in nltk.chat.suntsu.pairs[2:]])

responses = responses + ((r'(.*)', ("Sorry, I don't understand that. What now?\n[input];;",), "text", "no match what now"),)

import unittest

class TestChat( unittest.TestCase):
    def setUp(self):
        self.chatter = Chat(responses, reflections)

    def testQuitWorks( self ):
        '''Ask the chatbot to quit'''
        self.assertRaises(SystemExit, self.chatter.respond, ('quit'))
        
    def testHello(self):
        response = self.chatter.respond('hi')
        self.assertTrue( response.startswith("Welcome") )

    def testWordLookup(self):
        response = self.chatter.respond('what is cheese?')
        self.assertEqual( response, "a solid food prepared from the pressed curd of milk")
        
    def testWordLookup2(self):
        response = self.chatter.respond('what is learning')
        self.assertEqual(response, 'the cognitive process of acquiring skill or knowledge')
        
class TestChatMath( unittest.TestCase ):

    def setUp( self ):
        self.chatter = Chat(responses, reflections)
    
    def testAdditionWords1( self ):
        response = self.chatter.respond('add two and three')
        self.assertTrue( response.endswith('5'))

    def testAdditionWords2( self ):
        response = self.chatter.respond('add two to three')
        self.assertTrue( response.endswith('5'), 'Response was: %s' % response )
        
    def testAdditionNumbers (self ):
        response = self.chatter.respond('add 2 and 3')
        self.assertTrue( response.endswith('5'),'Response was: %s' % response)
    
    def testSubtractionWords1( self ):
        response = self.chatter.respond('subtract 20 from 30')
        self.assertTrue( response.endswith('10'),'Response was: %s' % response)
    
    def testSubtractionLargeNumbers(self):
        response = self.chatter.respond('subtract two hundred from one thousand')
        self.assertTrue( response.endswith('800'),'Response was: %s' % response)
        
    def testSubtractionSymbol( self ):
        response = self.chatter.respond('twenty - eight')
        self.assertTrue( response.endswith('12'), 'Response was: %s' % response)
    
    def testSubtractionWords( self ):
        response = self.chatter.respond('three - two')
        self.assertTrue( response.endswith('1'), response)
        
    def testAdditionPlus( self ):
        response = self.chatter.respond('two plus three')
        self.assertTrue( response.endswith('5'), response)
        
    def testAddition( self ):
        res = self.chatter.respond('two + three')
        self.assertTrue( res.endswith('5'), res)
        
    def testMultiply(self):
        res = self.chatter.respond('multiply five and four')
        self.assertTrue( res.endswith('20'), res)
        
if __name__ == "__main__":
    test = False
    if test:
        unittest.main()
    else:
        chatter = Chat(responses, reflections)
        chatter.converse()
