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

    def speak( self, phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.systemHasDragonfly:
           e = dragonfly.get_engine()
           e.speak( phrase )
       elif self.systemHasEspeak:
           os.system( 'espeak -s150 "' + phrase + '"' )
       else:
           print( phrase )
           #pygame.time.wait( 500 )

def test_voice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    voice.speak("Hello World")

if __name__ == "__main__":
    test_voice()
