#!/usr/bin/env python
"""
# D:\Python25\20100127f.py

# JG 20100113 Tie selections to keystrokes

# JG 20091214 pygame video
# Right and left reversed with pixelArray
# Detects change in hardcoded pixels
# Grid of points in box and causes color to be scaled depending on number of grid points touched
# Parameterize placement of boxes with xoffset and yoffset
# Allow sticky selection with second selection to right
# Exclusive selection
# Combine voice with vision
# Fix vocabulary to colors
# 20091219 Tiny window
# 20100117 Put text on webcam image?
# 20100117 gestures on top of question and answer text

# Started with pygame demo camera.py

# JG 20100127 This version has the following features:
- Allows gesture control with panel of boxes: top box selects first answer
     Next idea: have gestures highlight and select answers directly
- Allows voice control with full text of answer, number or letter of answer
     Future work: try to parse dictated answers
- Allows keyboard control including number of answer, letter of answer and right/left arrow keys

- Tracks order of questions visited in stack (list variable name: problems)

TODO: Separate content file using / // syntax
"""

import pkg_resources
import dragonfly
import pygame
import pygame.camera
from pgu import text
from pygame.locals import *
from dragonfly import *

action_pending = 0

pygame.font.init()
font = pygame.font.SysFont("default", 50)

release = Key("shift:up, ctrl:up")

black = (0,0,0)
gray  = (200,200,200)
red   = (255,0,0)
white = (255,255,255)
yellow= (255,255,0)

sequence = [
            [["Part one","and two"],
             ["1","2","Three","Fourth","This also works"],
             ["Well done. Next one.",
              "Well done. Next two.",
              "Well done. Next three.",
              "Well done. Next four.",
              "Well done. Next five."],
             [1,2,3,4,5]],

            [["This tutor works","both with the keyboard","and with voice recognition.",
              "Press 1 2 3 etc.","Say one two three","or first second third","or just say your choice.",
              "For example, pick from these choices:"],
             ["1","2","Three","Fourth","This also works"],
             ["Skip 2",
              "Skip 3",
              "Skip 4",
              "Skip 5",
              "Skip 6"],
             [2,3,4,5,6]],

            [["What color is the sky","overhead at midday","on a clear and cloudless day?"],
             ["The sky is Orange",
              "The sky is Blue",
              "The sky is White",
              "The sky is Black"],
             ["Perhaps at sunset. What about midday? Try again.",
              "Correct.  Now what causes a blue sky?",
              "Perhaps near the horizon or on a cloudy day. Try again.",
              "Black is the correct answer for someone standing where there is no atmosphere. What about on the Earth?"],
             [0,1,0,0]],

            [["Is the sky blue","due to"],
             ["the color of sunlight",
              "the color of the atmosphere",
              "how our eyes see colors",
              "other (dictation)"],
             ["Yes. Sunlight contains blue light and other colors of light. But what makes the sky appear blue overhead at midday?",
              "Correct. The air around the Earth is not entirely transparent.",
              "Yes. Seeing in color is required for the sky to appear blue. But what causes a blue sky?",
              "OK. What do you think causes the blue color?" ],
             [0,1,0,99]],

            [["What happens","when light passes through air?"],
             ["Nothing. It just passes through.",
              "It bends.",
              "It is partially absorbed.",
              "Something else. (dictation)"
             ],
             ["Yes, this lets us see long distances through clear air. But something must happen to cause blue light to come from the sky.",
              "Close. The light coming from the sun definitely goes in a different direction when it hits the atmosphere, but why is that?",
              "Correct. The air absorbs and then radiates the blue light.",
              "OK.  What do you think happens to the light?"
             ],
             [0,0,1,99]],

              [["What word describes","what happens to the blue light in the sky?"],
             ["scattering",
              "reflecting",
              "refracting",
              "other (dictation)"],
             ["Correct. Rayleigh scattering makes the sky blue because the light is first absorbed and then radiated in different directions.",
              "Reflected light is not absorbed and so it arrives and departs at fixed angles. Try again.",
              "Refracted light is not absorbed but is bent so it travels at a different, fixed angle.  Try again.",
              "OK. What word do you think describes what happens to the light?"],
             [1,0,0,99]],

              [["How to do you like this tutor?"],
             ["A. Great!",
              "B. OK",
              "C. Useless ...",
              "D. Other (dictation)"],
             ["Cool!",
              "Your input in appreciated.",
              "Hmmm. It probably needs improving then.",
              "OK. Please say briefly how you like this tutor."],
             [1,1,1,99]],

            [["Thank you","for trying this lesson.","\n\nYou can learn more at http://","www.sciencemadesimple.com\n","/sky_blue.html"],
             ["Press Escape to Exit"],
             [],
             []]

           ]

def speak(phrase):
   #print phrase
   e = dragonfly.get_engine()
   e.speak(phrase)

   #os.system('espeak -s150 "' + phrase + '"')

def build_problem_text(problem):
   global problem_text, just_question_text, choices
   """
   problem_text[0] is question
   problem_text[1] is question + answer 1
   problem_text[2] is question + answer 1 + answer 2
   etc.
   choices tells how may answers there are
   """
   problem_text = [""]
   problem_text[0] = " ".join(problem[0]) + "\n"
   on_answer = 0
   for i in problem[1]:
      problem_text.append(problem_text[on_answer] + "\n" + i)
      on_answer += 1
   choices = on_answer
   speak(str(choices) + " found")

   # build just question in pieces (if any)
   just_question_text = [""]
   on_text = 0
   for i in problem[0]:
      just_question_text.append(just_question_text[on_text] + i + " ")
      on_text += 1
   just_question_text = just_question_text[1:]


class VideoCapturePlayer(object):

   size = ( 640, 480 )
   def __init__(self, **argd):
       self.__dict__.update(**argd)
       super(VideoCapturePlayer, self).__init__(**argd)

       # create a display surface. standard pygame stuff
       self.display = pygame.display.set_mode( self.size, 0 )

       # gets a list of available cameras.
       self.clist = pygame.camera.list_cameras()
       if not self.clist:
           raise ValueError("Sorry, no cameras detected.")

       # creates the camera of the specified size and in RGB colorspace
       self.camera = pygame.camera.Camera(self.clist[0], self.size, "RGB")

       # starts the camera
       self.camera.start()
       self.last_row = None

       self.clock = pygame.time.Clock()

       # create a surface to capture to.  for performance purposes, you want the
       # bit depth to be the same as that of the display surface.
       self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

       # initialize box state variables
       VideoCapturePlayer.box1_set=0
       VideoCapturePlayer.box2_set=0
       VideoCapturePlayer.box3_set=0
       VideoCapturePlayer.box4_set=0
       VideoCapturePlayer.box5_set=0
       VideoCapturePlayer.box6_set=0

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
       # Draw reference lines
       ar[0+xoffset:22+xoffset,22+yoffset]    = (red,blue,green)
       count = 0
       for i in range(1, 11):
          for j in range(1, 11):
             if ar[2*i+xoffset,2*j+yoffset] > 10000000:
                count += 1
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

       # gesture to right turns off state
       box1b=self.color_box(ar,xoffset+20,yoffset,color,0)
       if box1b:
          box_state=0
          # unset all boxes
          VideoCapturePlayer.box1_set=0
          VideoCapturePlayer.box2_set=0
          VideoCapturePlayer.box3_set=0
          VideoCapturePlayer.box4_set=0
          VideoCapturePlayer.box5_set=0
          VideoCapturePlayer.box6_set=0
          action_pending = 0
       return box_state

   def state(self, problem):
       """
       problem[0] is the question, protentially broken into pieces for easier reading
       problem[1] are the possible answers
       problem[2] are the actions in response to those answers
       problem[3] are the next problem in response to those answers
       """
       global silence, choice, _stated, on_text, on_answer, skip_response, _quit
       #NOTE: _stated may be reset to 0 by a check_event call
       # always start reading a new question
       #TODO: check_event call can change which problem we're on!
       silence = 0
       choice = 0
       skip_response = 0
       self.get_and_flip()
##       pygame.time.wait(1000)
       check_events()

       #read question
       on_text = 0
       for i in problem[0]:
          check_events()
          if silence or choice or _quit: break
          self.get_and_flip()
          speak(i.strip())
          on_text += 1
          on_text = min(on_text,len(problem[0])-1)

       #read answers with interrupt
       #pygame.time.wait(1000)
       on_answer = 0
       for i in problem[1]:
          check_events()
          if silence or choice or _quit: break
          on_answer += 1
          self.get_and_flip()
          # Check for answer with "A. "
          if i[1:3] == '. ':
              speak(i[3:].strip())
          else:
              speak(i.strip())

       _stated = 1

   def show_choice(self,key):
       global _stated, on_problem, problem, problem_text, _dictation, on_text, on_answer, skip_response, _quit
       #check for valid key - must be no greater than number of answers or -1
       if key == -1:
          # return to prior question
          if len(problems) >0:
              on_problem = problems.pop()
          else:
              on_problem = 0
          problem = sequence[on_problem]
          build_problem_text(problem)
          choice = 0
          _stated = 0
          return
       else:
           if key > len(problem[1]):
               # Choice is invalid, reset
               choice = 0
               return
           answer = key - 1

           if not skip_response:
               # color selected choice
               self.get_and_flip()
               #repeat answer
               if problem[1][answer][1:3] == '. ':
                      speak("You selected " + problem[1][answer][3:].strip())
               else:
                      speak("You selected " + problem[1][answer].strip())

               #check that response exists for answer
               if len(problem[2]) >= key and isinstance(problem[2][answer],str):
                  #speak response to answer
                  speak(problem[2][answer].strip())
               skip_response = 0

       # reset pointers for next question
       on_text = 0
       on_answer = 0
       VideoCapturePlayer.box1_set=0
       VideoCapturePlayer.box2_set=0
       VideoCapturePlayer.box3_set=0
       VideoCapturePlayer.box4_set=0
       VideoCapturePlayer.box5_set=0
       VideoCapturePlayer.box6_set=0
       #repaint screen to make sure all options are gray
    ##   paint(gray)
       #paint up through selected answer in red
    ##   text.writewrap(screen,font,pygame.Rect(20,20,620,460),red,problem_text[key])
       #repaint question (and first unselected answer(s) if any) gray again
    ##   text.writewrap(screen,font,pygame.Rect(20,20,620,460),gray,problem_text[key-1])
    ##   pygame.display.flip()
       #pygame.time.wait(500)

       #check that next sequence exists as integer for answer
       if key <= len(problem[3]) and isinstance(problem[3][answer],int):
          #advance in sequence
          next = problem[3][answer]
          if next == 99:
              # process input
              speak("Taking dictation")
              silence = 1
              _dictation = 1
              while _dictation: check_events()
          else:
              #speak("Current problem is "+str(on_problem).strip())
              #speak("Next problem is "+str(next).strip())
              # Add last problem to stack if moving on
              if next > 0: problems.append(on_problem)
              on_problem = on_problem + next
              problem = sequence[on_problem]
              build_problem_text(problem)
              choice = 0
       else:
           # invalid or final choice
           _quit = 1
       _stated = 0


   def get_and_flip(self):
       global action_pending, on_text, on_answer, just_question_text, choice, choices, _stated

       # if you don't want to tie the framerate to the camera, you can check and
       # see if the camera has an image ready.  note that while this works
       # on most cameras, some will never return true.
       if 0 and self.camera.query_image():
           # capture an image

           self.snapshot = self.camera.get_image(self.snapshot)
       self.snapshot = self.camera.get_image(self.snapshot)
       #self.snapshot = self.camera.get_image()

       # Manipulate the image. Flip it around the y axis.
       ar = pygame.PixelArray (self.snapshot)
       ar[:] = ar[::-1,:]

       # Count points and color boxes with set/unset
       xposition = 480
       yposition = 250
       yspacing = 25

       # Check each box from the top down
       # If any box above is set, skip boxes below
       VideoCapturePlayer.box1_set=self.set_unset(ar,xposition,0*yspacing+yposition,self.white,VideoCapturePlayer.box1_set)
       if choices > 1 and not VideoCapturePlayer.box1_set:
          VideoCapturePlayer.box2_set=self.set_unset(ar,xposition,1*yspacing+yposition,self.red,VideoCapturePlayer.box2_set)
       if choices > 2 and not (VideoCapturePlayer.box1_set or VideoCapturePlayer.box2_set):
          VideoCapturePlayer.box3_set=self.set_unset(ar,xposition,2*yspacing+yposition,self.blue,VideoCapturePlayer.box3_set)
       if choices > 3 and not (VideoCapturePlayer.box1_set or VideoCapturePlayer.box2_set or VideoCapturePlayer.box3_set):
          VideoCapturePlayer.box4_set=self.set_unset(ar,xposition,3*yspacing+yposition,self.green,VideoCapturePlayer.box4_set)
       if choices > 4 and not (VideoCapturePlayer.box1_set or VideoCapturePlayer.box2_set or VideoCapturePlayer.box3_set or VideoCapturePlayer.box4_set):
          VideoCapturePlayer.box5_set=self.set_unset(ar,xposition,4*yspacing+yposition,self.yellow,VideoCapturePlayer.box5_set)
       if choices > 5 and not (VideoCapturePlayer.box1_set or VideoCapturePlayer.box2_set or VideoCapturePlayer.box3_set or VideoCapturePlayer.box4_set or VideoCapturePlayer.box5_set):
          VideoCapturePlayer.box6_set=self.set_unset(ar,xposition,5*yspacing+yposition,self.purple,VideoCapturePlayer.box6_set)
       del ar

       # blit it to the display surface.  simple!
       self.display.blit(self.snapshot, (0,0))

       # paint words on it with appropriate colors
       # If not stated, start with all black
       print "In get_and_flip (_stated/p/choice):" + str(_stated) + " " + str(on_problem) + " " + str(choice)
       if not _stated:
           text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.black,problem_text[-1])

           if on_answer == 0:
              # paint as much gray as needed on question
              text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,just_question_text[on_text])
           else:
              # or paint as much gray as needed on answers
              print "on answer" + str(on_answer)
              text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,problem_text[on_answer])

       # else start with all gray
       else:
           text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,problem_text[-1])

           # If choice made, paint it red, but everything before it gray
           if choice > 0 and choice <= len(problem_text)-1:
              text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.red,problem_text[choice])
              text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,problem_text[choice-1])
           else:
               # If choice highlighted, paint it yellow, but everything before it gray
               if highlight > 0:
                  text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.yellow,problem_text[highlight])
                  text.writewrap(self.display,font,pygame.Rect(20,20,620,460),self.gray,problem_text[highlight-1])

       pygame.display.flip()

       # Set box logic
       # Use action_pending flag to avoid duplicate actions
       if not action_pending:
           if VideoCapturePlayer.box1_set:
              VideoCapturePlayer.box1_set=0
              action_pending = 1
              action = Key("1")
              print "Key 1 pressed"
              action.execute()
              release.execute()

           if VideoCapturePlayer.box2_set:
              VideoCapturePlayer.box2_set=0
              action_pending = 1
              action = Key("2")
              print "Key 2 pressed"
              action.execute()
              release.execute()

           if VideoCapturePlayer.box3_set:
              VideoCapturePlayer.box3_set=0
              action_pending = 1
              action = Key("3")
              print "Key 3 pressed"
              action.execute()
              release.execute()

           if VideoCapturePlayer.box4_set:
              VideoCapturePlayer.box4_set=0
              action_pending = 1
              action = Key("4")
              print "Key 4 pressed"
              action.execute()
              release.execute()

           if VideoCapturePlayer.box5_set:
              VideoCapturePlayer.box5_set=0
              action_pending = 1
              action = Key("5")
              print "Key 5 pressed"
              action.execute()
              release.execute()

           if VideoCapturePlayer.box6_set:
              VideoCapturePlayer.box6_set=0
              action_pending = 1
              action = Key("6")
              print "Key 6 pressed"
              action.execute()
              release.execute()

   def main(self):
       global _stated, choice, _quit
       while not _quit:
          self.get_and_flip()
          if not _stated:
               self.state(problem)
          check_events()
          # Note: negative choice can change problem as well
          if not choice == 0:
              self.show_choice(choice)
          self.clock.tick()
          # print (self.clock.get_fps())

e = dragonfly.get_engine()
#e.speak("Hello")
grammar = Grammar("voice mirror")

class SpeakRule(CompoundRule):
    spec = "<text>"
    extras = [Dictation("text")]

    def _process_recognition(self, node, extras):
        # stop reading
        global silence, choice, _dictation, on_problem, problem, sequence, _stated
        silence = 1

        # repeat voice recognition
        answer = " ".join(node.words())
        answer1 = node.words()[0]
        speak("You said %s!" % answer)

        if _dictation == 0:
            # check for valid answer (see if words match)
            on_answer = 0
            match = 0
            for i in problem[1]:
                on_answer += 1
                #check against available answers - in lower case without punctuation
                # and allow first part only (eg "Yes." in "Yes. I agree.")
                # or first word
                answer = answer.lower().strip('.')
                if answer == i.lower().strip('.?') or answer == i.lower().split('.')[0] or answer == i.lower().split()[0]:
                   choice = on_answer
                   match = 1
            if not match:
                #check first word against number words
                on_answer = 0
                for i in ["one","two","three","four","five","six"]:
                    on_answer += 1
                    if answer1 == i:
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
                #check against control words
                for i in ["next","skip"]:
                   if answer == i:
                      silence = 1
                      on_problem += 1
                      # avoid stepping past end of sequence
                      on_problem = min(on_problem,len(sequence)-1)
                      speak("Advancing to question " + str(on_problem) )
                      problem = sequence[on_problem]
                      build_problem_text(problem)
                      choice = 0
                      _stated = 0
                      _dictation = 0
                      match = 1
            if not match:
                for i in ["back","prior","previous"]:
                   if answer == i:
                      silence = 1
                      on_problem -= 1
                      # avoid negative index
                      on_problem = max(on_problem,0)
                      speak("Returning to question " + str(on_problem) )
                      problem = sequence[on_problem]
                      build_problem_text(problem)
                      choice = 0
                      _stated = 0
                      match = 1

            if not match:
                speak("Try again.")
        else:
            speak("Thank you. Let's move on.")
            on_problem = on_problem + 1
            # avoid stepping past end of sequence
            on_problem = min(on_problem,len(sequence)-1)
            problem = sequence[on_problem]
            build_problem_text(problem)
            choice = 0
            _dictation = 0

grammar.add_rule(SpeakRule())    # Add the top-level rule.
grammar.load()                   # Load the grammar.

def check_events():
    """
    on_problem points to problem in sequence by number
    problem is structure holding the question, answers, responses to answers and subsequent actions
    problems is a list for tracking which problems were seen
    choice tells which answer is selected
    _stated is a flag to indicate whether the problem needs to be read out
    _quit is a flag telling whether to quit
    silence is a flag to silence text-to-speech
    skip_response is a flag to allow fast forwarding
    _dication is a flag indicating whether dication mode is on
    highlight is the number of the choice that should be highlighted
    highlight_on is a flag telling whether to apply highlights
    on_answer is a pointer to help coordinate the display of answers with the text-to-speech reading of them
    on_text is a pointer to help coordinate the display of parts of the question with text-to-speech reading
    """
    global on_problem, problem, problems, choice, _stated, _quit, silence, _dictation, skip_response
    global highlight, highlight_on, on_answer, on_text, _quit
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

           # Quality control on choice: reset choices beyond valid list
           if choice > len(problem[1]):
               choice = 0
               speak("Note there are only " + str(len(problem[1])) + " choices")

           # Right arrow advances in question sequence
           if e.type is KEYDOWN and e.key == K_RIGHT:
              silence = 1
              on_text = 0
              on_answer = 0
              skip_response = 1

              # Choice is first non-zero entry in problem[3]
              on_choice = 0
              for i in problem[3]:
                  on_choice += 1
                  if i > 0:
                      choice = on_choice
                      speak("On question " + str(on_problem + i))
                      break

           # Left arrow backs up in question sequence
           if e.type is KEYDOWN and e.key == K_LEFT:
              silence = 1
              on_text = 0
              on_answer = 0
              choice = -1
              if len(problems) > 0:
                  speak("On question " + str(problems[-1]))
              else:
                  on_problem = 0

           # Up arrow highlights prior answer (or wraps last answer)
           if e.type is KEYDOWN and e.key == K_UP:
              silence = 1
              highlight_on = 1
              if highlight == 0 or highlight == 1:
                  highlight = len(problem[1])
              else:
                  highlight -= 1

           # Down arrow highlights next answer (or wraps to first answer)
           if e.type is KEYDOWN and e.key == K_DOWN:
              silence = 1
              highlight += 1
              highlight_on = 1
              if highlight > len(problem[1]): highlight = 1

           # Enter key selected highlighted answer, if any
           if e.type is KEYDOWN and e.key == K_RETURN:
              if highlight > 0:
                 choice = highlight

       # Escape key sets flag to quit
       if e.type is KEYDOWN and e.key == K_ESCAPE:
          _quit = 1

       # Spacebar sets flag to silence voice
       if e.type is KEYDOWN and e.key == K_SPACE:
          silence = 1

       print "check_events (p/c/_stated) " + str(on_problem) + " " + str(choice) + " " + str(_stated)
    else:
         return 0

# initialize
on_problem = 0
problem = sequence[on_problem]

problem_text = [""]
just_question_text = [""]

choices = 0
build_problem_text(problem)
silence = 0
choice = 0
_quit = 0
_stated = 0
_dictation = 0
highlight = 0
highlight_on = 0

action_pending = 0
on_text = 0
on_answer = 0

skip_response = 0

# List of problems numbers in sequence
problems = []


def main():
    pygame.init()
    pygame.camera.init()
    videoPlayer = VideoCapturePlayer().main()
    pygame.quit()

if __name__ == '__main__':
    main()
