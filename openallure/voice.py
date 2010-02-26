"""
voice.py
a component of openallure.py

Collection of functions for rendering text-to-speech

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

import pygame
import dragonfly
import ConfigParser

class Voice( object ):
    """Text-to-speech Functionality ( optional )"""
    def __init__( self ):
        """Initialize flag for available text-to-speech engine

        TODO: Make this dynamic rather than hardcoded.
        """
        config = ConfigParser.RawConfigParser()
        config.read( 'openallure.cfg' )
        self.systemHasDragonfly = eval( config.get( 'Voice', 'systemHasDragonfly' ) )
        self.systemHasEspeak    = eval( config.get( 'Voice', 'systemHasEspeak' ) )

    def speak( self,phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.systemHasDragonfly:
           e = dragonfly.get_engine()
           e.speak( phrase )
       elif self.systemHasEspeak:
           os.system( 'espeak -s150 "' + phrase + '"' )
       else:
           print phrase
           #pygame.time.wait( 500 )
