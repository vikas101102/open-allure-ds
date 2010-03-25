"""
openallure.py

Voice-and-vision enabled dialog system

Project home at `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

__version__='0.1d7dev'

# Standard Python modules
import ConfigParser
import logging
import os
import random
import re
import string

# 3rd Party modules
from nltk.corpus import wordnet
import pygame

# Import from Open Allure DS modules
from gesture import Gesture
from qsequence import QSequence
from text import OpenAllureText
from video import VideoCapturePlayer, GreenScreen
from voice import Voice

# Setup logging
logging.basicConfig( level=logging.DEBUG )

WELCOME_TEXT = """
   Welcome to Open Allure, a voice-and-vision enabled dialog system.

   F4 to recalibrate green screen.
   Escape to quit.

   Enjoy!
"""

reflections = {
  "am"     : "are",
  "was"    : "were",
  "i"      : "you",
  "i'd"    : "you would",
  "i've"   : "you have",
  "i'll"   : "you will",
  "my"     : "your",
  "are"    : "am",
  "you've" : "I have",
  "you'll" : "I will",
  "your"   : "my",
  "yours"  : "mine",
  "you"    : "me",
  "me"     : "you"
}

class OpenAllure(object):
    def __init__(self):
        self.voiceChoice = -1
        self.question = []
        self.ready = False
        self.stated = False
        self.currentString = ''

openallure = OpenAllure()

class Chat(object):
    def __init__(self, tuples, reflections={}):
        """
        Initialize the chatbot.  tuples is a list of patterns and responses.  Each
        pattern is a regular expression matching the user's statement or question,
        e.g. r'I like (.*)'.  For each such pattern a list of possible responses
        is given, e.g. ['Why do you like %1', 'Did you ever dislike %1'].  Material
        which is matched by parenthesized sections of the patterns (e.g. .*) is mapped to
        the numbered positions in the responses, e.g. %1.

        @type tuples: C{list} of C{tuple}
        @param tuples: The patterns and responses
        @type reflections: C{dict}
        @param reflections: A mapping between first and second person expressions
        @rtype: C{None}
        """

        self._tuples = [(re.compile(x, re.IGNORECASE),y,z) for (x,y,z) in tuples]
        self._reflections = reflections

    # bug: only permits single word expressions to be mapped
    def _substitute(self, inputString):
        """
        Substitute words in the string, according to the specified reflections,
        e.g. "I'm" -> "you are"

        @type inputString: C{string}
        @param inputString: The string to be mapped
        @rtype: C{string}
        """

        words = ""
        for word in string.split(string.lower(inputString)):
            if self._reflections.has_key(word):
                word = self._reflections[word]
            words += ' ' + word
        return words

    def _wildcards(self, response, match):
        pos = string.find(response,'%')
        while pos >= 0:
            num = string.atoi(response[pos+1:pos+2])
            response = response[:pos] + \
                self._substitute(match.group(num)) + \
                response[pos+2:]
            pos = string.find(response,'%')
        return response

    def respond(self, inputString):
        """
        Generate a response to the user input.

        @type inputString: C{string}
        @param inputString: The string to be mapped
        @rtype: C{string}
        """

        # check each pattern
        for (pattern, response, responseType) in self._tuples:
            match = pattern.match(inputString)

            # did the pattern match?
            if match:
                if responseType == "quit":
                    #TODO: Make this more polite
                    os.sys.exit()

                if responseType == "text":
                    if isinstance(response,tuple):
                        resp = random.choice(response)    # pick a random response
                    else:
                        resp = response
                    resp = self._wildcards(resp, match) # process wildcards

                if responseType == "wordLookup":
                    pos = string.find(response,'%')
                    num = string.atoi(response[pos+1:pos+2])
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
                    pos = string.find(response,'%')
                    while pos >= 0:
                        num = string.atoi(response[pos+1:pos+2])
                        operands.append(match.group(num))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos+2:]
                        pos = string.find(response,'%')
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
                    pos = string.find(response,'%')
                    while pos >= 0:
                        num = string.atoi(response[pos+1:pos+2])
                        numberWord = match.group(num)
                        if numberWord[0] in string.digits:
                            number = eval( numberWord )
                        else:
                            number = ['zero','one','two','three','four','five','six','seven','eight','nine','ten',
                                      'eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen',
                                      'nineteen','twenty'].index(numberWord)
                        operands.append(str(number))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos+2:]
                        pos = string.find(response,'%')
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

    # Hold a conversation with a chatbot
    def converse(self, quit="quit"):
        input = ""
        while input != quit:
            input = quit
            try: input = raw_input(">")
            except EOFError:
                print( input )
            if input:
                while input[-1] in "!.": input = input[:-1]
                print( self.respond(input) )


# responses are matched top to bottom, so non-specific matches occur later
# for each match, a list of possible responses is provided
responses = (


    (r'(demo|hi|hello)(.*)',
    ( "Welcome.\nHere are some choices:\nDo simple math;;\nExplore a dictionary;;;\nLearn about Open Allure;[about.txt]\n[input];;;;\n\nOK.\nTry some two operand math\nlike ADD 2 + 2:\n[input];;\n\nLook up words\nby entering WHAT IS <word>:\n[input];;\n"),"text"),

    (r'(.*)(turing|loebner)(.*)',
    ( "I was hoping this would come up.\nLook at std-turing.aiml;[turing.txt]"),"text"),

    (r'(quit|exit)',
    ( "Request to quit"),"quit"),
##
##    (r'(good|bad)',
##    ( "I'm not%1","You're%1","So%1"),"text"),

# Extract numbers from math expressions

    # Addition
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\+\s*(\-?[0-9.]+)',
    ( "You want to add%1 and%2"),"math"),
    # Subtraction
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\-\s*(\-?[0-9.]+)',
    ( "You want to subtract%1 minus%2"),"math"),
    # Multiplication
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\*\s*(\-?[0-9.]+)',
    ( "You want to multiply%1 by%2"),"math"),
    # Division /
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\/\s*(\-?[0-9.]+)',
    ( "You want to divide%1 by%2"),"math"),

# Word math expressions

    # Addition
    (r'(what is|what\'s|find|calculate|add)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|[0-9.]+)\s+plus\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to add%2 and%3"),"wordMath"),

    (r'add\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(and|plus)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to add%1 and%3"),"wordMath"),

    # Subtraction
    (r'(what is|what\'s|find|calculate|subtract)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+minus\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to subtract%2 minus%3"),"wordMath"),

    (r'subtract\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+from\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to subtract%2 minus%1"),"wordMath"),

    # Multiplication
    (r'(what is|what\'s|find|calculate|multiply)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(times|multiplied by)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to multiply%2 by%4"),"wordMath"),

    # Division /
    (r'(what is|what\'s|find|calculate|divide)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(over|divided by|by)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to divide%2 by%4"),"wordMath"),

# Word lookup expressions

    (r'(what does|what\'s)\s+(.*)\s+mean(.*)',
    ( "You want to define%2"),"wordLookup"),

    (r'(what is an|what is a|what is the|what is|search for|search|what\'s an|what\'s a|what\'s|find|define|defined)\s+(.*)',
    ( "You want to define%2"),"wordLookup"),

# fall through case -
# when stumped, respond with generic zen wisdom
#
# Test returning multiline response
    (r'(.*)',
     ( "Sorry, I don't understand that. What now?\nQuit;;Thanks" ),"text")
)



def main():
    """Initialization and event loop"""

    # provide instructions and other useful information (hide by elevating logging level:
    logging.info( "Open Allure Version: %s" % __version__ )
    logging.debug( "Pygame Version: %s" % pygame.__version__ )

    # initialize pyGame screen
    textRect = pygame.rect.Rect( 0, 0, 640, 480 )
    screenRect = pygame.rect.Rect( 0, 0, 752, 600 )
    pygame.init()
    screen = pygame.display.set_mode( screenRect.size )

    # load initial question sequence from url specified in openallure.cfg file
    config = ConfigParser.RawConfigParser()
    config.read( 'openallure.cfg' )
    url = config.get( 'Source', 'url' )
    backgroundColor = eval( config.get( 'Colors', 'background' ) )
    seq = QSequence( filename=url )
    logging.info( "Question sequence Loaded with %s questions" % str( len( seq.sequence ) ) )
    #print seq.sequence

##    # load initial AIML file
##    k = aiml.Kernel()
##    aiml = config.get( 'Source', 'aiml' )
##    aimlLoadPattern = config.get( 'Source', 'aimlLoadPattern' )
##    k.learn( aiml )
##    AIMLResponse = k.respond( aimlLoadPattern )
##    logging.info( "AIML %s" % (aiml + " " + AIMLResponse ) )

    # initialize chatbot
    openallure_chatbot = Chat(responses, reflections)
    logging.info( "Chatbot initialized" )


    # load browser command string
    browser = config.get( 'Browser', 'browser' )

    greenScreen = GreenScreen()
    vcp         = VideoCapturePlayer( processFunction=greenScreen.process )
    gesture     = Gesture()
    voice       = Voice()

    margins     = [ 20, 20, 620, 460 ]
    text        = OpenAllureText( margins )

    showFlag = eval( config.get( 'Video', 'showFlag' ) )

    # start on first question of sequence
    # TODO: have parameter file track position in sequence at quit and resume there on restart
    onQuestion = 0

    # initialize mode flags
    # Has new question from sequence been prepared?
    openallure.ready = False
    # Has question been openallure.stated (read aloud)?
    openallure.stated = False
    # What choice (if any) has been highlighted by gesture or keyboard?
    highlight= 0
    # When was choice first highlighted by gesture?
    choiceStartTime = 0
    # How much of highlight color should be blended with selected color? in how many steps? with how much time (in ticks) per step?
    colorLevel = colorLevels = 12
    colorLevelStepTime = 100
    # Do we have an answer? what number is it (with 0 being first answer)?
    answer = -1
    # What questions have been shown (list)?
    questions = []
    # What has been typed in so far
    openallure.currentString = ""


    # Greetings
    vcp.talk()
    voice.speak( 'Hello' )
    vcp.smile()

    print WELCOME_TEXT

    while 1:

        if not openallure.ready:
            # prepare for question display
            openallure.question = seq.sequence[ onQuestion ]
            choiceCount, questionText, justQuestionText = text.buildQuestionText( openallure.question )

            textRegions = text.preRender( questionText[ choiceCount ] )

            # initialize pointers - no part of the question text and none of the answers
            # have been read aloud.  Note that question text is numbered from 0
            # while answers are numbered from 1.
            openallure.stated = False
            onText = 0
            onAnswer = 0
            next = 0

            # initialize selections - nothing has been highlighted or previously
            # selected as an answer
            highlight = 0
            colorLevel = colorLevels
            choice = ( - 1, 0 )
            answer = -1
            eliminate = []

            # initialize typed input
            openallure.currentString = ''

            # clear screen of last question
            screen.fill( backgroundColor, rect=textRect )
            greenScreen.calibrated = False
            greenScreen.backgrounds = []
            vcp.processruns = 0
            openallure.ready = True

        # make sure currentString has been added to questionText
        # as new contents may have been added by voice
        if openallure.currentString:
            questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + \
                                          "\n" + openallure.currentString

        # get keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT   \
               or (event.type == pygame.KEYDOWN and    \
                   event.key == pygame.K_ESCAPE):
                return

            # Trap and quit on Ctrl + C
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_c and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                return

            # Define toggle keys and capture character by character string inputs
            elif event.type == pygame.KEYDOWN:
               # Keys 1 through 6 select choices 1 through 6
               if event.key in range( pygame.K_1, pygame.K_6 ) and \
                  not openallure.question[ 6 ][choiceCount - 1 ] == 1:
                   answer = event.key - pygame.K_1
                   if answer < choiceCount:
                       choice = ( answer + 1, 0 )
                       colorLevel = 0
                   else:
                       answer = -1

               elif event.key == pygame.K_F3:
                    showFlag = not showFlag
               elif event.key == pygame.K_F4:
                    greenScreen.calibrated = False
               elif event.key == pygame.K_F5:
                    gesture.showPixels = not gesture.showPixels
               elif event.key == pygame.K_F6:
                    # reveal all the attributes of openallure
                    print( openallure.__dict__ )
                    # drop into interpreter for debugging
                    import code; code.interact(local=locals())

               # Allow space to silence reading of question unless there is an input (which might require a space)
               elif event.key == pygame.K_SPACE and not openallure.question[ 6 ][choiceCount - 1 ] == 1:
                    # Silence reading of question
                    openallure.stated = True
               elif event.key == pygame.K_RETURN:
                   if openallure.currentString:
                          nltkResponse = openallure_chatbot.respond( openallure.currentString )
                          print openallure.currentString
                          print nltkResponse
                          # if nltkResponse is one line containing a semicolon, replace the semicolon with \n
                          if nltkResponse.find('\n') == -1:
                              nltkResponse = nltkResponse.replace(';','\n')
                          filename = "nltkResponse.txt"
                          f = open( filename, 'w' )
                          f.write( nltkResponse )
                          f.write( "\n[input];;\n")
                          f.close()
                          if nltkResponse:
                              answer = choiceCount - 1
                              choice = ( choiceCount, 0 )
##                        aimlResponse = k.respond( openallure.currentString )
##                        # print answer, k.respond( openallure.currentString )
##                        # put response in a file for now
##                        filename = "aimlResponse.txt"
##                        f = open( filename, 'w')
##                        ##                print k.respond( openallure.currentString )
##                        ##                print k.respond( openallure.currentString ).replace( '\\n ', '\n' )
##                        f.write( aimlResponse.replace( '\\n ', '\n' ) )
##                        f.close()
##                        if aimlResponse:
##                           answer = choiceCount - 1
##                           choice = ( choiceCount, 0 )
                   else:
                       # This takes last response
                       answer = choiceCount - 1
                       choice = ( choiceCount, 0 )
               elif event.key == pygame.K_BACKSPACE and openallure.question[ 6 ][choiceCount - 1 ] == 1:
                   openallure.currentString = openallure.currentString[0:-1]
                   openallure.question[ 1 ][ choiceCount - 1 ] = openallure.currentString
                   questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + "\n" + openallure.currentString
                   screen.fill( backgroundColor, rect=textRect)
               elif event.key <= 127 and openallure.question[ 6 ][choiceCount - 1 ] == 1:
##                   print event.key
                   mods = pygame.key.get_mods()
                   if mods & pygame.KMOD_SHIFT:
                       if event.key in range( 47, 58 ):
                           openallure.currentString += \
                           ('?',')','!','@','#','$','%','^','&','*','('
                           )[range( 47, 58 ).index( event.key )]
                       elif event.key == 45:
                           openallure.currentString += "_"
                       elif event.key == 61:
                           openallure.currentString += "+"
                       else:
                           openallure.currentString += chr( event.key ).upper()
                   else:
                       openallure.currentString += chr( event.key )
                   openallure.question[ 1 ][ choiceCount - 1 ] = openallure.currentString
                   questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + \
                                                 "\n" + openallure.currentString
                   screen.fill( backgroundColor, rect=textRect)

        if openallure.voiceChoice > 0:
            print openallure.voiceChoice
            openallure.stated = 1
            choice = ( openallure.voiceChoice, 0 )
            # block non-choices
            if choice[ 0 ] < 0 or choice[ 0 ] > len( questionText ) - 1 :
                choice = ( -1, 0 )
            else:
                answer = openallure.voiceChoice - 1
                colorLevel = 0
                openallure.voiceChoice = 0
                # Update screen to reflect choice
                text.paintText(screen,
                               justQuestionText, onText,
                               questionText,     onAnswer,
                               highlight,
                               openallure.stated,
                               choice,
                               colorLevel,colorLevels)
                pygame.display.flip()

#        print openallure.voiceChoice
        if openallure.voiceChoice > 0:
            openallure.stated = 1
            answer = openallure.voiceChoice - 1
            colorLevel = 0
            openallure.voiceChoice = 0
            # Update screen to reflect choice
            text.paintText(screen,
                           justQuestionText, onText,
                           questionText,     onAnswer,
                           highlight,
                           openallure.stated,
                           choice,
                           colorLevel,colorLevels)
            pygame.display.flip()


        if answer < 0 and openallure.ready:
            # check webcam
            processedImage = vcp.get_and_flip( show=showFlag )

            # show a photo
            if isinstance( vcp.photoSmile,pygame.Surface ) and openallure.currentString == '' and openallure.stated == 1:
               vcp.display.blit( vcp.photoSmile, (650,10))

            if isinstance( vcp.photoTalk,pygame.Surface ) and openallure.currentString == '' and openallure.stated == 0:
               vcp.display.blit( vcp.photoTalk, (650,10))

            if isinstance( vcp.photoListen,pygame.Surface ) and not openallure.currentString == '':
               vcp.display.blit( vcp.photoListen, (650,10))

            # show the raw input
            if isinstance( vcp.snapshotThumbnail,pygame.Surface ):
                vcp.display.blit( vcp.snapshotThumbnail, (10,480) )

            # show the green screen
            if isinstance( vcp.processedShotThumbnail,pygame.Surface ):
                vcp.display.blit( vcp.processedShotThumbnail, (190,480) )

            # obtain choice from processed snapshot
            if isinstance( processedImage,pygame.Surface ):
                choice = gesture.choiceSelected( processedImage, textRegions, margins )
##                if choice[0]> 0:
##                    print choice

            # show selected boxes
            if isinstance( gesture.scaledImageWithPixels,pygame.Surface ):
                vcp.display.blit( gesture.scaledImageWithPixels, (370,480) )

            pygame.display.flip()

            # block non-choices
            if choice[ 0 ] < 0 or choice[ 0 ] > len( questionText ) - 1 :
                choice = ( -1, 0 )
            #print choice, highlight

            # adjust highlight and colorLevel
            if highlight > 0 and highlight == choice[ 0 ]:
                # choice was previously highlighted. Find out how long.
                dwellTime = pygame.time.get_ticks() - choiceStartTime
                #if choice[0] > 0: print choice, highlight, colorLevel, dwellTime
                # print dwellTime
                # lower color level to 0
                colorLevel = colorLevels - int( dwellTime / colorLevelStepTime )
                colorLevel = max( 0, colorLevel )
                #TODO: provide shortcut to go immediately to colorLevel=0
                #if choice[1] (number of selected boxes) is big enough
                if colorLevel == 0:
                    # choice has been highlighted long enough to actually be the desired selection
                    choiceMade = True
                    answer = choice[ 0 ] - 1
    ##                print openallure.question[1]
    ##                print choice[0]
                    voice.speak( "You selected " + openallure.question[ 1 ][ answer ] )
                    highlight = 0
                else:
                    # block a choice that has not been highlighted long enough
                    choice = ( -1, 0 )
            else:
                # new choice or no choice
                highlight      = min( choice[ 0 ], choiceCount )
                if highlight < 0:
                    highlight = 0
                    colorLevel = colorLevels
                else:
                    choiceStartTime = pygame.time.get_ticks()

            screen.fill( backgroundColor, rect=textRect )
            text.paintText(screen,
                           justQuestionText, onText,
                           questionText,     onAnswer,
                           highlight,
                           openallure.stated,
                           choice,
                           colorLevel,colorLevels)

        elif not choice == ( - 1, 0 ):
            # respond to choice when something has been typed and entered
            if len( openallure.currentString ):
##                if len( aimlResponse ) == 0:
                if len( nltkResponse ) == 0:
                    choice = ( -1, 0 )
                    answer = -1
                    voice.speak("Try again")
                else:
                    voice.speak("You entered " + openallure.currentString )
                # Reset string
                openallure.currentString = ''

            # check whether a link is associated with this answer and, if so, follow it
            if openallure.question[ 5 ][ answer ]:
                os.system( browser + " " + openallure.question[ 5 ][ answer ] )

            #check that response exists for answer
            if answer < len( openallure.question[ 2 ] ) and (isinstance( openallure.question[ 2 ][ answer ], str ) or \
                                                  isinstance( openallure.question[ 2 ][ answer ], unicode)):
                  #speak response to answer
                  voice.speak(openallure.question[ 2 ][ answer ].strip())

            #check that next sequence exists as integer for answer
            if answer < len( openallure.question[ 3 ] ) and isinstance( openallure.question[ 3 ][ answer ], int ):
              #get new sequence or advance in sequence
              next = openallure.question[ 3 ][ answer ]
              if next == 88:
                  # speak( "New source of questions" )
                  path = seq.path
                  #print "path is ", path
                  seq = QSequence( filename = openallure.question[ 4 ][ answer ], path = path )
                  onQuestion = 0
                  openallure.ready = False
              elif next == 99:
                  voice.speak( "Taking dictation" )
                  #TODO
              else:
                  # Add last question to stack and move on
                  if next > 0:
                     questions.append( onQuestion )
                     onQuestion = onQuestion + next

                  # Try to pop question off stack if moving back
                  elif next < 0:
                    for i in range( 1, 1 - next ):
                           if len( questions ) > 0:
                                        onQuestion = questions.pop()
                           else:
                                        onQuestion = 0

                  # Quit if advance goes beyond end of sequence
                  if onQuestion >= len( seq.sequence ):
                      voice.speak( "You have reached the end. Goodbye." )
                      return
                  else:
                      openallure.ready  = False

            else:
               # invalid or final choice
               print "Something is wrong with the question sequence.  Please check it:"
               print seq.sequence
               return

        if not openallure.stated:
            if onAnswer == len(openallure.question[1])+1:
                openallure.stated = True
            else:
                # work through statement of question
                # this means speaking each part of the question and each of the answers
                # UNLESS the process is cut short by other events
                if onAnswer > 0 and onAnswer < len( openallure.question[ 1 ] ) + 1 :
                    answerText = openallure.question[ 1 ][ onAnswer-1 ]
                    if not answerText.startswith('[input]'):
                        # Check for answer with "A. "
                        if answerText[ 1:3 ] == '. ' :
                           voice.speak( answerText[ 3: ].strip() )
                        else:
                           voice.speak( answerText.strip() )
                        del answerText
                    onAnswer += 1

                if onText < len( openallure.question[ 0 ] ):
                    # speak the current part of the question
                    voice.speak( openallure.question[ 0 ][ onText ] )
                    # and move on to the next part (which needs to be displayed before being spoken)
                    onText += 1
                    # once all the parts of the question are done, start working through answers
                    if onText == len( openallure.question[ 0 ] ):
                       onAnswer = 1

# initialize speech recognition before entering main()
config = ConfigParser.RawConfigParser()
config.read( 'openallure.cfg' )
systemHasDragonfly = eval( config.get( 'Voice', 'systemHasDragonfly' ) )
systemHasEspeak    = eval( config.get( 'Voice', 'systemHasEspeak' ) )

_dictation = 0

openallure.voiceChoice = 0

def speak(phrase):
   #print phrase
   if systemHasDragonfly:
	   e = dragonfly.get_engine()
	   e.speak(phrase)
   if systemHasEspeak:
       os.system('espeak -s150 "' + phrase + '"')
   if not (systemHasDragonfly or systemHasEspeak):
       print phrase
       pygame.time.wait(500)

if systemHasDragonfly:
    import dragonfly
    from dragonfly import *

    e = dragonfly.get_engine()
    e.speak("Using dragonfly.")

    grammar = Grammar("openallure")

    class SpeakRule(CompoundRule):
        spec = "<text>"
        extras = [Dictation("text")]

        def _process_recognition(self, node, extras):
##            # stop reading
##            global _silence, choice, _dictation, on_question, question, sequence, _openallure.stated, _quit
##            _silence = 1

            openallure.stated = True

            if openallure.ready:
                # repeat voice recognition
                answer = " ".join(node.words())
                answer1 = node.words()[0]
                speak("You said %s!" % answer)

                if _dictation == 0:
                    # check for valid answer (see if words match)
                    onAnswer = 0
                    match = 0
                    for i in openallure.question[1]:
                        onAnswer += 1
                        #check against available answers - in lower case without punctuation
                        # and allow first part only (eg "Yes." in "Yes. I agree.")
                        # or first word
                        answer = answer.lower().strip('.')
                        if answer == i.lower().strip('.?!') or answer == i.lower().split('.')[0] or answer == i.lower().split()[0]:
                           openallure.voiceChoice = onAnswer
                           match = 1
                    if not match:
                        #check first word against number words
                        onAnswer = 0
                        for i in ["one","two","three","four","five","six"]:
                            onAnswer += 1
                            if answer1 == i or answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check first word against "choice" + number words
                        onAnswer = 0
                        for i in ["choice one","choice two","choice three","choice four","choice five","choice six"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check first word against "answer" + number words
                        onAnswer = 0
                        for i in ["answer one","answer two","answer three","answer four","answer five","answer six"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check first word against words similar to number words
                        onAnswer = 0
                        for i in ["won","to","tree","for","fife","sex"]:
                            onAnswer += 1
                            if answer1 == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against ordinal words
                        onAnswer = 0
                        for i in ["first","second","third","fourth","fifth","sixth"]:
                            onAnswer += 1
                            if answer1 == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against ordinal words + "choice"
                        onAnswer = 0
                        for i in ["first choice","second choice","third choice","fourth choice","fifth choice","sixth choice"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against ordinal words + "answer"
                        onAnswer = 0
                        for i in ["first answer","second answer","third answer","fourth answer","fifth answer","sixth answer"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against letter words
                        onAnswer = 0
                        for i in ["A.","B.","C.","D.","E.","F."]:
                            onAnswer += 1
                            if answer1 == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
    ##                if not match:
    ##                    #check against control words
    ##                    for i in ["next","next question","skip to next question"]:
    ##                       if answer == i:
    ##                          _silence = 1
    ##                          on_text = 0
    ##                          onAnswer = 0
    ##                          skip_response = 1
    ##
    ##                          # Choice is first non-zero entry in openallure.question[3]
    ##                          on_choice = 0
    ##                          for i in openallure.question[3]:
    ##                              on_choice += 1
    ##                              if not i == 0:
    ##                                  openallure.voiceChoice = on_choice
    ##                                  voice.speak("On question " + str(on_question + i))
    ##                                  break
    ##                          match = 1
    ##                if not match:
    ##                    for i in ["back","prior","previous","back up","back one","prior question","previous question"]:
    ##                       if answer == i:
    ##                          _silence = 1
    ##                          on_text = 0
    ##                          onAnswer = 0
    ##                          openallure.voiceChoice = -1
    ##                          if len(questions) > 0:
    ##                              voice.speak("Returning to question " + str(questions[-1]))
    ##                          else:
    ##                              on_question = 0
    ##                          match = 1
    ##                if not match:
    ##                    for i in ["quit now","exit now","i give up"]:
    ##                       if answer == i:
    ##                           _quit = 1
    ##                           match = 1

                    if not match:
                        # try plugging into currentString
                        openallure.currentString = answer
                        openallure.question[ 1 ][ choiceCount - 1 ] = openallure.currentString
##                        speak("Try again.")
    ##            else:
    ##                voice.speak("Thank you. Let's move on.")
    ##                on_question = on_question + 1
    ##                # avoid stepping past end of sequence
    ##                on_question = min(on_question,len(sequence)-1)
    ##                openallure.question = sequence[on_question]
    ##                build_question_text(openallure.question)
    ##                openallure.voiceChoice = 0
    ##                _dictation = 0
    ##            if match and verbose: print "dragonfly openallure.voiceChoice " + str(openallure.voiceChoice)
    ##                e.speak("dragonfly voice Choice " + str(openallure.voiceChoice))

    grammar.add_rule(SpeakRule())    # Add the top-level rule.
    grammar.load()                   # Load the grammar.



if __name__ == '__main__':
    main()
