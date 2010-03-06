"""
openallure.py

Voice-and-vision enabled dialog system

Project home at `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

__version__='0.1d4dev'

import ConfigParser

def main():
    """Initialization and event loop"""
    import logging
    import sequence
    import video
    import gesture
    import pygame
    import text
    import voice
    import ConfigParser
    import aiml
    import os

    global voiceChoice

    # provide instructions and other useful information (hide by elevating logging level:
    LEVELS = { 'debug'   : logging.DEBUG,
               'info'    : logging.INFO,
               'warning' : logging.WARNING,
               'error'   : logging.ERROR,
               'critical': logging.CRITICAL }

    print("\n\n   Open Allure. Voice-and-vision enabled dialog system.\n\n   F3 to Show webcam. F4 to Recalibrate. \n\n   F5 to Show pixels. Escape to quit.\n\n   Enjoy!\n\n")

    logging.basicConfig( level=logging.DEBUG )
    logging.info( "Open Allure Version: %s" % __version__ )
    logging.debug( "Pygame Version: %s" % pygame.__version__ )

    # initialize pyGame screen
    screenRect = pygame.rect.Rect( 0, 0, 640, 480 )
    pygame.init()
    screen = pygame.display.set_mode( screenRect.size )
    del screenRect

    # load initial sequence from url specified in openallure.cfg file
    config = ConfigParser.RawConfigParser()
    config.read( 'openallure.cfg' )
    url = config.get( 'Source', 'url' )
    backgroundColor = eval( config.get( 'Colors', 'background' ) )

    seq = sequence.Sequence( filename=url )
    logging.info( "Sequence Loaded with %s questions" % str( len( seq.sequence ) ) )
    #print seq.sequence

    # load initial AIML file
    k = aiml.Kernel()
    aiml = config.get( 'Source', 'aiml' )
    aimlLoadPattern = config.get( 'Source', 'aimlLoadPattern' )
    k.learn( aiml )
    AIMLResponse = k.respond( aimlLoadPattern )
    logging.info( "AIML %s" % (aiml + " " + AIMLResponse ) )

    # load browser command string
    browser = config.get( 'Browser', 'browser' )

    greenScreen = video.GreenScreen()
    vcp         = video.VideoCapturePlayer( processFunction=greenScreen.process )
    gesture     = gesture.Gesture()
    voice       = voice.Voice()

    margins     = [ 20, 20, 620, 460 ]
    text        = text.Text( margins )

    showFlag = False

    # start on first question of sequence
    # TODO: have parameter file track position in sequence at quit and resume there on restart
    onQuestion = 0

    # initialize mode flags
    # Has new question from sequence been prepared?
    ready = False
    # Has question been stated (read aloud)?
    stated = False
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
    currentString = ""


    # Greetings
    voice.speak( 'Hello' )

    while 1:

        if not ready:
            # prepare for question display
            question = seq.sequence[ onQuestion ]
            choiceCount, questionText, justQuestionText = text.buildQuestionText( question )

            textRegions = text.preRender( questionText[ choiceCount ] )

            # initialize pointers - no part of the question text and none of the answers
            # have been read aloud.  Note that question text is numbered from 0
            # while answers are numbered from 1.
            stated = False
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
            currentString = ''

            # clear screen of last question
            screen.fill( backgroundColor )
            greenScreen.calibrated = False
            greenScreen.backgrounds = []
            vcp.processruns = 0
            ready = True

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
               if event.key in range( pygame.K_1, pygame.K_6 ):
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

               # Allow space to silence reading of question unless there is an input (which might require a space)
               elif event.key == pygame.K_SPACE and not question[ 6 ][choiceCount - 1 ] == 1:
                    # Silence reading of question
                    stated = True
               elif event.key == pygame.K_RETURN:
                   # This takes last response (which can be input string)
                   answer = choiceCount - 1
                   choice = ( choiceCount, 0 )
               elif event.key == pygame.K_BACKSPACE and question[ 6 ][choiceCount - 1 ] == 1:
                   currentString = currentString[0:-1]
                   question[ 1 ][ choiceCount - 1 ] = currentString
                   questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + "\n" + currentString
                   screen.fill(backgroundColor)
               elif event.key <= 127 and question[ 6 ][choiceCount - 1 ] == 1:
                   mods = pygame.key.get_mods()
                   if mods & pygame.KMOD_SHIFT:
                       currentString += chr( event.key ).upper()
                   else:
                       currentString += chr( event.key )
                   question[ 1 ][ choiceCount - 1 ] = currentString
                   questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + "\n" + currentString
                   screen.fill(backgroundColor)

#        print voiceChoice
        if voiceChoice > 0:
            answer = voiceChoice - 1
            voiceChoice = 0

        if answer < 0 and ready:
            # check webcam
            processedImage = vcp.get_and_flip( show=showFlag )
            choice         = gesture.choiceSelected( processedImage, textRegions, margins )
            if showFlag:
                vcp.display.blit( processedImage, ( 0, 0 ) )
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
                #TODO: provide shortcut to go immediately to colorLevel=0 if choice[1] (number of selected boxes) is big enough
                if colorLevel == 0:
                    # choice has been highlighted long enough to actually be the desired selection
                    choiceMade = True
                    answer = choice[ 0 ] - 1
    ##                print question[1]
    ##                print choice[0]
                    voice.speak( "You selected " + question[ 1 ][ answer ] )
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

            text.paintText(screen,
                           justQuestionText, onText,
                           questionText,     onAnswer,
                           highlight,
                           stated,
                           choice,
                           colorLevel,colorLevels)
        elif not choice == ( - 1, 0 ):
            # respond to choice
            if len( currentString ):
                voice.speak("You entered " + currentString )
                # print answer, k.respond( currentString )
                # put response in a file for now
                filename = "aimlResponse.txt"
                f = open( filename, 'w')
                print k.respond( currentString )
                print k.respond( currentString ).replace( '\\n ', '\n' )
                f.write( k.respond( currentString ).replace( '\\n ', '\n' ) )
                f.close()

            # check whether a link is associated with this answer and, if so, follow it
            if question[ 5 ][ answer ]:
                os.system( browser + " " + question[ 5 ][ answer ] )

            #check that response exists for answer
            if answer < len( question[ 2 ] ) and (isinstance( question[ 2 ][ answer ], str ) or \
                                                  isinstance( question[ 2 ][ answer ], unicode)):
                  #speak response to answer
                  voice.speak(question[ 2 ][ answer ].strip())

            #check that next sequence exists as integer for answer
            if answer < len( question[ 3 ] ) and isinstance( question[ 3 ][ answer ], int ):
              #get new sequence or advance in sequence
              next = question[ 3 ][ answer ]
              if next == 88:
                  # voice.speak( "New source of questions" )
                  path = seq.path
                  #print "path is ", path
                  seq = sequence.Sequence( filename = question[ 4 ][ answer ], path = path )
                  onQuestion = 0
                  ready = False
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
                      ready  = False

            else:
               # invalid or final choice
               print "Something is wrong with the question sequence.  Please check it:"
               print seq.sequence
               return

        if not stated:
            if onAnswer == len(question[1])+1:
                stated = True
            else:
                # work through statement of question
                # this means speaking each part of the question and each of the answers
                # UNLESS the process is cut short by other events
                if onAnswer > 0 and onAnswer < len( question[ 1 ] ) + 1 :
                    answerText = question[ 1 ][ onAnswer-1 ]
                    if not answerText.startswith('[input]'):
                        # Check for answer with "A. "
                        if answerText[ 1:3 ] == '. ' :
                           voice.speak( answerText[ 3: ].strip() )
                        else:
                           voice.speak( answerText.strip() )
                        del answerText
                    onAnswer += 1

                if onText < len( question[ 0 ] ):
                    # speak the current part of the question
                    voice.speak( question[ 0 ][ onText ] )
                    # and move on to the next part (which needs to be displayed before being spoken)
                    onText += 1
                    # once all the parts of the question are done, start working through answers
                    if onText == len( question[ 0 ] ):
                       onAnswer = 1

# initialize speech recognition before entering main()
config = ConfigParser.RawConfigParser()
config.read( 'openallure.cfg' )
systemHasDragonfly = eval( config.get( 'Voice', 'systemHasDragonfly' ) )
systemHasEspeak    = eval( config.get( 'Voice', 'systemHasEspeak' ) )

_dictation = 0

voiceChoice = 0

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
    e.speak("Hello. Using dragonfly.")
    grammar = Grammar("openallure")

    class SpeakRule(CompoundRule):
        spec = "<text>"
        extras = [Dictation("text")]

        def _process_recognition(self, node, extras):
##            # stop reading
##            global _silence, choice, _dictation, on_question, question, sequence, _stated, _quit
##            _silence = 1
            global voiceChoice

            # repeat voice recognition
            answer = " ".join(node.words())
            answer1 = node.words()[0]
            speak("You said %s!" % answer)

            if _dictation == 0:
                # check for valid answer (see if words match)
                onAnswer = 0
                match = 0
##                for i in question[1]:
##                    onAnswer += 1
##                    #check against available answers - in lower case without punctuation
##                    # and allow first part only (eg "Yes." in "Yes. I agree.")
##                    # or first word
##                    answer = answer.lower().strip('.')
##                    if answer == i.lower().strip('.?!') or answer == i.lower().split('.')[0] or answer == i.lower().split()[0]:
##                       voiceChoice = onAnswer
##                       match = 1
                if not match:
                    #check first word against number words
                    onAnswer = 0
                    for i in ["one","two","three","four","five","six"]:
                        onAnswer += 1
                        if answer1 == i or answer == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check first word against "choice" + number words
                    onAnswer = 0
                    for i in ["choice one","choice two","choice three","choice four","choice five","choice six"]:
                        onAnswer += 1
                        if answer == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check first word against "answer" + number words
                    onAnswer = 0
                    for i in ["answer one","answer two","answer three","answer four","answer five","answer six"]:
                        onAnswer += 1
                        if answer == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check first word against words similar to number words
                    onAnswer = 0
                    for i in ["won","to","tree","for","fife","sex"]:
                        onAnswer += 1
                        if answer1 == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check against ordinal words
                    onAnswer = 0
                    for i in ["first","second","third","fourth","fifth","sixth"]:
                        onAnswer += 1
                        if answer1 == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check against ordinal words + "choice"
                    onAnswer = 0
                    for i in ["first choice","second choice","third choice","fourth choice","fifth choice","sixth choice"]:
                        onAnswer += 1
                        if answer == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check against ordinal words + "answer"
                    onAnswer = 0
                    for i in ["first answer","second answer","third answer","fourth answer","fifth answer","sixth answer"]:
                        onAnswer += 1
                        if answer == i:
                           voiceChoice = onAnswer
                           match = 1
                if not match:
                    #check against letter words
                    onAnswer = 0
                    for i in ["A.","B.","C.","D.","E.","F."]:
                        onAnswer += 1
                        if answer1 == i:
                           voiceChoice = onAnswer
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
##                          # Choice is first non-zero entry in question[3]
##                          on_choice = 0
##                          for i in question[3]:
##                              on_choice += 1
##                              if not i == 0:
##                                  voiceChoice = on_choice
##                                  speak("On question " + str(on_question + i))
##                                  break
##                          match = 1
##                if not match:
##                    for i in ["back","prior","previous","back up","back one","prior question","previous question"]:
##                       if answer == i:
##                          _silence = 1
##                          on_text = 0
##                          onAnswer = 0
##                          voiceChoice = -1
##                          if len(questions) > 0:
##                              speak("Returning to question " + str(questions[-1]))
##                          else:
##                              on_question = 0
##                          match = 1
##                if not match:
##                    for i in ["quit now","exit now","i give up"]:
##                       if answer == i:
##                           _quit = 1
##                           match = 1

                if not match:
                    speak("Try again.")
##            else:
##                speak("Thank you. Let's move on.")
##                on_question = on_question + 1
##                # avoid stepping past end of sequence
##                on_question = min(on_question,len(sequence)-1)
##                question = sequence[on_question]
##                build_question_text(question)
##                voiceChoice = 0
##                _dictation = 0
##            if match and verbose: print "dragonfly voiceChoice " + str(voiceChoice)
                e.speak("dragonfly voice Choice " + str(voiceChoice))

    grammar.add_rule(SpeakRule())    # Add the top-level rule.
    grammar.load()                   # Load the grammar.



if __name__ == '__main__':
    main()
