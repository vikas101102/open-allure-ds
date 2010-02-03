# Derived from Nirav Patel's Pygame Camera Tutorial
# http://code.google.com/p/pycam/source/browse/trunk/pycam/pycam/VideoCapturePlayer.py
# http://code.google.com/p/pycam/source/browse/trunk/pycam/examples/greenscreen.py
# Have green screen RESET when too many selections or R is pressed
# Knock out middle columns to ignore head motion
# 20100203b.py JG Modified for Windows
# 20100203c.py JG Both up/down arrow and gesture highlighting work

#  Variables to control code to run in different environments
# TODO: Make these dynamic
system_has_dragonfly = 1
system_has_espeak    = 0
verbose              = 0

import os
import pygame
from pygame.locals import *
import numpy
from pgu import text
import exceptions

import logging
verbose = False

if system_has_dragonfly:
   import dragonfly
   from dragonfly import *

pygame.font.init()
font = pygame.font.SysFont("default", 50)

black = (0,0,0)
gray  = (200,200,200)
red   = (255,0,0)
white = (255,255,255)
yellow= (255,255,0)

"""
Parsing of separate content file

Question part1
Question part2
<optional blank line>
Answer 1 <separator> Response 1
Answer 2 <separator> Response 2
...
up to 6 answers
<blank line>

where <separator> can be
; no action
;; or ;1 or ;+1 advance to next question
;-1 return to prior question (in order exposed in sequence)
;;; or ;2 or ;+2 advance two questions
"""

content_file_name = "20100203e.txt"
inputs = open(content_file_name).readlines()
#print inputs

def classify(strings):
    """Identify strings which contain new line only
                              contain ; or ;; markers"""
    string_types = []
    for i in strings:
        if i == "\n": string_types.append("N")
        else:
           slash_at = i.find(";")
           if slash_at > 0: string_types.append(str(slash_at))
           else: string_types.append("Q")

    return string_types

#print classify(inputs)

def regroup(strings,string_types):
    """Use string_types to sort strings into Questions,
                                Answers, Responses and Subsequent Actions"""
    on_string = 0
    sequence = []
    question = []
    answer   = []
    response = []
    action   = []
    while on_string < len(strings):
        if string_types[on_string] == "Q": question.append(strings[on_string].rstrip())
        elif string_types[on_string] == "N":
            # signal for end of question IF there are responses
            if len(response):
                # add to sequence and reset
                sequence.append([question, answer, response, action])
                question = []
                answer   = []
                response = []
                action   = []
        else:
            # use number to break string into answer and response
            answer.append(strings[on_string][:int(string_types[on_string])].rstrip())
            # NOTE: +1 means to leave off first ;
            response_string = strings[on_string][int(string_types[on_string])+1:].strip()

            # examine start of response_string to determine if it signals action
            # with additional ;'s or digits (including + and -)
            # IF none found, leave action as 0
            action_value = 0
            while len(response_string) and response_string[0] == ';':
                action_value += 1
                response_string = response_string[1:].lstrip()
            digits = ''
            while len(response_string) and (response_string[0].isdigit() or response_string[0] in ['+','-']):
                digits += response_string[0]
                response_string = response_string[1:].lstrip()
            if len(digits): action_value = int(digits)

            response.append(response_string)
            action.append(action_value)

        on_string += 1
    # append last question if not already signaled by N at end of inputs
    if len(question): sequence.append([question, answer, response, action])
    return sequence

#print classify(inputs)
sequence = regroup(inputs, classify(inputs))
#print sequence

# Text-to-speech Functionality (optional)
def speak(phrase):
   global system_has_dragonfly, system_has_espeak
   #print phrase
   if system_has_dragonfly:
	   e = dragonfly.get_engine()
	   e.speak(phrase)
   if system_has_espeak:
       os.system('espeak -s150 "' + phrase + '"')
   if not (system_has_dragonfly or system_has_espeak):
       print phrase
       pygame.time.wait(500)

if system_has_dragonfly == 1: speak("Using dragonfly")
if system_has_espeak    == 1: speak("Using e speak")

def build_question_text(question):
   global question_text, just_question_text, choices, answer_at, calibrate, color_level, color_levels
   global highlight, highlight_on
   """
   question_text[0] is question
   question_text[1] is question + answer 1
   question_text[2] is question + answer 1 + answer 2
   etc.

   just_question_text[0] is first (perhaps only) part of question
   just_question_text[1] is next part of question
   etc.

   choices tells how may answers there are

   answer_at[0] is tuple with y and height of question
   answer_at[1] is tuple with y and height of first answer
   """
   # TODO Put all initializations together here
   highlight = 0
   highlight_on = 0
   color_level = color_levels
   calibrate = 0
   question_text = [""]
   question_text[0] = " ".join(question[0]) + "\n"
   on_answer = 0
   answer_at = []
   for i in question[1]:
      question_text.append(question_text[on_answer] + "\n" + i)
      on_answer += 1
   choices = on_answer
#   speak(str(choices) + " found")

   # build just question in pieces (if any)
   just_question_text = [""]
   on_text = 0
   for i in question[0]:
      just_question_text.append(just_question_text[on_text] + i + " ")
      on_text += 1
   just_question_text = just_question_text[1:]

   # Pre-render text to find out where it will be placed
   # find width and height of one space
   space = font.render(" ",1,black)
   sw,sh = space.get_width(),space.get_height()
   del space
   starting_y = 0
   for text in question_text:
      x = y = 0
      for sentence in text.split("\n"):
         for word in sentence.split(" "):
            rendered_word = font.render(word,1,black)
            rww,rwh = rendered_word.get_width(),rendered_word.get_height()
            if x+rww > 620: x,y = 0,y+sh
            x += rww+sw
         y += sh
         #print rendered_word, x, y
         x = 0
      answer_at.append((starting_y,y-starting_y))
      starting_y = y
   #print answer_at

"""
Future API changing notes.
It would be good to combine the VideoCapturePlayers (VCP) for OpenCV and for Pygame.
Maybe using functools a VCP could be made using the optimal data storage format?

Or could have in the constructor args a opencvprocess and a numpyprocess and a surface process
and depending on what is given create the right display and use the right data storage...


"""

logging.debug("Pygame Version: %s" % pygame.__version__)

class VideoCapturePlayer(object):
    """
    A VideoCapturePlayer object is an encapsulation of
    the display of a video stream.

    A process can be given (as a function) that is run
    on every frame between capture and display.

    For example a filter function that takes and returns a
    surface can be given. This player will take the webcam image,
    pass it through the filter then display the result.

    If the function takes significant computation time (>1second)
    The VideoCapturePlayer takes 3 images between each, this flushes
    the buffer, ensuring an updated picture is used in the next computation.

    If a new version of pygame is installed - this class uses the pygame.camera module, otherwise
    it uses opencv.
    """
    size = width,height = 640, 480

    def __init__(self, processFunction = None, forceOpenCv = False, displaySurface=None, show=True, **argd):
        self.__dict__.update(**argd)
        super(VideoCapturePlayer, self).__init__(**argd)
        logging.debug("Initializing Video Capture Class")
        self.processFunction = processFunction
        self.processRuns = 0

        self.show = show

        self.display = displaySurface
        if self.display is None:
            if show is True:
                # create a display surface. standard pygame stuff
                self.display = pygame.display.set_mode( self.size, 0 )
            else:
                pygame.display.init()
                #pygame.display.set_mode((0,0),0)
                self.display = pygame.surface.Surface(self.size)

        if forceOpenCv:
            import camera
        else:
            import pygame.camera as camera
        camera.init()

        # gets a list of available cameras.
        self.clist = camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")

        logging.info("Opening device %s, with video size (%s,%s)" % (self.clist[0],self.size[0],self.size[1]))

        # creates the camera of the specified size and in RGB colorspace
        if not forceOpenCv:
            try:
                self.camera = camera.Camera(self.clist[0], self.size, "RGB")
                # starts the camera
                self.camera.start()
            except:
                logging.debug("Ignoring that pygame camera failed - we will try opencv")
                forceOpenCv = True
                del camera
                import camera
                self.clist = camera.list_cameras()
        if forceOpenCv:
            logging.debug("Trying to open the OpenCV wrapped camera")
            self.camera = camera.Camera(self.clist[0], self.size, "RGB", imageType="pygame")
            self.camera.start()

        logging.info("Waiting for camera...")
        self.waitForCam()
        logging.info("Camera ready.")

        self.clock = pygame.time.Clock()
        self.processClock = pygame.time.Clock()

        # create a surface to capture to.  for performance purposes, you want the
        # bit depth to be the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

        # name colors
        self.black = (0,0,0)
        self.gray  = (200,200,200)
        self.white = (255,255,255)
        self.red   = (255,0,0)
        self.blue  = (0,255,0)
        self.green = (0,0,255)
        self.yellow= (255,255,0)
        self.purple= (255,0,255)
        self.selected= (84,245,56) # A shade of green

    def paint_box(self,ar,xoffset,yoffset,(red,blue,green)):
          # paint box with color
          ar[0+xoffset:22+xoffset,0+yoffset:22+yoffset] = (red, blue, green)

    def color_box(self,ar,xoffset,yoffset,(red,blue,green),paintyn):
       global calibrate
       # Draw reference lines
       ar[0+xoffset:22+xoffset,22+yoffset]    = (red,blue,green)
       count = 0
       for i in range(1, 11):
          for j in range(1, 11):
             if ar[2*i+xoffset,2*j+yoffset] > 10000000:
                if calibrate == 1: count += 1
       if count > 10:
          count = 10
       red = int(red*count/10)
       blue = int(blue*count/10)
       green = int(green*count/10)
       if count > 4 and paintyn:
          self.paint_box(ar,xoffset,yoffset,(red,blue,green))
       if count == 10:
          return 1
       else:
          return 0

    def set_unset(self,ar,xoffset,yoffset,color,box_state):
       global action_pending
       if not box_state:
          box1=self.color_box(ar,xoffset,yoffset,color,1)

       # gesture to left turns on state
       box1a=self.color_box(ar,xoffset-20,yoffset,color,0)
       if box1a or box_state:
          # paint box and set state
          self.paint_box(ar,xoffset,yoffset,color)
          box_state=1

       # gesture to right turns off state +y_yh[1]
       box1b=self.color_box(ar,xoffset+20,yoffset,color,0)
       if box1b:
          box_state=0
          action_pending = 0
       return box_state

    def state(self, question):
       """
       question[0] is the question, protentially broken into pieces for easier reading
       question[1] are the possible answers
       question[2] are the actions in response to those answers
       question[3] are the next question in response to those answers
       """
       global _silence, choice, _stated, on_text, on_answer, skip_response, _quit
       #NOTE: _stated may be reset to 0 by a check_event call
       # always start reading a new question
       #TODO: check_event call can change which question we're on!
       _silence = 0
       choice = 0
       skip_response = 0
       self.get_and_flip()
#       pygame.time.wait(1000)
       self.check_events()

       #read question
       on_text = 0
       for i in question[0]:
          self.check_events()
          if _silence or choice or _quit: break
          self.get_and_flip()
          speak(i.strip())
          on_text += 1
          on_text = min(on_text,len(question[0])-1)

       #read answers with interrupt
       #pygame.time.wait(1000)
       on_answer = 0
       for i in question[1]:
          self.check_events()
          if _silence or choice or _quit: break
          on_answer += 1
          self.get_and_flip()
          # Check for answer with "A. "
          if i[1:3] == '. ':
              speak(i[3:].strip())
          else:
              speak(i.strip())

       _stated = 1

    def show_choice(self,key):
       global _stated, on_question, question, question_text, _dictation, on_text, on_answer, skip_response, _quit
       #check for valid key - must be no greater than number of answers or -1 from left arrow
       if key == -1:
          # return to prior question
          if len(questions) >0:
              on_question = questions.pop()
          else:
              on_question = 0
          question = sequence[on_question]
          build_question_text(question)
          choice = 0
          _stated = 0
          return
       else:
           if key > len(question[1]):
               # Choice is invalid, reset
               choice = 0
               return
           answer = key - 1
           if len(choices_made) > 0:
               # check if answer in choices made
               if not answer in choices_made:
                   choices_made.append(answer)

           if not skip_response:
               # color selected choice
               self.get_and_flip()
               #repeat answer
               if question[1][answer][1:3] == '. ':
                      speak("You selected " + question[1][answer][3:].strip())
               else:
                      speak("You selected " + question[1][answer].strip())

               #check that response exists for answer
               if len(question[2]) >= key and isinstance(question[2][answer],str):
                  #speak response to answer
                  speak(question[2][answer].strip())
               skip_response = 0

       # reset pointers for next question
       on_text = 0
       on_answer = 0
       highlight = 0
       on_highlight = 0

       #check that next sequence exists as integer for answer
       if key <= len(question[3]) and isinstance(question[3][answer],int):
          #advance in sequence
          next = question[3][answer]
          if next == 99:
              # process input
              speak("Taking dictation")
              _silence = 1
              _dictation = 1
              while _dictation: self.check_events()
          else:
              # Add last question to stack if moving on
              if next > 0:
				 questions.append(on_question)
				 on_question = on_question + next

              # Try to pop question off stack if moving back
              elif next < 0:
			    for i in range(1,1-next):
				   if len(questions) > 0:
						on_question = questions.pop()
				   else:
						on_question = 0

              # Quit if advance goes beyond end of sequence
              if on_question >= len(sequence):
                  speak("You have reached the end. Goodbye.")
                  _quit = 1
              else:
                  question = sequence[on_question]
                  build_question_text(question)
                  choice = 0
       else:
           # invalid or final choice
           _quit = 1
       _stated = 0


    def get_and_flip(self):
        """We will take a snapshot, do some arbitrary process (eg in numpy/scipy)
        then display it.
        """
        global action_pending, on_text, on_answer, just_question_text, choice, choices
        global _stated, highlight, highlight_on, calibrate, row_time, color_level, color_levels

        # capture an image
        self.snapshot = self.camera.get_image(self.snapshot)#.convert()
        #self.snapshot = self.camera.get_image(self.snapshot) # if not use this line

        # Manipulate the image. Flip it around the y axis.
        ar = pygame.PixelArray (self.snapshot)
        ar[:] = ar[::-1,:]
       # del ar

        if self.processFunction:
            self.processClock.tick()
            if self.processRuns > 5 and self.processClock.get_fps() < 2:
                # The function is really slow so take a few frames.
                #if verbose:
                #    print "Running your resource intensive process at %f fps" % self.processClock.get_fps()
                # flush the camera buffer to get a new image...
                # we have the time since the process is slow...
                for i in range(5):
          #          self.waitForCam()
                    del ar
                    self.snapshot = self.camera.get_image(self.snapshot)#.convert()
                    # Manipulate the image. Flip it around the y axis.
                    ar = pygame.PixelArray (self.snapshot)
                    ar[:] = ar[::-1,:]
     #               del ar
            else:
     #           self.waitForCam()
                del ar
                self.snapshot = self.camera.get_image(self.snapshot)
                # Manipulate the image. Flip it around the y axis.
                ar = pygame.PixelArray (self.snapshot)
                ar[:] = ar[::-1,:]
      #          del ar
            #try:
            res = self.processFunction(self.snapshot)
            if isinstance(res,pygame.Surface):
                self.snapshot = res
                ar = pygame.PixelArray (self.snapshot)
                #print ar[:10]
            self.processRuns += 1

                #except Exception, e:
                #    print e
                #    raise exceptions.RuntimeError("error while running the process function")

            # Draw lines
            row_counts = []
            for y_yh in answer_at:
               #ar[0:640,y_yh[0]+20] = white # +y_yh[1]
               row_count = 0
               for x in [0, 1, 2, 3, 4,  13, 14, 15, 16, 17]:
                  xspacing = 35
                  row_count += self.color_box(ar,x*xspacing,y_yh[0]+y_yh[1],white,1)
                  if row_count > 5 and calibrate == 1:
                     #speak("Need to recalibrate")
                     #print "row_count" , row_count
                     GreenScreen.__init__(greenScreen)
                     calibrate = 0
               row_counts.append(row_count)
            #print row_counts
            #if highlight_on == 0:
            for row, row_count in enumerate(row_counts):
               if row_count > 0:
                  highlight_on = 1
                  # Check if already highlighted
                  if not highlight == row:
                     row_time = pygame.time.get_ticks()
                  highlight = row
                  # set color level based on either row_count or time on
                  # max keeps color_level from becoming negative
                  # min keeps color_level from exceeding the number of color levels
                  # the last expression should get down to color_level 0 with a row_count of 3+
                  color_level = max(0,min(color_levels,color_levels-row_count*3))
                  if row_time:
                      dwell_time = pygame.time.get_ticks() - row_time
                      if verbose: print dwell_time
                      color_level -= int(dwell_time/200)
                      color_level = max(0, color_level)
                  if color_level == 0: choice = row
                  break
               else:
                  # check if previously highlighted and if so fade
                  if highlight == row:
                      color_level += 1
                      color_level = min(color_level, color_levels)
                      if color_level == color_levels:
                          highlight_on = 0
               #print index, item
            if highlight_on == 0:
                row_time = 0
                highlight = 0
                color_level = color_levels
            del ar

        if self.show is not False:
            # blit it to the display surface.  simple!
            self.display.blit(self.snapshot, (0,0))

        # paint words on it with appropriate colors
        # If not stated, start with all black
        if choice > 0 and verbose: print "In get_and_flip (_stated/p/choice):" + str(_stated) + " " + str(on_question) + " " + str(choice)
        if not _stated:
            text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.white,question_text[-1])

            if on_answer == 0:
               # paint as much gray as needed on question
               text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,just_question_text[on_text])
            else:
               # or paint as much gray as needed on answers
               # print "on answer" + str(on_answer)
               text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,question_text[on_answer])

        # else start with all gray
        else:
            text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,question_text[-1])

            # If choice made, paint it red, but everything before it gray
            if choice > 0 and choice <= len(question_text)-1:
               text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.red,question_text[choice])
               text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,question_text[choice-1])
            else:
                # If choice highlighted, paint it yellow, but everything before it gray
                if highlight > 0:
                   #text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.yellow,question_text[highlight])
                   #print highlight, len(question_text)
                   text.writewrap(self.display,font,pygame.Rect(20,20,620,460),(255,int(255*color_level/color_levels),0),question_text[highlight])
                   text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,question_text[highlight-1])

        pygame.display.flip()


    def waitForCam(self):
       # Wait until camera is ready to take image
#        while not self.camera.query_image():
 #           pygame.time.wait(100)
        pass

    def check_events(self):
        global on_question, question, questions, choice, _stated, _quit, _silence, _dictation, skip_response
        global highlight, highlight_on, on_answer, on_text, _quit, calibrate, color_level, color_levels
        for e in pygame.event.get():
           if e.type is QUIT:
              _quit = 1
           if choice == 0:
               # Keys 1 through 6 select choices 1 through 6
               if e.type is KEYDOWN and e.key == K_1: choice = 1
               if e.type is KEYDOWN and e.key == K_2: choice = 2
               if e.type is KEYDOWN and e.key == K_3: choice = 3
               if e.type is KEYDOWN and e.key == K_4: choice = 4
               if e.type is KEYDOWN and e.key == K_5: choice = 5
               if e.type is KEYDOWN and e.key == K_6: choice = 6

               # Keys a through f select choices 1 through 6
               if e.type is KEYDOWN and e.key == K_a: choice = 1
               if e.type is KEYDOWN and e.key == K_b: choice = 2
               if e.type is KEYDOWN and e.key == K_c: choice = 3
               if e.type is KEYDOWN and e.key == K_d: choice = 4
               if e.type is KEYDOWN and e.key == K_e: choice = 5
               if e.type is KEYDOWN and e.key == K_f: choice = 6

               if e.type is KEYDOWN and e.key == K_r: GreenScreen.__init__(greenScreen)

               # Quality control on choice: reset choices beyond valid list
               if choice > len(question[1]):
                   choice = 0
                   speak("Note there are only " + str(len(question[1])) + " choices")

               # Right arrow advances in question sequence
               if e.type is KEYDOWN and e.key == K_RIGHT:
                  _silence = 1
                  on_text = 0
                  on_answer = 0
                  skip_response = 1

                  # Choice is first non-zero entry in question[3]
                  on_choice = 0
                  for i in question[3]:
                      on_choice += 1
                      if i > 0:
                          choice = on_choice
                          speak("On question " + str(on_question + i))
                          break

               # Left arrow backs up in question sequence
               if e.type is KEYDOWN and e.key == K_LEFT:
                  _silence = 1
                  on_text = 0
                  on_answer = 0
                  choice = -1
                  if len(questions) > 0:
                      speak("Returning to question " + str(questions[-1]))
                  else:
                      on_question = 0

               # Up arrow highlights prior answer (or wraps last answer)
               if e.type is KEYDOWN and e.key == K_UP:
                  _silence = 1
                  highlight_on = 1
                  color_level = color_levels
                  if highlight == 0 or highlight == 1:
                      highlight = len(question[1])
                  else:
                      highlight -= 1

               # Down arrow highlights next answer (or wraps to first answer)
               if e.type is KEYDOWN and e.key == K_DOWN:
                  _silence = 1
                  highlight += 1
                  highlight_on = 1
                  color_level = color_levels
                  if highlight > len(question[1]): highlight = 1

               # Enter key selected highlighted answer, if any
               if e.type is KEYDOWN and e.key == K_RETURN:
                  if highlight > 0:
                     choice = highlight

           # Escape key sets flag to quit
           if e.type is KEYDOWN and e.key == K_ESCAPE:
              _quit = 1

           # Spacebar sets flag to _silence voice
           if e.type is KEYDOWN and e.key == K_SPACE:
              _silence = 1

           if verbose: print "check_events (p/c/_stated) " + str(on_question) + " " + str(choice) + " " + str(_stated)
        else:
             return 0

    def main(self):
        global _stated, choice, _quit
        """Start the video capture loop"""
        if verbose:
            print "Video Capture & Display Started... press Escape to quit"
        _quit = 0
        fpslist = []
        while not _quit:
#           if self.camera.query_image():
           self.get_and_flip()
           if not _stated:
              self.state(question)
           self.check_events()
           # Note: negative choice can change question as well
           if not choice == 0:
              self.show_choice(choice)
           self.clock.tick()
"""
                self.clock.tick()
                if self.clock.get_fps():
                    fpslist.append(self.clock.get_fps())
                    if verbose:
                        print "fps: ",fpslist[-1]

        print "Video Capture &  Display complete."
        print "Average Frames Per Second "
        avg = numpy.average(fpslist)
        print avg
        if self.processFunction:
            print "Process ran at %f fps" % self.processClock.get_fps()
"""

if system_has_dragonfly:
    e = dragonfly.get_engine()
    e.speak("Hello")
    grammar = Grammar("voice mirror")

    class SpeakRule(CompoundRule):
        spec = "<text>"
        extras = [Dictation("text")]

        def _process_recognition(self, node, extras):
            # stop reading
            global _silence, choice, _dictation, on_question, question, sequence, _stated, _quit
            _silence = 1

            # repeat voice recognition
            answer = " ".join(node.words())
            answer1 = node.words()[0]
            speak("You said %s!" % answer)

            if _dictation == 0:
                # check for valid answer (see if words match)
                on_answer = 0
                match = 0
                for i in question[1]:
                    on_answer += 1
                    #check against available answers - in lower case without punctuation
                    # and allow first part only (eg "Yes." in "Yes. I agree.")
                    # or first word
                    answer = answer.lower().strip('.')
                    if answer == i.lower().strip('.?!') or answer == i.lower().split('.')[0] or answer == i.lower().split()[0]:
                       choice = on_answer
                       match = 1
                if not match:
                    #check first word against number words
                    on_answer = 0
                    for i in ["one","two","three","four","five","six"]:
                        on_answer += 1
                        if answer1 == i or answer == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check first word against "choice" + number words
                    on_answer = 0
                    for i in ["choice one","choice two","choice three","choice four","choice five","choice six"]:
                        on_answer += 1
                        if answer == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check first word against "answer" + number words
                    on_answer = 0
                    for i in ["answer one","answer two","answer three","answer four","answer five","answer six"]:
                        on_answer += 1
                        if answer == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check first word against words similar to number words
                    on_answer = 0
                    for i in ["won","to","tree","for","fife","sex"]:
                        on_answer += 1
                        if answer1 == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check against ordinal words
                    on_answer = 0
                    for i in ["first","second","third","fourth","fifth","sixth"]:
                        on_answer += 1
                        if answer1 == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check against ordinal words + "choice"
                    on_answer = 0
                    for i in ["first choice","second choice","third choice","fourth choice","fifth choice","sixth choice"]:
                        on_answer += 1
                        if answer == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check against ordinal words + "answer"
                    on_answer = 0
                    for i in ["first answer","second answer","third answer","fourth answer","fifth answer","sixth answer"]:
                        on_answer += 1
                        if answer == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check against letter words
                    on_answer = 0
                    for i in ["A.","B.","C.","D.","E.","F."]:
                        on_answer += 1
                        if answer1 == i:
                           choice = on_answer
                           match = 1
                if not match:
                    #check against control words
                    for i in ["next","next question","skip to next question"]:
                       if answer == i:
                          _silence = 1
                          on_text = 0
                          on_answer = 0
                          skip_response = 1

                          # Choice is first non-zero entry in question[3]
                          on_choice = 0
                          for i in question[3]:
                              on_choice += 1
                              if not i == 0:
                                  choice = on_choice
                                  speak("On question " + str(on_question + i))
                                  break
                          match = 1
                if not match:
                    for i in ["back","prior","previous","back up","back one","prior question","previous question"]:
                       if answer == i:
                          _silence = 1
                          on_text = 0
                          on_answer = 0
                          choice = -1
                          if len(questions) > 0:
                              speak("Returning to question " + str(questions[-1]))
                          else:
                              on_question = 0
                          match = 1
                if not match:
                    for i in ["quit now","exit now","i give up"]:
                       if answer == i:
                           _quit = 1
                           match = 1

                if not match:
                    speak("Try again.")
            else:
                speak("Thank you. Let's move on.")
                on_question = on_question + 1
                # avoid stepping past end of sequence
                on_question = min(on_question,len(sequence)-1)
                question = sequence[on_question]
                build_question_text(question)
                choice = 0
                _dictation = 0
            if match and verbose: print "dragonfly choice " + str(choice)

    grammar.add_rule(SpeakRule())    # Add the top-level rule.
    grammar.load()                   # Load the grammar.

class GreenScreen():
    def __init__(self):
        self.calibrated = False
        self.bgs = []

    def calibration(self, snapshot):
        global calibrate
        """
        Capture a bunch of background images and average them out.
        """
        if len(self.bgs) < 10:
            self.bgs.append(snapshot)
        else:
            # Average them out to remove noise, and save as background
            self.background = pygame.transform.average_surfaces(self.bgs)
            self.calibrated = True

    def threshold(self, snapshot):
        global calibrate
        #speak("Threshold" + str(calibrate))
        dest = snapshot.copy()
        dest.fill((255,255,255))    # Make a black background
        threshold_value = 40        # How close to the existing colour must each point be?
        pygame.transform.threshold(dest, snapshot, (0,0,0), [threshold_value]*3 ,(255,255,255),1, self.background)
        calibrate = 1
        # Median filter would be good here to remove salt + pepper noise...

        return dest #self.dest

    def process(self, snapshot):
        if not self.calibrated:
            return self.calibration(snapshot)
        else:
            return self.threshold(snapshot)



"""
Initialize global variables:

Name          Function
============= =============================================================================================
on_question   points to question in sequence by number
question      is structure holding the question, answers, responses to answers and subsequent actions
questions     is a list for tracking which questions were seen
choice        tells which answer is selected
_stated       is a flag indicating whether the question needs to be stated (read aloud via text-to-speech)
_quit         is a flag indicating whether to quit
_silence      is a flag indicating whether text-to-speech is off
skip_response is a flag to allow fast forwarding
_dication     is a flag indicating whether dication mode is on
highlight     is the number of the choice that should be highlighted
highlight_on  is a flag telling whether to apply highlights and whether Enter will make a selection
color_level   is an indicator of the extent of highlight (reflecting dwell time)
color_levels  is a parameter controlling how many levels of color change there are to the highlight
calibrate     is a flag telling whether the green screen has been calibrated
on_answer     is a pointer to help coordinate the display of answers with the text-to-speech reading of them
on_text       is a pointer to help coordinate the display of parts of the question with text-to-speech reading
"""

# Start on first question in sequence
on_question         = 0
question            = sequence[on_question]

# Start with no answers highlighted (Highlights should only result from gestures or up/down arrow keys or TODO mouse roll-overs) and dwell on row time of zero
highlight    = 0
highlight_on = 0
color_level  = 0
color_levels = 9
row_time     = 0
calibrate    = 0
greenScreen  = GreenScreen()

# Prepare text for easier display and count choices for first question
question_text       = [""]
just_question_text  = [""]
choices             = 0
answer_at           = []
build_question_text(question)

# Start with text-to-speech ON (if available)
_silence = 0

# Start with no answer chosen, no choices made and question unstated
choice   = 0
choices_made = []
_stated  = 0

# Start with pointers indicating no part of the question text and none of the answers have been read aloud
on_text   = 0
on_answer = 0

# Start with flags set to NOT quit and NOT have dictation mode
_quit      = 0
_dictation = 0

# Start with flag set to indicate that no action is pending (Actions will be pending when a gesture selection has been made, but not yet resolved into a choice)  -- TODO should no longer be needed
action_pending = 0

# Start with flag set to permit responses to be sent to text-to-speech.  This flag is used to skip responses when left/right arrow keys are used to skip through sequence
skip_response = 0

# Initialize stack of question numbers exposed.  Used to allow backward movement through sequence of questions.
questions = []

def main():
    vcp = VideoCapturePlayer(processFunction=greenScreen.process)
    vcp.main()
    pygame.quit()

if __name__ == '__main__':
    main()

