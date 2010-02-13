"""
text.py
a component of openallure.py

Collection of functions for rendering text

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

import pygame
pygame.font.init()

class Text( object ):

    def __init__( self, margins ):

        self.font = pygame.font.SysFont( "default", 50 )

        self.boundingRectangle = pygame.Rect( margins )

        # name colors
        self.black = ( 0, 0, 0 )
        self.gray = ( 200, 200, 200 )
        self.white = ( 255, 255, 255 )
        self.red = ( 255, 0, 0 )
        self.blue = ( 0, 255, 0 )
        self.green = ( 0, 0, 255 )
        self.yellow = ( 255, 255, 0 )
        self.purple = ( 255, 0, 255 )

        # put colors on things
        # TODO: put these in parameter file
        self.unreadColor = self.white
        self.readColor = self.gray
        self.selectedColor = self.red
        self.highlightColor = self.yellow

    def buildQuestionText( self, question ):
        """
Prepare text of question and answers for display and reading aloud::

   questionText[0] is question
   questionText[1] is question + answer 1
   questionText[2] is question + answer 1 + answer 2
   etc.

   justQuestionText[0] is first (perhaps only) part of question
   justQuestionText[1] is next part of question
   etc.

   choiceCount tells how may answers there are

        """
        questionText = [""]
        questionText[0] = " ".join( question[0] ) + "\n"
        choiceCount = 0
        for text in question[1]:
            questionText.append( questionText[choiceCount] + "\n" + text )
            choiceCount += 1
        #   speak(str(choiceCount) + " found")

        # build just question in pieces (if any)
        justQuestionText = [""]
        textCount = 0
        for text in question[0]:
            justQuestionText.append( justQuestionText[textCount] + text + " " )
            textCount += 1
        justQuestionText = justQuestionText[1:]

        return choiceCount, questionText, justQuestionText

    def writewrap( self, s, font, rect, color, text ):
     """write wrapped text

     Copied from PyGame Utilities
     """
     r, c, txt = rect, color, text
     txt = txt.replace( "\t", "        " )
     i = font.render( " ", 1, c )
     sw, sh = i.get_width(), i.get_height()
     y = r.top
     for sentence in txt.split( "\n" ):
         x = r.left
         for word in sentence.split( " " ):
             i = font.render( word, 1, c )
             iw, ih = i.get_width(), i.get_height()
             if x + iw > r.right: x, y = r.left, y + sh
             s.blit( i, ( x, y ) )
             x += iw + sw
         y += sh

    def preRender( self, questionText, screenWidth=640, rightMargin=20 ):
        """
        Pre-render text to find regions where it will be placed within screen with **screenWidth** and right margin of **rightMargin**
        """
        space = self.font.render( " ", 1, self.black )
        sw, sh = space.get_width(), space.get_height()
        del space

        rightHandLimit = screenWidth - rightMargin

        # choices collects (upper left x y, lower right x y) coordinates of question (choice 0) and answers (choice 1, 2, ...)
        choices = []

        # starting x, y track upper left corner
        starting_x = starting_y = 0

        # x, y track lower right corner
        x = y = 0

        for sentence in questionText.split( "\n" ):
            for word in sentence.split( " " ):
                rendered_word = self.font.render( word, 1, self.black )
                rww, rwh = rendered_word.get_width(), rendered_word.get_height()
                if x + rww > rightHandLimit: x, y = 0, y + sh
                x += rww + sw
            y += sh
            #print rendered_word, x, y
            x = 0
            choices.append( ( starting_x, starting_y, screenWidth - 1, y ) )
            starting_y = y + 1

        return choices

    def paintText( self, screen, justQuestionText, onText, questionText, onAnswer, highlight, stated, choice, colorLevel, colorLevels ):
        """
Paint words of **justQuestionText** and **questionText** on **screen** with appropriate colors.

What is appropriate depends on

* whether the question is **stated** (everything has been read aloud)
* how far along (**onText**) in the **justQuestionText** the reading of the question is
* how far along (**onAnswer**) in the **questionText** the reading of the answers is
* whether a **choice** has been selected
* if touched by **highlight**, the dwellTime-based **colorLevel** (out of  **colorLevels**)
        """

        #print choice

        # If not stated, start with all unreadColor
        if not stated:
            self.writewrap( screen, self.font, self.boundingRectangle, self.unreadColor, questionText[-1] )

            if onAnswer == 0:
               # paint as much readColor as needed on question
               self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, justQuestionText[onText] )
            else:
               # or paint as much readColor as needed on answers
               # print "on answer" + str(on_answer)
               self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[onAnswer] )

        # else start with all readColor
        else:
            self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[-1] )

            # If choice made, paint it selectedColor, but everything before it readColor
            if choice[0] > 0 and choice[0] <= len( questionText ) - 1:
               self.writewrap( screen, self.font, self.boundingRectangle, self.selectedColor, questionText[choice[0]] )
               self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[choice[0] - 1] )
            else:
                # If choice highlighted, paint it yellow, but everything before it gray
                if highlight > 0:
                   #self.writewrap(screen,self.font,self.boundingRectangle,self.yellow,questionText[highlight])
                   #print highlight, len(questionText)
                   highlightPercent = float( colorLevel ) / float( colorLevels )
                   highlightPart = [x * highlightPercent for x in self.highlightColor]
                   selectedPercent = 1 - highlightPercent
                   selectedPart = [x * selectedPercent for x in self.selectedColor]
                   blendedColor = [int( selectedPart[i] + highlightPart[i] ) for i in [0, 1, 2]]
##                   print highlight,stated,choice,colorLevel,colorLevels,blendedColor
##                   print highlightPercent, highlightPart
##                   print selectedPercent, selectedPart
##                   print blendedColor, highlight
                   self.writewrap( screen, self.font, self.boundingRectangle, blendedColor, questionText[highlight] )
                   self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[highlight - 1] )

        pygame.display.flip()


