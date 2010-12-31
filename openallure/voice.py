"""
voice.py
a component of openallure.py

Function for rendering text-to-speech

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

from configobj import ConfigObj
import os
import subprocess
import sys

class Voice( object ):
    """Text-to-speech Functionality ( optional )"""
    def __init__( self ):
        """Initialize flags for text-to-speech engines"""
        self.useEspeak = 0
        self.useSay = 0
        self.useSayStatic = 0
        config = ConfigObj(r"openallure.cfg")
        if sys.platform == 'darwin':
            self.useSay = eval( config['Voice']['useSay'] )
        elif sys.platform == 'win32':
            self.useSayStatic = eval( config['Voice']['useSayStatic' ] )
        else:
            self.useEspeak = eval( config['Voice']['useEspeak'] )
        self.language = config['Voice']['language'] 
        if self.language:
            self.language = self.language + " "
        self.pid_status = 0

    def speak( self, phrase ):
        """Say or print phrase using text-to-speech engine or stdout"""
        phrase = phrase.strip()
        if len(phrase) == 0:
            return

        if self.useEspeak:
            subprocess.Popen( ['espeak', " -s150 " + self.language + \
                               phrase.encode( 'utf-8' ) + '"' ] )
        elif self.useSay:
            if self.pid_status == 0:
                self.pid_status = subprocess.Popen( ['say', \
                '"' + self.language + phrase.encode( 'utf-8' ) + '"' ]).pid
            else:
                # wait for prior speaking to finish
                try:
                    self.pid_status = os.waitpid(self.pid_status, 0)[1]
                except:
                    pass
                self.pid_status = subprocess.Popen( ['say', \
                '"' + self.language + phrase.encode( 'utf-8' ) + '"' ]).pid
                
        elif self.useSayStatic:
            try:
                subprocess.call(["SayStatic ", \
                                 phrase.encode( 'utf-8' )], shell=True)
            except OSError, e:
                print("Call to SayStatic failed:", e)
                
        else:
            print( phrase.encode('utf-8'))

def testVoice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    voice.speak("This is a test")

if __name__ == "__main__":
    testVoice()
