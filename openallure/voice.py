"""
voice.py
a component of openallure.py

Collection of functions for rendering text-to-speech

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

import pygame

class Voice( object ):
    """Text-to-speech Functionality (optional)"""
    def __init__( self ):
        """Initialize flag for available text-to-speech engine

        TODO: Make this dynamic rather than hardcoded.
        """
        self.systemHasDragonfly = 0
        self.systemHasEspeak = 0

    def speak( self, phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""
       if self.systemHasDragonfly:
           e = dragonfly.get_engine()
           e.speak( phrase )
       elif self.systemHasEspeak:
           os.system( 'espeak -s150 "' + phrase + '"' )
       else:
           print phrase
           #pygame.time.wait(500)
