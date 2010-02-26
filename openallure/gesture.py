"""
gesture.py
a component of openallure.py

Derive a signal from a processed webcam image

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

import pygame

DEFAULT_BOX_PLACEMENT = ( 0, 1, 2, 3, 4, 13, 14, 15, 16, 17 )

class Gesture(object):
    """
    Return the uppermost choice based on checking boxes on either side of a webcam image.

    **Background**

    A webcam image processed with the green screen approach (background subtraction)
    may have white pixels which can be used to extract a signal from a gesture (hand movement).

    This implementation looks along rows of boxes, counting the non-black (white) pixels within each box.
    Any count over 5 (about finger width) is considered a valid selection.

    """
    def isBoxSelected( self, imageArray, xoffset, yoffset, threshold=10, n=11, spacing=2 ):
       """
       Determine whether a box located at (lower right) coordinate
       **xoffset**, **yoffset** in an
       **imageArray** is selected based on whether more than
       **threshold** number of pixels in an
       **n** x **n** matrix of pixels with
       **spacing** (to cover more area while processing fewer pixels) have non-black values
       """
       xUpperLeft = max( 0, xoffset - n * spacing )
       #print xUpperLeft
       yUpperLeft = max( 0, yoffset - n * spacing )
       count = 0
       for i    in range( 1, n ):
          for j in range( 1, n ):
             # test pixel
             if imageArray[ i * spacing + xUpperLeft, j * spacing + yUpperLeft ] > 0:
                #print i*spacing+xUpperLeft,j*spacing+yUpperLeft
                count += 1
       if count > threshold:
          return 1
       else:
          return 0

    def choiceSelected( self, image, choices, boxWidth=35, boxPlacementList=DEFAULT_BOX_PLACEMENT ):
        """
        Find which choice is selected in an
        **image** where
        **choices** contains a list of coordinates (upper left x y, lower right x y) of non-overlapping regions within the image.

        A row of boxes is checked along the lower edge of each region.

        Each box has width **boxWidth** and they can be placed using **boxPlacementList** in a manner that leaves a gap mid-image so head motion does not interfere with hand gestures.

        Function returns a (choice, boxCount) tuple. This allows for auto-recalibration when choice 0 is selected with too many boxes.

        If no choice is selected, a choice of -1 is returned.

        TODO: Use a better system which allows hand gestures to be recognized even with a moving face as the background.
        """
        import pygame
        imageArray = pygame.PixelArray( image )
        yLowerRight = 3
        for choice, coordinates in enumerate( choices ):
           boxCount = 0
           for aBox in boxPlacementList:
              boxCount += self.isBoxSelected( imageArray, aBox * boxWidth, coordinates[ yLowerRight] )
##              if boxCount > 5 and calibrate == 1:
##                 #speak("Need to recalibrate")
##                 #print "boxCount" , boxCount
##                 GreenScreen.__init__(greenScreen)
##                 calibrate = 0
           if boxCount:
               return choice, boxCount
        #else
        return -1, 0
