"""
voice.py
a component of openallure.py

Collection of functions for rendering text-to-speech

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt

TODO: Add standalone tests for text-to-speech modules.
"""

import ConfigParser
import os
import pygame
import subprocess
mixer = pygame.mixer
time = pygame.time

class Voice( object ):
    """Text-to-speech Functionality ( optional )"""
    def __init__( self ):
        """Initialize flag for available text-to-speech engine

        TODO: Make this dynamic rather than hardcoded.
        """
        config = ConfigParser.RawConfigParser()
        config.read( 'openallure.cfg' )
        self.useEspeak = eval( config.get( 'Voice', 'useEspeak' ) )
        self.useSay    = eval( config.get( 'Voice', 'useSay' ) )
        self.usesaystatic    = eval( config.get( 'Voice', 'usesaystatic' ) )
        self.language  = config.get( 'Voice', 'language' )
        if self.language:
            self.language = self.language + " "
        self.pid_status = 0

    def speak( self, phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.useEspeak:
           p = subprocess.Popen( ['espeak', " -s150 " + self.language + phrase.encode( 'utf-8' ) + '"' ] )
       elif self.useSay:
           if self.pid_status == 0:
               self.pid_status = subprocess.Popen( ['say', '"' + self.language + phrase.encode( 'utf-8' ) + '"' ]).pid
               # OK to continue execution, fading in text and getting input while computer talks
           else:
               # wait for prior speaking to finish
               try:
                   self.pid_status = os.waitpid(self.pid_status, 0)[1]
               except:
                   pass
               self.pid_status = subprocess.Popen( ['say', '"' + self.language + phrase.encode( 'utf-8' ) + '"' ]).pid
       elif self.usesaystatic:
           # print("using saystatic with " + str(self.pid_status))
           try:
               retcode = subprocess.call(["SayStatic ", phrase.encode( 'utf-8' )], shell=True)
##               if retcode < 0:
##                   print("Child was terminated by signal", -retcode)
##               else:
##                   print("Child returned", retcode)
           except OSError, e:
               print("Execution failed:", e)
##           if self.pid_status == 0:
##               if phrase != '' and len(phrase) > 0:
##                  self.pid_status = subprocess.Popen( ['saystatic', '"' + phrase.encode( 'utf-8' ) + '"' ]).pid
##               # OK to continue execution, fading in text and getting input while computer talks
##           else:
##               # wait for prior speaking to finish
##               print("trying to wait on " + str(self.pid_status))
##               try:
##                  self.pid_status = os.waitpid(self.pid_status, 0)[1]
##               except OSError:
##               try:
##                   while self.pid_status:
##                      print("waited for " + str(self.pid_status))
##               except:
##                   pass
##                  if phrase != '' and len(phrase)>0 :
##                      self.pid_status = subprocess.Popen( ['saystatic', '"' + phrase.encode( 'utf-8' ) + '"' ]).pid

       else:
           print( phrase.encode( 'utf-8' ) )
           # Allow time for user to move hand down
           pygame.time.wait( 500 )

def test_voice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    voice.speak("Finished")

if __name__ == "__main__":
    test_voice()
