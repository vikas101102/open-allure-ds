"""
openallure.py

Voice-and-vision enabled dialog system

Project home at `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

__version__='0.1d0dev'

def main():
    """Initialization and event loop"""
    import logging
    import sequence
    import video
    import gesture
    import pygame
    import text
    import voice

    # provide instructions and other useful information (hide by elevating logging level:
    LEVELS = {'debug'   : logging.DEBUG,
              'info'    : logging.INFO,
              'warning' : logging.WARNING,
              'error'   : logging.ERROR,
              'critical': logging.CRITICAL}

    print("\n\n   Open Allure. R to Recalibrate. Escape to quit.\n\n   Enjoy!\n\n")

    logging.basicConfig(level=logging.DEBUG)
    logging.info(" Open Allure Version: %s" % __version__)
    logging.debug("Pygame Version: %s" % pygame.__version__)

    # initialize pyGame screen
    screenRect = pygame.rect.Rect(0, 0, 640, 480)
    pygame.init()
    screen = pygame.display.set_mode(screenRect.size)
    del screenRect

    seq = sequence.Sequence(filename='test.txt')
    logging.info(" Sequence Loaded with %s questions" % str(len(seq.sequence)))
    #print seq.sequence

    greenScreen = video.GreenScreen()
    vcp         = video.VideoCapturePlayer(processFunction=greenScreen.process)
    gesture     = gesture.Gesture()
    voice       = voice.Voice()

    margins     = [20,20,620,460]
    text        = text.Text(margins)

    showFlag = False

    # start on first question of sequence
    # TODO: have parameter file track position in sequence at quit and resume there on restart
    onQuestion = 0
    #pick = 0
    #print margins
    #print margins[0]

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


    # Greetings
    voice.speak('Hello')

    while 1:

        if not ready:
            # prepare for question display
            question = seq.sequence[onQuestion]
            choiceCount, questionText, justQuestionText = text.buildQuestionText(question)
            #print choiceCount, questionText, justQuestionText
            #print questionText[choiceCount]
            choices = text.preRender(questionText[choiceCount])

            #print choices
            #break
            # initialize pointers - no part of the question text and none of the answers have been read aloud
            onText   = 0
            onAnswer = 0
            highlight= 0
            ready    = True
        if not stated:
            # work through statement of question
            # this means speaking each part of the question and each of the answers
            # UNLESS the process is cut short by other events
            while onText < len(justQuestionText):
                voice.speak(justQuestionText[onText])
                onText += 1
            while onAnswer < len(question[1]):
                answerText = question[1][onAnswer]
                # Check for answer with "A. "
                if answerText[1:3] == '. ':
                   voice.speak(answerText[3:].strip())
                else:
                   voice.speak(answerText.strip())
                del answerText
                onAnswer += 1
                if onAnswer == len(question[1]): stated = True

        # get keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT   \
               or (event.type == pygame.KEYDOWN and    \
                   event.key == pygame.K_ESCAPE):
                return
# TODO
            if event.type == pygame.KEYDOWN and \
               event.key == pygame.K_s:
                    screen.blit(arena.background, (0, 0))
                    pygame.display.update()
                    showFlag = not showFlag
            if event.type == pygame.KEYDOWN and \
               event.key == pygame.K_r:
                    greenScreen.calibrated = False

        if answer < 0:
            # check webcam
            processedImage = vcp.get_and_flip(show=showFlag)
            choice         = gesture.choiceSelected(processedImage,choices)
            # block non-choices
            if choice[0] < 0 or choice[0] > len(questionText)-1:
                choice = (-1,0)
            #print choice, highlight

            # adjust highlight and colorLevel
            if highlight > 0 and highlight == choice[0]:
                # choice was previously highlighted. Find out how long.
                dwellTime = pygame.time.get_ticks() - choiceStartTime
                #if choice[0] > 0: print choice, highlight, colorLevel, dwellTime
                # print dwellTime
                # lower color level to 0
                colorLevel = colorLevels - int(dwellTime/colorLevelStepTime)
                colorLevel = max(0, colorLevel)
                #TODO: provide shortcut to go immediately to colorLevel=0 if choice[1] (number of selected boxes) is big enough
                if colorLevel == 0:
                    # choice has been highlighted long enough to actually be the desired selection
                    choiceMade = True
                    answer = choice[0]-1
    ##                print question[1]
    ##                print choice[0]
                    voice.speak("You selected " + question[1][answer])
                    highlight = 0
                else:
                    # block a choice that has not been highlighted long enough
                    choice = (-1,0)
            else:
                # new choice or no choice
                highlight      = min(choice[0],choiceCount)
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
        else:
            # respond to choice
            #check that response exists for answer
            if len(question[2]) >= answer and isinstance(question[2][answer],str):
                  #speak response to answer
                  voice.speak(question[2][answer].strip())

            #check that next sequence exists as integer for answer
            if answer < len(question[3]) and isinstance(question[3][answer],int):
              #advance in sequence
              next = question[3][answer]
              if next == 99:
                  voice.speak("Taking dictation")
                  #TODO
              else:
                  # Add last question to stack and move on
                  if next > 0:
                     questions.append(onQuestion)
                     onQuestion = onQuestion + next

                  # Try to pop question off stack if moving back
                  elif next < 0:
                    for i in range(1,1-next):
                           if len(questions) > 0:
                                        onQuestion = questions.pop()
                           else:
                                        onQuestion = 0

                  # Quit if advance goes beyond end of sequence
                  if onQuestion >= len(seq.sequence):
                      voice.speak("You have reached the end. Goodbye.")
                      return
                  else:
                      ready  = False
                      stated = False
                      choice = (-1,0)
                      answer = -1

            else:
               # invalid or final choice
               print "Something is wrong with question sequence.  Please check."
               return

if __name__ == '__main__':
    main()