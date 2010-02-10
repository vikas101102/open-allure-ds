#!/usr/bin/env python
"""
pyPong.py

Implement game like Pong(R) using webcam to control paddles

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""
__version__='0.1d0dev'

def main():
    """Initialization and event loop"""
    import logging
    import game
    import pygame

    #print dir()
    #print dir(video)
    #print dir(game)
    print("\n\n   pyPong. B for Ball(s). S to Show webcam. R to Recalibrate. Escape to quit.\n\n   Enjoy!\n\n")

    logging.basicConfig(level=logging.DEBUG)
    logging.info(" PyPong Version: %s" % __version__)

##    greenScreen = video.GreenScreen()
##    vcp         = video.VideoCapturePlayer(processFunction=greenScreen.process)
##    gesture     = gesture.Gesture()
    game        = game.Game()

##    _quit = 0
##    while not _quit:
##       processedImage = vcp.get_and_flip()
##       signal = gesture.countWhitePixels(processedImage)
##       print signal

##       vcp.clock.tick()

    pygame.quit()

if __name__ == '__main__':
    main()