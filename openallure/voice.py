"""
voice.py
a component of openallure.py

Collection of functions for rendering text-to-speech

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt

TODO: Add standalone tests for text-to-speech modules.
"""

import os
import ConfigParser
import pygame
try:
    import dragonfly
except ImportError:
    pass

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
        self.systemHasSay       = eval( config.get( 'Voice', 'systemHasSay' ) )

    def speak( self, phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.systemHasDragonfly:
           e = dragonfly.get_engine()
           e.speak( phrase.encode( 'utf-8' ) )
       elif self.systemHasEspeak:
           os.system( 'espeak -s150 "' + phrase.encode( 'utf-8' ) + '"' )
       elif self.systemHasSay:
           os.system( 'say "' + phrase.encode( 'utf-8' ) + '"' )
       else:
           print( phrase.encode( 'utf-8' ) )
           # Allow time for user to move hand down
           pygame.time.wait( 500 )

def test_voice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    voice.speak("Hello World")

if __name__ == "__main__":
    test_voice()
