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
from restclient import POST 
mixer = pygame.mixer
time = pygame.time

# only allow useDragonfly if dragonfly module can be imported
allowUseDragonfly = True
try:
    import dragonfly
except ImportError:
    allowUseDragonfly = False

class Voice( object ):
    """Text-to-speech Functionality ( optional )"""
    def __init__( self ):
        """Initialize flag for available text-to-speech engine

        TODO: Make this dynamic rather than hardcoded.
        """
        config = ConfigParser.RawConfigParser()
        config.read( 'openallure.cfg' )
        if allowUseDragonfly:
            self.useDragonfly = eval( config.get( 'Voice', 'useDragonfly' ) )
        else:
            self.useDragonfly = False
            wantedToUseDragonfly = eval( config.get( 'Voice', 'useDragonfly' ) )
            if wantedToUseDragonfly:
                print "Dragonfly module not installed. Download from http://code.google.com/p/dragonfly/"

        self.useEspeak = eval( config.get( 'Voice', 'useEspeak' ) )
        self.useSay    = eval( config.get( 'Voice', 'useSay' ) )
        self.useiSpeech    = eval( config.get( 'Voice', 'useiSpeech' ) )
        self.language  = config.get( 'Voice', 'language' )
        if self.language:
            self.language = self.language + " "
        self.pid_status = 0

    def speak( self, phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.useDragonfly:
           e = dragonfly.get_engine()
           e.speak( phrase.encode( 'utf-8' ) )
       elif self.useEspeak:
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
       elif self.useiSpeech:
               r = POST("http://ws.ispeech.org/api/rest/1.5/",params={'username' : 'john.graves@aut.ac.nz', \
               'password' : 'JohnGAUT', 'action' : 'convert', \
               'text' : phrase, \
               'voice' : 'engfemale2', 'format' : 'wav'})
               print r
               #'status=waiting&result=success&fileid=1844815&words=2'
    
               status = r.split('&')[1].split('=')[1]
               fileid = r.split('&')[2].split('=')[1]
               fileName = fileid + '.wav'
               f = open(fileName, 'w')
    
               while status in ("waiting","working"):
                   print ('Waiting conversion ...')
                   r = POST("http://ws.ispeech.org/api/rest/1.5/",params={'username' : 'john.graves@aut.ac.nz', \
                   'password' : 'JohnGAUT', \
                   'action' : 'status', \
                   'fileid' : fileid})
                   #'result=success&status=finished&filesize=62246&words=1&eta=1&format=wav'
                   status = r.split('&')[1].split('=')[1]
                   print status
               
               downloadFile = POST("http://ws.ispeech.org/api/rest/1.5/",params={'username' : 'john.graves@aut.ac.nz', \
               'password' : 'JohnGAUT', \
               'action' : 'download', \
               'fileid' : fileid})               
               f.write(downloadFile)
               f.close()

               #choose a desired audio format
               mixer.init(11025) #raises exception on fail
           
               #load the sound    
               sound = mixer.Sound(fileName)
           
               #start playing
               print ('Playing Sound...')
               channel = sound.play()

               #poll until finished
               while channel.get_busy(): #still playing
                   print ('  ...still going...')
                   time.wait(1000)
               print ('...Finished')
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
