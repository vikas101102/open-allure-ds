# Wiki-to-Speech.py
# 20110818 Changes to enable reading http://aucklandunitarian.pagekite.me/Test20110818b
# 20110819 Tested on Mac:
# http://aucklandunitarian.pagekite.me/Test20110814
# http://aucklandunitarian.pagekite.me/Test20110819 which calls another script
# http://aucklandunitarian.pagekite.me/Test20110819b which has [path=pathToImageFiles] and
#   combined image with question
# 20110822 Added version number to input form
# 20110824 Pass __version__ to input form
#          Ensure static directory exists
# 20110825 Add __version__ to title
import cherrypy
import os.path
import Queue
import threading
import webbrowser

import forms
import objects
import scriptParser
import sys
import voice

__version__ = "0.1.9"

if not os.path.exists('static'):
    os.makedirs('static')

class WelcomePage:

    def index(self):
        # Ask for the script name.
        return forms.scriptInputFormWithErrorMessage(__version__,"")
    index.exposed = True
    webbrowser.open_new_tab('http://localhost:8080')

    def getScriptName(self, name = None):
        #name = "http://dl.dropbox.com/u/12838403/20110428a.txt"
        if name:
            if name=="exit":
                sys.exit()
            seq.sequence = scriptParser.parseScript(name)
            if seq.sequence:
                seq.onQuestion = 0
                return speakAndReturnForm()
            else:
                return forms.scriptInputFormWithErrorMessage( \
                       __version__,
                       "<i>Could not open "+name+"</i>")
        else:
            # No name was specified
            return forms.scriptInputFormWithErrorMessage( \
                       __version__,
                       "<i>Please enter a file name or link on the web.</i>")
    getScriptName.exposed = True

    def nextSlide(self):
        clearQueue()
        seq.onQuestion += 1
        if seq.onQuestion > len(seq.sequence) - 1:
            return forms.scriptInputFormWithErrorMessage(__version__,"")
        else:
            return speakAndReturnForm()
    nextSlide.exposed = True

    def nextSlideFromAnswer0(self):
        return respondToAnswer(0)
    nextSlideFromAnswer0.exposed = True

    def nextSlideFromAnswer1(self):
        return respondToAnswer(1)
    nextSlideFromAnswer1.exposed = True

    def nextSlideFromAnswer2(self):
        return respondToAnswer(2)
    nextSlideFromAnswer2.exposed = True

    def nextSlideFromAnswer3(self):
        return respondToAnswer(3)
    nextSlideFromAnswer3.exposed = True

    def nextSlideFromAnswer4(self):
        return respondToAnswer(4)
    nextSlideFromAnswer4.exposed = True

    def nextSlideFromAnswer5(self):
        return respondToAnswer(5)
    nextSlideFromAnswer5.exposed = True

    def nextSlideFromAnswer6(self):
        return respondToAnswer(6)
    nextSlideFromAnswer6.exposed = True

seq = objects.Sequence()
voiceInstance = voice.Voice()

def speakAndReturnForm():
    # Check for visited answers. If found, do not re-read question
    noVisitedAnswers = True
    for a in seq.sequence[seq.onQuestion].answers:
        if a.visited:
            noVisitedAnswers = False
    if noVisitedAnswers:
        speakList(seq.sequence[seq.onQuestion].questionTexts)
        for a in seq.sequence[seq.onQuestion].answers:
            speakList([a.answerText])
    linkToShow = seq.sequence[seq.onQuestion].linkToShow

    if linkToShow.lower().endswith(".pdf"):
        return forms.showPDFSlide(seq.sequence[seq.onQuestion].linkToShow)

    elif linkToShow.lower().endswith(".jpg") or linkToShow.lower().endswith(".png"):
        if linkToShow.startswith("Slide") or linkToShow.startswith("img") or \
           linkToShow.find("\Slide")!=-1 or linkToShow.find("/img")!=-1:
            if len(seq.sequence[seq.onQuestion].pathToImageFiles)>0:
                linkToShow = seq.sequence[seq.onQuestion].pathToImageFiles + linkToShow
            else:
                linkToShow = "static/" + linkToShow
        if len(seq.sequence[seq.onQuestion].answers)>0:
            return forms.showJPGSlideWithQuestion(linkToShow, \
                                     seq.sequence[seq.onQuestion] )
        else:
            return forms.showJPGSlide(linkToShow)

    elif linkToShow.lower().endswith(".htm"):
        return forms.showDHTML()
    elif linkToShow.lower().endswith(".swf"):
        return forms.showSWF()
    elif len(linkToShow)>0:
        #return forms.showWebsite(seq.sequence[seq.onQuestion])
        return forms.showQuestionAndWebsite(seq.sequence[seq.onQuestion])
    else: # no match for linkToShow
        return forms.showQuestion(seq.sequence[seq.onQuestion])

def respondToAnswer(n):
    clearQueue()
    response = ""
    if n<len(seq.sequence[seq.onQuestion].answers):
        # mark answer as visited
        seq.sequence[seq.onQuestion].answers[n].visited = True
        # say what there is to say
        response = seq.sequence[seq.onQuestion].answers[n].responseText
        if response != "":
            speakList([response])
        # follow any response side link
        responseSideLink = seq.sequence[seq.onQuestion].answers[n].responseSideLink
        if len(responseSideLink)>0:
            seq.sequence = scriptParser.parseScript(responseSideLink)
            if seq.sequence:
                seq.onQuestion = 0
                return speakAndReturnForm()
            #TODO error recovery
        # move to whichever question comes next
        if seq.sequence[seq.onQuestion].answers[n].action != 0:
            seq.onQuestion += seq.sequence[seq.onQuestion].answers[n].action
    if seq.onQuestion<len(seq.sequence):
        return speakAndReturnForm()
    else:
        # past end of sequence
        speakList(["You have reached the end. Please select another script."])
        return forms.scriptInputFormWithErrorMessage(__version__,"")

def clearQueue():
    while not q.empty():
        q.get()

def worker():
    while True:
        text = q.get()
        voiceInstance.speak(text, "")
        q.task_done()

q = Queue.Queue()
t = threading.Thread(target=worker)
t.daemon = True
t.start()

def speakList(textList):
    for item in textList:
        q.put(item)
    #q.join()       # block until all tasks are done

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                        'server.socket_port': 8080,
                        'server.thread_pool': 10,
                       })
    config = {'/': {'tools.staticdir.root': os.path.abspath(os.curdir)},
              '/static':{'tools.staticdir.on':True,
                         'tools.staticdir.dir':"static"}}
    cherrypy.quickstart(WelcomePage(), config=config)

