"""
openallure.py

Voice-and-vision enabled dialog system

Project home at `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

__version__ = '0.1d29dev'

# Standard Python modules
import ConfigParser
import os
import re
import string
import subprocess
import sys
import time
import webbrowser

# 3rd Party modules
# note: nltk is used by chat.py
import pygame
from buzhug import Base

# Import from Open Allure DS modules
from qsequence import QSequence
from oagraph import oagraph, oaMetaGraph, wrapWords
from voice import Voice
from text import OpenAllureText
from chat import Chat, responses, reflections
#from chat import reflections
#from util import reflections


WELCOME_TEXT = u"""
   Welcome to the Open Allure Dialog System.

   Escape to quit.
"""


class OpenAllure(object):
    def __init__(self):
        self.__version__ = __version__
        self.currentString = u''
        self.question = []
        self.ready = False
        self.stated = False
        self.statedq = -1
        self.voiceChoice = -1

openallure = OpenAllure()

def inRegion(region, y):
    if y >= region[1] and y <= region[3]:
        return 1
    else:
        return 0

def main():
    """Initialization and event loop"""

    # provide instructions and other useful information

    # initialize pyGame screen
    textRect = pygame.rect.Rect(0, 0, 640, 480)
    screenRect = pygame.rect.Rect(0, 0, 640, 480)
    pygame.init()
    pygame.display.set_caption(u"Open Allure")
    screen = pygame.display.set_mode(screenRect.size)
    if sys.platform != 'darwin':
        pygame.scrap.init()

    # load initial question sequence from url specified in openallure.cfg file
    config = ConfigParser.RawConfigParser()
    config.read('openallure.cfg')
    url = unicode(config.get('Source', 'url'))
    if len(sys.argv) > 1 and 0 != len(sys.argv[1]):
        url = unicode(sys.argv[1])
    backgroundColor = eval(config.get('Colors', 'background'))
    seq = QSequence(filename = url)

    # open database to track progress

    oadb = config.get('Data', 'oadb')
    try:
        openallure.db = Base(oadb).open()
        record_id = openallure.db.insert(time = time.time(), \
        url = url, q = 0)
    except IOError:
        openallure.db = Base(oadb)
        openallure.db.create(('time',float), ('url',unicode), \
        ('q',int), ('a',int), ('cmd',unicode))
        record_id = openallure.db.insert(time = time.time(), \
        url = url, q = 0)

    # read configuration options
    delayTime = int(config.get('Options', 'delayTime'))
    openallure.allowNext = int(config.get('Options', 'allowNext'))

    # initialize chatbot
    openallure_chatbot = Chat(responses, reflections)
    chatHistory = []
    onChatHistory = -1

    # load browser command line strings and select appropriate one
    darwinBrowser = config.get('Browser', 'darwinBrowser')
    windowsBrowser = config.get('Browser', 'windowsBrowser')
    if sys.platform == 'darwin':
        browser = darwinBrowser
    else:
        browser = windowsBrowser
    # track when Open Allure has gained mouse focus
    openallure.gain = 1

    voice = Voice()

    margins = eval(config.get('Font', 'margins'))
    text = OpenAllureText(margins)

    # start on first question of sequence
    # TODO: have parameter file track position in sequence at quit
    # and resume there on restart
    openallure.onQuestion = 0

    # initialize mode flags
    # Has new question from sequence been prepared?
    openallure.ready = False
    # Has question been openallure.stated (read aloud)?
    openallure.stated = False
    # Which question in sequence has been read alond (to avoid re-reading it)?
    openallure.statedq = -1
    # What choice (if any) has been highlighted by gesture or keyboard?
    highlight = 0
    # When was the statement of the question complete?
    delayStartTime = 0
    # Do we have an answer? what number is it (with 0 being first answer)?
    answer = -1
    # What questions have been shown (list)?
    openallure.questions = []
    # What has been typed in so far
    openallure.currentString = u""

    # Subprocesses
    graphViz = None
    openallure.showResponses = eval(config.get('GraphViz', 'showResponses'))
    openallure.showText = eval(config.get('GraphViz', 'showText'))
    openallure.showLabels = eval(config.get('GraphViz', 'showLabels'))
    graphVizPath = config.get('GraphViz', 'path')
    #if eval(config.get('GraphViz', 'autoStart')):
    #    oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
    #    graphViz = subprocess.Popen([graphVizPath,'oagraph.dot'])

    browserLink = None

    # Greetings
    #voice.speak('Hello')

    # Post arrival record
    record_id = openallure.db.insert(time = time.time(), \
                url = url, q = openallure.onQuestion, \
                a = answer)

    print WELCOME_TEXT
    runFlag = True;
    while runFlag:

        if not openallure.ready:
            # prepare for question display
            openallure.question = seq.sequence[openallure.onQuestion]
            choiceCount, \
            questionText, \
            justQuestionText = text.buildQuestionText(openallure.question)
            if graphViz:
                # Create .dot file for new sequence
                graphViz.kill()
                oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
                graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])

            textRegions = text.writewrap(None, text.font, text.boundingRectangle, text.unreadColor, questionText[-1])

            # initialize pointers - no part of the question text
            # and none of the answers have been read aloud.
            # Note that question text is numbered from 0
            # while answers are numbered from 1.
            next = 0
            onAnswer = 0
            onText = 0
            openallure.stated = False

            # initialize selections - nothing has been highlighted
            # or previously selected as an answer
            answer = -1
            choice = (- 1, 0)
            colorLevel = colorLevels = 12
            eliminate = []
            highlight = 0

            # initialize typed input
            openallure.currentString = u''

            # clear screen of last question
            screen.fill(backgroundColor, rect=textRect)

            # wait for prior speaking to finish
            if voice.pid_status > 0:
                try:
                    os.waitpid(voice.pid_status, 0)[1]
                except:
                    pass
                voice.pid_status = 0
            openallure.ready = True

            # clear any previous response
            nltkResponse = ''

            # start with gain
            openallure.gain = 1

        # make sure currentString has been added to questionText
        if openallure.currentString:
            questionText[choiceCount] = questionText[choiceCount - 1] + \
                                          "\n" + openallure.currentString

        # get keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT   \
               or (event.type == pygame.KEYDOWN and    \
                   event.key == pygame.K_ESCAPE):
 #               if graphViz:
 #                   graphViz.kill()
                runFlag = False

            # Trap and quit on Ctrl + C
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_c and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                return

            # Trap Ctrl + I to force input
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_i and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                # TODO: This kills the entire current sequence. Build a way to back up to it.
                seq.inputs = [u"Input",
                         u"[input];;"]
                seq.sequence = seq.regroup(seq.inputs, \
                seq.classify(seq.inputs))
                openallure.onQuestion = 0
                url = u'[input]'
                record_id = openallure.db.insert(time = time.time(), \
                url = url, q = 0)
                openallure.ready = False

            # Trap and paste clipboard on Ctrl + V for Mac
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_v and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                if sys.platform == 'darwin':
                    os.system('pbpaste > clipboard')
                    clipboard = open('clipboard').readlines()
                    if clipboard[0].startswith(u"http://") or \
                       clipboard[0].find(u"http://"):
                        openallure.currentString += clipboard[0]
                else:
                    clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clipboard.startswith(u"http://") or \
                       clipboard.find(u"http://"):
                        openallure.currentString += clipboard

            # Trap Ctrl + - (minus) to decrease font size
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_MINUS and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                text.fontSize -= 5
                text.font = pygame.font.SysFont( text.fontName, \
                text.fontSize )

            # Trap Ctrl + + (plus) to increase font size
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_EQUALS and
                  pygame.key.get_mods() & (pygame.KMOD_CTRL |
                  pygame.KMOD_CTRL)):
                text.fontSize += 5
                text.font = pygame.font.SysFont( text.fontName, \
                text.fontSize )

            # Trap Ctrl + R to refresh from url without changing question number
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_r and
                  pygame.key.get_mods() & (pygame.KMOD_CTRL |
                  pygame.KMOD_CTRL)):
                  seq = QSequence(filename = url)
                  openallure.ready = False

            # Define toggle keys and capture string inputs
            elif event.type == pygame.KEYDOWN:
                # Keys 1 through 6 select choices 1 through 6
                if event.key in range(pygame.K_1, pygame.K_6) and \
                    (not openallure.question[6][choiceCount - 1] == 1 or
                    (openallure.question[6][choiceCount - 1] == 1 and
                    openallure.currentString == u'')):
                        answer = event.key - pygame.K_1
                        if answer < choiceCount:
                            # Record choice along with destination, if any
                            record_id = openallure.db.insert(time = time.time(), \
                            url = url, q = openallure.onQuestion, \
                            a = answer, cmd = openallure.question[4][answer])
                            if graphViz:
                                graphViz.kill()
                                oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
                                graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])
                            choice = (answer + 1, 0)
                            colorLevel = 0
                            # Update screen to reflect choice
                            text.paintText(screen,
                                           justQuestionText, onText,
                                           questionText, onAnswer,
                                           highlight,
                                           openallure.stated,
                                           choice,
                                           colorLevel, colorLevels)
                            pygame.display.flip()
                        else:
                            answer = -1

                elif event.key == pygame.K_F4:
                    greenScreen.calibrated = False
                elif event.key == pygame.K_F6:
                    # reveal all the attributes of openallure
                    print "\nCurrent values of openallure object variables:\n"
                    for item in openallure.__dict__:
                        print item + ":", openallure.__dict__[item]
                    # drop into interpreter for debugging
                    print "\n   Press Ctrl+D to close console and resume. " + \
                    "Enter exit() to exit.\n"
                    import code
                    code.interact(local=locals())

                # Allow space to silence reading of question
                # unless there is an input (which might require a space)
                elif event.key == pygame.K_SPACE and \
                not openallure.question[6][choiceCount - 1] == 1:
                    # Silence reading of question
                    openallure.stated = True
                elif event.key == pygame.K_RIGHT and openallure.allowNext:
                    # Choice is first non-zero entry
                    # in openallure.question[3]
                    onChoice = 0
                    for i in openallure.question[3]:
                        onChoice += 1
                        if not i == 0:
                            openallure.voiceChoice = onChoice
                            break
                    del onChoice

                elif event.key == pygame.K_LEFT:
                    if len(openallure.questions) > 0:
                        openallure.onQuestion = openallure.questions.pop()
                        openallure.ready = False
                    else:
                        openallure.onQuestion = 0

                elif event.key == pygame.K_UP:
                    if len(chatHistory) > 0 and onChatHistory > -1:
                        onChatHistory -= 1
                        openallure.currentString = chatHistory[onChatHistory]
                elif event.key == pygame.K_DOWN:
                    if len(chatHistory) > 0 and \
                    onChatHistory < len(chatHistory) - 1:
                        onChatHistory += 1
                        openallure.currentString = chatHistory[onChatHistory]

                elif event.key == pygame.K_RETURN:
                    if openallure.currentString:
                        # add to history
                        chatHistory.append(openallure.currentString)
                        onChatHistory = len(chatHistory)
                        # record input
                        record_id = openallure.db.insert(time = time.time(), \
                        url = unicode(url), q = openallure.onQuestion, \
                        a = answer, cmd = openallure.currentString)
                        nltkResponse, \
                        nltkType, \
                        nltkName = \
                        openallure_chatbot.respond(openallure.currentString)

                        # Act on commands
                        if nltkType == 'quit':
                            #TODO: Make this more polite
                            if graphViz:
                                graphViz.kill()
                            raise SystemExit

                        if nltkType == 'return':
                            # Find first different sequence in db, walking back
                            for id in range(record_id - 1,-1,-1):
                                try:
                                    record = openallure.db[id]
                                    if not record.url in (url, u'nltkResponse.txt'):
                                        seq = QSequence(filename = record.url, \
                                                path = path, \
                                                nltkResponse = nltkResponse)
                                        url = record.url
                                        openallure.onQuestion = record.q
                                        openallure.ready = False
                                        if graphViz:
                                            # Fall through into graphing
                                            nltkType = 'graph'
                                            nltkName = 'show'
                                        break
                                except:
                                    pass
                            nltkResponse = u''
                            openallure.currentString = u''

                        if nltkType == 'open':
                            # Reset stated question pointer for new sequence
                            openallure.statedq = -1
                            path = seq.path
                            linkStart = nltkResponse.find(u'[')
                            linkEnd = nltkResponse.find(u']', linkStart)
                            url = nltkResponse[linkStart + 1:linkEnd]
                            seq = QSequence(filename = url,
                                            path = path,
                                            nltkResponse = nltkResponse)
                            record_id = openallure.db.insert(time = time.time(), \
                            url = unicode(url), q = 0)
                            openallure.onQuestion = 0
                            openallure.ready = False
                            if graphViz:
                                # Fall through into graphing
                                nltkType = 'graph'
                                nltkName = 'show'
                            nltkResponse = u''
                            openallure.currentString = u''

                        if nltkType == 'show':
                            # use open (Mac only) to view source
                            if sys.platform == 'darwin':
                                # Find first non-[input] sequence in db, walking back
                                for id in range(record_id - 1,-1,-1):
                                    record = openallure.db[id]
                                    print record
                                    if record.url.find('.txt') > 0 or \
                                       record.url.find('http:') == 0 :
                                        if not record.url == 'nltkResponse.txt':
                                            url = record.url
                                            print url
                                            break
                                os.system("open "+url)

                        if nltkType == 'graph':
                            # Commands which change graph display
                            if nltkName == 'hideText':
                                openallure.showText = False
                            elif nltkName == 'showText':
                                openallure.showText = True
                            elif nltkName == 'showResp':
                                openallure.showResponses = True
                            elif nltkName == 'hideResp':
                                openallure.showResponses = False
                            elif nltkName == 'showLabels':
                                openallure.showLabels = True
                            elif nltkName == 'hideLabels':
                                openallure.showLabels = False
                            elif nltkName == 'hide':
                                if graphViz:
                                    graphViz.kill()
                                graphViz = None
                            elif nltkName == 'reset':
                                records = [record for record in openallure.db]
                                openallure.db.delete(records)
                                openallure.db.cleanup()

                            # Make .dot file and display graph
                            if nltkName in ('show', \
                            'hideText', 'showText', \
                            'showResp', 'hideResp', \
                            'meta', 'reset'):
                                if nltkName == 'meta':
                                    # Crete .dot meta file
                                    oaMetaGraph(openallure.db)
                                else:
                                    # Create .dot file for one sequence in response to command
                                    oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
                                # Display graph
                                if graphViz:
                                    graphViz.kill()
                                    oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
                                graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])
                            if nltkName == 'list':
                                for record in (record for record in openallure.db):
                                    if record.cmd:
                                        print(record.__id__, str(record.url), record.q, record.a, str(record.cmd))
                                    elif not record.a == None:
                                        print(record.__id__, str(record.url), record.q, record.a)
                                    else:
                                        print(record.__id__, str(record.url), record.q)
                            nltkResponse = u''
                            openallure.currentString = u''

                        # if nltkResponse is one line containing a semicolon,
                        # replace the semicolon with \n
                        if nltkResponse.find('\n') == -1:
                            nltkResponse = nltkResponse.replace(';', '\n')

                        if nltkResponse:
                            answer = choiceCount - 1
                            choice = (choiceCount, 0)
                    else:
                        # This takes last response
                        answer = choiceCount - 1
                        choice = (choiceCount, 0)
                elif event.key == pygame.K_BACKSPACE and \
                openallure.question[6][choiceCount - 1] == 1:
                    openallure.currentString = openallure.currentString[0:-1]
                    openallure.question[1][choiceCount - 1] = \
                    openallure.currentString
                    questionText[choiceCount] = \
                    questionText[choiceCount - 1] + \
                    u"\n" + openallure.currentString
                    screen.fill(backgroundColor, rect=textRect)
                elif event.key <= 127 and \
                openallure.question[6][choiceCount - 1] == 1:
                    # print event.key
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        if event.key in range(47, 60):
                            openallure.currentString += \
                            (u'?', u')', u'!', u'@', u'#', u'$', u'%', u'^', \
                            u'&', u'*', u'(', u'', u':')[range(47, 60).index(event.key)]
                        elif event.key == 45:
                            openallure.currentString += u"_"
                        elif event.key == 61:
                            openallure.currentString += u"+"
                        elif event.key == 96:
                            openallure.currentString += u"~"
                        else:
                            openallure.currentString += unicode(chr(event.key).upper())
                    else:
                        openallure.currentString += unicode(chr(event.key))
                    openallure.question[1][choiceCount - 1] = \
                    openallure.currentString
                    questionText[choiceCount] = \
                    questionText[choiceCount - 1] + \
                    u"\n" + openallure.currentString
                    screen.fill(backgroundColor, rect=textRect)

        # check for automatic page turn
        if openallure.ready and \
           openallure.stated == True and \
           not openallure.currentString and \
           openallure.question[1][choiceCount - 1] == u'[next]' and \
           pygame.time.get_ticks() - delayStartTime > delayTime:
            # This takes last response
            answer = choiceCount - 1
            choice = (choiceCount, 0)

        if openallure.statedq == openallure.onQuestion:
            openallure.stated = True

        if openallure.ready and not openallure.stated:
            # work through statement of question
            # speaking each part of the question and each of the answers
            # (unless the process is cut short by other events)
            if onText == 0:
                screen.fill(backgroundColor, rect=textRect)
                pygame.display.flip()

            # Stop when onAnswer pointer is beyond length of answer list
            if onAnswer > len(openallure.question[1]):
                openallure.stated = True
                openallure.statedq = openallure.onQuestion

            else:
                # Speak each answer
                #(but only after speaking the full question below)
                if onAnswer > 0 and onAnswer < len(openallure.question[1]) + 1:
                    answerText = openallure.question[1][onAnswer - 1]
                    if not (answerText.startswith('[input]') or
                             answerText.startswith('[next]') or
                             answerText.endswith( '...]' ) or
                             answerText.endswith( '...' )):
                        if len(answerText) > 0:
                            # Check for answer with "A. "
                            if answerText[1:3] == '. ':
                                voice.speak(answerText[3:].strip())
                            else:
                                voice.speak(answerText.strip())
                        del answerText

                # Speak each part of the question using onText pointer
                # to step through parts of question list
                if onText < len(openallure.question[0]):
                    if not (openallure.question[0][onText].endswith( '...' )):
                        if len(openallure.question[0][onText]) > 0:
                            # speak the current part of the question
                            voice.speak(openallure.question[0][onText])

        if answer < 0 and openallure.ready:

            # Trap mouse click on text region
            textRegions = text.writewrap(None, text.font, text.boundingRectangle, text.unreadColor, questionText[-1])
            (mousex, mousey) = pygame.mouse.get_pos()
            (lbutton, mbutton, rbutton) = pygame.mouse.get_pressed()
            regions = [inRegion(region, mousey) for region in textRegions]
            if 1 in regions:
               onRegion = regions.index(1)
            else:
               onRegion = 0
            #print mousex, mousey, lbutton, regions, onRegion
            if onRegion > 0:
                if lbutton:
                    answer = onRegion - 1
                    if answer < choiceCount:
                        record_id = openallure.db.insert(time = time.time(), \
                        url = url, q = openallure.onQuestion, \
                        a = answer)
                        if graphViz and openallure.question[3][answer] == 0:
                            # Create .dot file for one sequence in response to answer in place
                            graphViz.kill()
                            oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
                            graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])
                        choice = (answer + 1, 0)
                        colorLevel = 0
                        # Update screen to reflect choice
#                         text.paintText(screen,
#                                        justQuestionText, onText,
#                                        questionText, onAnswer,
#                                        highlight,
#                                        openallure.stated,
#                                        choice,
#                                        colorLevel, colorLevels)
#                         pygame.display.flip()
                    else:
                        answer = -1
                else:
                    highlight = onRegion
                    # Update screen to reflect highlight
#                     text.paintText(screen,
#                                    justQuestionText, onText,
#                                    questionText, onAnswer,
#                                    highlight,
#                                    openallure.stated,
#                                    choice,
#                                    colorLevel, colorLevels)
#                     pygame.display.flip()
                    colorLevel -= 1
                    colorLevel = max(colorLevel, 0)
            else:
                highlight = 0
                colorLevel = colorLevels

            # block non-choices
            if choice[0] < 0 or choice[0] > len(questionText) - 1:
                choice = (-1, 0)
            #print choice, highlight

            screen.fill(backgroundColor, rect=textRect)
            text.paintText(screen,
                           justQuestionText, onText,
                           questionText, onAnswer,
                           highlight,
                           openallure.stated,
                           choice,
                           colorLevel, colorLevels)
            # and move on to the next part
            # (which needs to be displayed while being spoken)
            onText += 1
            # once all the parts of the question are done,
            # start working through answers
            if onAnswer > 0:
                onAnswer += 1
            if onText == len(openallure.question[0]):
                onAnswer = 1
                # Take note of time for automatic page turns
                delayStartTime = pygame.time.get_ticks()

            pygame.display.flip()

        elif not choice == (- 1, 0) and openallure.ready:

            openallure.stated = True

            # respond to choice when something has been typed and entered
            if openallure.currentString:
                if len(nltkResponse) == 0:
                    choice = (-1, 0)
                    answer = -1
                    voice.speak("Try again")
                else:
                    voice.speak(u"You entered " + openallure.currentString)
                # Reset string
                openallure.currentString = u''

            # check whether a link is associated with this answer and,
            # if so, follow it
            if len(openallure.question[5]) and openallure.question[5][answer]:
                webbrowser.open_new_tab(openallure.question[5][answer])
                openallure.gain = 0
                while not openallure.gain:
                    for event in pygame.event.get():
                        if event.type == pygame.ACTIVEEVENT:
                            openallure.gain = event.gain

            #check that response exists for answer
            if len(openallure.question[2]) and \
               answer < len(openallure.question[2]) and \
                (isinstance(openallure.question[2][answer], str) or \
                isinstance(openallure.question[2][answer], unicode)):
                    #speak response to answer
                    voice.speak(openallure.question[2][answer].strip())

            #check that next sequence exists as integer for answer
            if len(openallure.question[3]) and \
            answer < len(openallure.question[3]) and \
            isinstance(openallure.question[3][answer], int):
                #get new sequence or advance in sequence
                next = openallure.question[3][answer]
                if not openallure.question[4][answer] == '' and \
                not openallure.question[1][answer] == u'[next]':
                    # speak("New source of questions")
                    # Reset stated question pointer for new sequence
                    openallure.statedq = -1
                    path = seq.path
                    #print "path is ", path
                    url = openallure.question[4][answer]
                    seq = QSequence(filename = url,
                                    path = path,
                                    nltkResponse = nltkResponse)
                    record_id = openallure.db.insert(time = time.time(), \
                    url = unicode(url), q = 0)
                    openallure.onQuestion = 0
                    openallure.questions = []
                    openallure.ready = False
                else:
                    # Add last question to stack (if not duplicate) and move on
                    if next > 0:
                        openallure.questions.append(openallure.onQuestion)
                        openallure.onQuestion = openallure.onQuestion + next

                    # Try to pop question off stack if moving back one
                    elif next == -1:
                        for i in range(1, 1 - next):
                            if len(openallure.questions) > 0:
                                openallure.onQuestion = \
                                openallure.questions.pop()
                            else:
                                openallure.onQuestion = 0
                                
                    elif next < 0:
                        openallure.onQuestion = max( 0, openallure.onQuestion + next )
                        
                    record_id = openallure.db.insert(time = time.time(), \
                    url = url, q = openallure.onQuestion)

                    # Quit if advance goes beyond end of sequence
                    if openallure.onQuestion >= len(seq.sequence):
                        voice.speak("You have reached the end. Goodbye.")
                        return
                    else:
                        openallure.ready = False

##            else:
##               # invalid or final choice
##               print "Something is wrong with the question sequence."
##               print seq.sequence
##               return
##
### initialize speech recognition before entering main()
##config = ConfigParser.RawConfigParser()
##config.read('openallure.cfg')
##useDragonfly = eval(config.get('Voice', 'useDragonfly'))
##useEspeak = eval(config.get('Voice', 'useEspeak'))
##
##def speak(phrase):
##    #print phrase
##    if useDragonfly:
##        e = dragonfly.get_engine()
##        e.speak(phrase)
##    if useEspeak:
##        os.system('espeak -s150 "' + phrase + '"')
##    if not (useDragonfly or useEspeak):
##        print phrase
##        pygame.time.wait(500)

if __name__ == '__main__':
    main()
