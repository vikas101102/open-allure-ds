# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
qsequence.py
a component of openallure.py

Parses separate content file into question sequence object

**Usage**

QSequence( *filename* ) returns a question sequence object

*filename* can be either a local file or a URL containing preformatted text

An input file is a plain text file with the format::

   [ tag ]
   [ configuration overrides ]
   Question part1
   { optional Question part2 }
   { optional blank line }
   Answer 1 <separator> Response 1
   Answer 2 <separator> Response 2
    etc ...
   up to 6 answers
   { blank line }
   Next question ...

where configuration overrides can be::

   smile            image to use for smiling avatar
   talk             image to use for talking avatar
   listen           image to use for listening avatar
   stickyBrowser    0/False = no pause while viewing Browser (voice over), 1/True = pause until gain focus

where Answer can be::

   [link label]     to open link in separate browser when label is selected
   [input]          to enable user input
   [next]           to enable user input, but only until an automatic "page turn"

where <separator> can be::

   ;                no action
   ;; or ;1 or ;+1  advance to next question
   ;-1              return to prior question ( in order exposed in sequence )
   ;;; or ;2 or ;+2 advance two questions
   ;[tag]           advance to question marked with tag
   ;[filename]      advance to first question found in filename
   ;[url]           advance to first question found in text marked <pre> </pre> at URL (webpage)

In addition, an input file can specify string matching rules of the form::

   [type of rule]
   [[name of rule]]
   re=
   example=
   reply=

where::

   #     [Section: type of rule]
   #        The type of rule determines which block of code in chat.py
   #        will be used to process the parsed string.  All the rules of
   #        a given type can be listed in a section.
   #
   #     [[Sub-section: name of rule]]
   #         Each rule should have a unique name.  This name can be
   #         posted to the log so it can be worked out which rule fired
   #         and led to the observed behaviour of Open Allure.
   #
   #     example =
   #         (optional)
   #         NOTE: If left out, there must be a regular expression (below)
   #         Example question from which Open Allure derives a regular expression.
   #         Strings which must be matched are enclosed in brackets.
   #         For instance,
   #
   #         example = "Who is alan [turing]?"
   #
   #         should be converted to the regular expression
   #
   #         re = '(.*)(turing)(.*)'
   #
   #         which would lead to matches on all sorts of inputs, including
   #         "Tell me about Turing."
   #         "What is the Turing Test?"
   #         "Was Turing gay?"
   #
   #         This brings up the issue of rule ORDER.
   #         More specific matches need to come first, so if you want
   #         something special in response to
   #         "What is the [Turing Test]?"
   #         that rule must come BEFORE the response to
   #         "Who is Alan [Turing]?"
   #         or else the Turing Test rule will never fire.
   #
   #     re =
   #         (optional)
   #         NOTE: If an example (above) exists, this overrides it.
   #         Regular expression used to match against input string
   #         For instance,
   #
   #         re = '(.*)(turing|loebner)(.*)'
   #
   #         where the vertical bar indicates OR
   #
   #     reply =
   #         Reply from Open Allure
   #         Triple quoted strings allow for multi-line scripts here.
   #
   #         In other words, the reply can include an entire
   #         question sequence, not merely a direct answer.
   #
   #         Open Allure stands out from other chatbots with this capability.
   #         Scripts allow Open Allure to take some of the initiative and
   #         guide the conversation in a particular direction or offer alternatives.
   #

See `Open Allure wiki Rule File Syntax`_ for details and examples.

.. _Open Allure wiki Rule File Syntax: http://code.google.com/p/open-allure-ds/wiki/RuleFileSyntax


**Output**

List of lists::

   #   [   The whole sequence of questions is outermost list,
   #                             so seq[ 0 ] is everything about the first question
   #    [  The parts of the a question including the question set, answer set, response set and action/destination sets are the next level list,
   #                             so seq[ ][ 0 ] is the question set
   #                                seq[ ][ 1 ] is the answer set
   #                                seq[ ][ 2 ] is the response set
   #                                seq[ ][ 3 ] is the action set
   #                                seq[ ][ 4 ] is the action set destinations (Response-side filenames or URLs for new questions)
   #                                seq[ ][ 5 ] is the links set (Answer-side filenames or URLs to open in browser)
   #                                seq[ ][ 6 ] is the input set
   #     [ The parts of the question are the next level list,
   #                             so seq[ ][ 0 ][ 0 ] is the first part of the question, for example "What color"
   #                            and seq[ ][ 0 ][ 1 ] is the next  part of the question, for example "is the sky?" ],
   #     [ The answers are the next list,
   #                             so seq[ ][ 1 ][ 0 ] is the first  answer, for example "Black"
   #                            and seq[ ][ 1 ][ 1 ] is the second answer, for example "Blue" ],
   #     [ The response are the next list,
   #                             so seq[ ][ 2 ][ 0 ] is the first  response, for example "Yes, at night."
   #                            and seq[ ][ 2 ][ 1 ] is the second response, for example "Yes, during the day." ],
   #     [ The actions are the next list,
   #                             so seq[ ][ 3 ][ 0 ] is the first  action, for example 0 ( meaning take no action )
   #                            and seq[ ][ 3 ][ 1 ] is the second action, for example 1 ( meaning advance one question ) ],
   #     [ The destinations are the next list,
   #                             so seq[ ][ 4 ][ 0 ] is the first  destination, for example 'secondSetOfQuestions.txt'
   #                            and seq[ ][ 4 ][ 1 ] is the second destination, for example 'http://bit.ly/openalluretest' ]]]
   #     [ The links are the next list,
   #                             so seq[ ][ 5 ][ 0 ] is the first  link, for example 'http://movieToWatch'
   #                            and seq[ ][ 5 ][ 1 ] is the second link, for example 'slidecastToWatch' ]]]
   #     [ The input flags are the next list,
   #                             so seq[ ][ 6 ][ 0 ] is the first  input, for example 0 (indicating no input on this answer)
   #                            and seq[ ][ 6 ][ 1 ] is the second link, for example 1 (indicating input allowed on this answer)
   #     Special case for photos    seq[0][ 7 ] is list of smile/talk/listen photo names
   #     [ The tag strings are next,
   #                             so seq[ ][ 8 ] is a unicode string tag for the question, for example u'skip to here'
   #     [ The stickyBrowser flags are the next list,
   #                             so seq[ ][ 9 ][ 0 ] determines the behavior of the link http://movieToWatch'   
   #     [ The visited flags are the next list,
   #                             so seq[0][10 ][0] tells whether the first answer has been picked in the past
   #     Special case for flashcard question number (NOT a list)
   #                             so Seq[0][11 ] tells what question number in the original sequence gave this flashcard question
   #     Special case for rules     seq[0][12 ] is a tuple with any script-specific rules
   
See `Open Allure wiki Separate Content File Syntax`_ for details and examples.

.. _Open Allure wiki Separate Content File Syntax: http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""

QUESTION = 0
ANSWER = 1
RESPONSE = 2
ACTION = 3
DESTINATION = 4
LINK = 5
INPUTFLAG = 6
#PHOTOS = 7
TAG = 8
STICKY = 9
VISITED = 10
FLASHCARD = 11
RULE = 12

import gettext
import htmlentitydefs
import os
import re
from string import Template
import sys
import urllib2

from BeautifulSoup import BeautifulSoup          # For processing HTML
from configobj import ConfigObj


##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
#
# From Fredrik Lundh, http://effbot.org/zone/re-sub.htm#unescape-html


                
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class QSequence( object ):
    """A Question Sequence contains (multiple) question blocks consisting of a question with answers/responses/actions"""

    def __init__( self, filename=u"openallure.txt", path='', nltkResponse=None, dictionary={}):
        """
        Read either a local plain text file or text tagged <pre> </pre> from a webpage or body of an Etherpad
        """
        self.dictionary = dictionary.copy()
         
        config = ConfigObj("openallure.cfg", )

        # configure language for this question sequence
        # start with default from openallure.cfg (may be overridden by script)
        gettext.install(domain='openallure', localedir='locale', unicode=True)
        self.language = u'en'
        try:
            self.language = config['Options']['language']
        except KeyError:
            pass
        if len(self.language) > 0 and self.language != u'en':
            mytrans = gettext.translation(u"openallure",
                                          localedir='locale',
                                          languages=[self.language], fallback=True)
            mytrans.install(unicode=True) # must set explicitly here for Mac
            
        self.defaultAnswer = config['Options']['defaultAnswer']
        if self.defaultAnswer.lower() in [_('input'),'['+_('input')+']','['+_('input')+'];']:
            self.defaultAnswer = 'input'
        elif self.defaultAnswer.lower() in [_('next'),'['+_('next')+']','['+_('next')+'];']:
            self.defaultAnswer = 'next'
        else:
            self.defaultAnswer = ''
        self.stickyBrowser = config['Options']['stickyBrowser']
        if self.stickyBrowser.lower() in ['1','true']:
            self.stickyBrowser = 1
        else:
            self.stickyBrowser = 0
        # flashcard mode causes the first question line to become a prompt
        # and the next question line to become an answer    
        self.flashcardMode = False
        
        # find rule types from responses.cfg
        responsesConfig = ConfigObj("responses.cfg")
        self.ruleTypes = responsesConfig.sections
        self.cleanUnicodeTextStr = ''
        self.inputs = []

        # attribute storing path to sequence (excludes name)
        self.path = path

        if (filename.startswith(u"http://") or filename.startswith(u"https://") or filename.startswith(u"file://")):
            # read text tagged with <pre> </pre> from website or body of an Etherpad
            try:
                urlOpen = urllib2.urlopen( filename )
                urlText = urlOpen.read()
            except:
                print( u"Could not open %s" % filename )
                urlText = "<pre>It seems " + filename + " could not be opened.\nWhat now?\n[input];</pre>"
                
            # parse out text marked with <pre> </pre>
#            links = SoupStrainer('pre')
#            taggedPreText = [tag for tag in BeautifulSoup(urlOpen, parseOnlyThese=links)]
#          print 'taggedPreText', taggedPreText

            soup = BeautifulSoup(urlText)
            taggedPre = soup.pre
            if not str(taggedPre) == 'None':
                taggedPreStr = str(taggedPre).replace('<br />\n','\n')
                taggedPreStr = taggedPreStr.replace('<br />','\n')
                soup = BeautifulSoup(taggedPreStr)
                self.inputs = unescape(''.join(soup.pre.findAll(text=True))).splitlines()
            else:
                # If no taggedPreText, try postbody (NING)
                postbody = soup.find("div", { "class" : "postbody" })
                if not str(postbody) == 'None' and filename.find('.ning.') > -1:
                    # restore blank lines
                    postbodyStr = str(postbody).replace('<br /><br />','\n')
                    postbodyStr = postbodyStr.replace('<br/><br/>','\n')
                    postbody = BeautifulSoup(postbodyStr)
                    self.inputs = unescape('\n'.join(postbody.findAll(text=True))).splitlines()
                    # strip off leading spaces
                    self.inputs = [line.lstrip() for line in self.inputs]
                    
                elif (filename.find('etherpad.') > -1):
                    # If no taggedPreText, try Etherpad body
                    soupString = ""
                    try:
                        soupString = str(soup)
                    except UnicodeDecodeError:
                        # no luck here, give up
                        pass
                    if len(soupString) > 0:
                        self.cleanUnicodeTextStr = \
                        soupString[ soupString.find(u'"initialAttributedText":{"text"')+33 : \
                                   soupString.find(u',"attribs":')-1 ]
                        self.inputs = unescape(self.cleanUnicodeTextStr).split('\\n')

            if len(self.inputs) == 0:
                self.inputs = [_(u"Hmmm. It seems ") + filename, _(u"does not have a script"),
                           _(u"marked with preformatted text (<pre> </pre>)."),
                           _(u"What now?"),
                           _(u"[input];;")]
#                self.inputs = [_(u"What now?"),
#                           _(u"[input];;")]
            else:
                # set path attribute to be everything up to through last slash in url
                slashAt = filename.rfind( '/' ) + 1
                self.path = filename[0:slashAt]

        elif filename.startswith("nltkResponse.txt"):
            self.inputs = nltkResponse.split("\n")
            
        elif filename.endswith(".py"):  
            file = open(filename)              
            pyText = file.read()
            soup = BeautifulSoup(pyText)
            taggedPre = soup.pre
            if not str(taggedPre) == 'None':
                self.inputs = unescape(''.join(soup.pre.findAll(text=True))).splitlines()

        else:
            if filename.startswith('~/'):
                filename = os.environ['HOME'] + filename[1:]
            # read file and decode with utf-8
            raw = 0
            try:
                raw = open( filename ).readlines()
            except:
                if not filename.endswith(u'.txt'):
                    filename = filename.strip() + '.txt'
                    try:
                        raw = open( filename ).readlines()
                    except IOError:
                        pass
            if raw:
                self.inputs = []
                for line in raw:
                    self.inputs.append( unicode( line, 'utf-8' ) )
            else:
                self.inputs = [_(u"Well ... It seems ") + filename, _(u"could not be opened."),
                           _(u"What now?"),
                           _(u"[input];;")]

        # parse into sequence
        self.sequence = self.regroup( self.inputs, self.classify( self.inputs ) )


    def findSetOfTemplateFields( self, strings ):
        string = ' '.join(strings)
        # Strip out escaped $ (two $s in a row)
        # then find matches for unicode strings $field or ${field}
        # finally, make a set of the unique fields
        return set(re.findall("(?u)\${?(\w*)[}\s]",string.replace('$$','')))

    
    def classify( self, strings ):
        """
Create list of string types::

    Identify strings which contain new line only   ( type N )
    #             or start with a hash # comment   ( type C )
    #             or which contain ; or ;; markers ( type indicated by offset of separator
    #                                                     between Answer ; Response )
    #             or start with rule indicators    ( type R )
    #                [ rule type ]
    #                [[ rule name ]]
    #                re= or re =
    #                example= or example =
    #                reply= or reply =
    #             or start with http://            ( type L )
    #             or else mark as question         ( type Q )

        """
        string_types = []
        inRule = False
        inQuote = False
        priorQString = ""
        for string in strings:
            if inQuote:
                # mark as type R until closing triple quotes are found
                string_types.append( "R" )
                tripleQuoteAt = string.find('"""')
                if not tripleQuoteAt == -1:
                    inQuote = False
                    inRule = False
            else:
                if string.strip() in ["","\n","\\n"]:
                    string_types.append( "N" )
                    priorQString = ""
                elif string.startswith( "#" ):
                    string_types.append( "C" )

                elif string.startswith( "re=" ) or string.startswith( "re =" ):
                    string_types.append( "R" )
                elif string.startswith( "example=" ) or string.startswith( "example =" ):
                    string_types.append( "R" )
                elif string.startswith( "reply=" ) or string.startswith( "reply =" ):
                    string_types.append( "R" )
                    # test for triple quotes on this line
                    tripleQuoteAt = string.find('"""')
                    if tripleQuoteAt == -1:
                        # reply marks last line of rule
                        inRule = False
                    else:
                        # closing triple quotes will mark last line of rule
                        inQuote = True
                        # test for SECOND (closing) triple quotes on this line
                        if not string[tripleQuoteAt+2:].find('"""') == -1:
                            inQuote = False
                            inRule = False
                elif string.startswith( "http://" ):
                    semicolonAt = string.find( ";" )
                    if semicolonAt > 0:
                        string_types.append( str( semicolonAt ) )
                    else:
                        # An answer-side link with no square bracket
                        string_types.append( "L" )

                elif string.startswith( "[" ):
                    # This could be a rule type, rule name, question tag or answer-side link
                    if inRule:
                        # It's a rule name
                        string_types.append( "R" )
                    elif string.startswith("[["):
                        # It's a second rule name
                        string_types.append( "R" )
                    else:
                        # Check content against list of rule types
                        bracketAt = string.find( ']' )
                        maybeRuleType = string[ 1 : bracketAt ].strip()
                        if maybeRuleType in self.ruleTypes:
                            # It's a rule type
                            string_types.append( "R" )
                            inRule = True
                        else:
                            # must be question tag or answer-side link
                            semicolonAt = string.find( ";" )
                            if semicolonAt > 0:
                                string_types.append( str( semicolonAt ) )
                            else:
                                string_types.append( "Q" )

                else:
                    semicolonAt = string.find(";")
                    if semicolonAt > 0:
                        string_types.append(str(semicolonAt))
                    else:
                        if len(string) > 0:
                            if priorQString.strip().endswith('?'):
                                # next things are answers even if not marked with ;
                                string_types.append(len(string))
                            else:
                                string_types.append("Q")
                                priorQString = string
                        else:
                            string_types.append("Q")
                            priorQString = string
                            
        # for debugging, show how strings are classified
#        for index, string in enumerate(strings):
#            print string_types[index], string
        return string_types

    def regroup( self, strings, string_types ):
        """Use string_types to sort strings into
        Questions, Answers, Responses and Subsequent Actions
        and Rules"""
        onString    = 0
        sequence    = []
        question    = []
        answer      = []
        response    = []
        action      = []
        destination = []
        link        = []
        inputFlags  = []
        photos      = []
        tag         = u''
        sticky      = []
        visited     = []
        flashcard   = None
        rules       = None
        photoSmile = photoTalk = photoListen = None
        
        #TODO: Sort out templates
        setOfTemplateFields = self.findSetOfTemplateFields(strings)
        setOfDictionaryFields = set(self.dictionary.keys())
        setOfMissingFields = (setOfTemplateFields - setOfDictionaryFields)
        for templateField in list(setOfMissingFields):
            additionToDictionary = {str(templateField) : 'placeholder'}
            self.dictionary.update(additionToDictionary)
        
        # substitute dictionary values into template
        for index, string in enumerate(strings):
            pattern = Template(string)
            try:
                strings[index] = pattern.substitute(self.dictionary)
            except ValueError:
                # if there is something unrecognizable, just ignore it for now
                pass
            
        onQuestion = 0
        while onString < len( strings ):
            if string_types[ onString ] == "Q":
                # check for tags and configuration overrides (which use =)
                if strings[ onString ].startswith('['):
                    if strings[ onString ].find( '=' ) == -1:
                        # this is a tag
                        # Add prior question to sequence, if any
                        if len(question)>0:
                            if not len(answer):
                                answer.append(_(u'[next]'))
                                response.append(u'')
                                action.append(1)
                                destination.append(u'')
                                link.append(u'')
                                inputFlags.append(1)
                                sticky.append(self.stickyBrowser)
                                visited.append(0)
                            sequence.append( [question, answer, response, action,
                                              destination, link, inputFlags, photos, tag, sticky, visited, flashcard] )
                            onQuestion += 1
                            question    = []
                            answer      = []
                            response    = []
                            action      = []
                            destination = []
                            link        = []
                            inputFlags  = []
                            photos      = []
                            sticky      = []
                            visited     = []
                            flashcard   = None
                        bracketAt = strings[ onString ].find( ']' )
                        tag = strings[ onString ][ 1 : bracketAt ]
                    else:
                        # this is a configuration override
                        # strip [ and ] and then split on =
                        bracketAt = strings[ onString ].find( ']' )
                        configItem, configValue = \
                           strings[ onString ][ 1 : bracketAt ].split( '=' )
                        configItem = configItem.strip().lower()
                        configValue = configValue.strip().lower()
                        if configItem == 'smile':
                            photoSmile = configValue.strip()
                        elif configItem == 'talk':
                            photoTalk = configValue.strip()
                        elif configItem == 'listen':
                            photoListen = configValue.strip()

                        if isinstance( photoSmile, unicode ) and \
                           isinstance( photoTalk, unicode ) and \
                           isinstance( photoListen, unicode ):
                            photos.append( photoSmile )
                            photos.append( photoTalk )
                            photos.append( photoListen )
                            del photoSmile, photoTalk, photoListen

                        if configItem == 'language':
                            self.language = configValue
                            if len(self.language) > 0:
                                mytrans = gettext.translation(u"openallure",
                                                              localedir='locale',
                                                              languages=[self.language], fallback=True)
                                mytrans.install(unicode=True) # must set explicitly here for mac
                                #print _('Language is %s') % self.language

                        # possible override of default stickyBrowser (at question level)
                        if configItem == 'stickybrowser':
                            if configValue.strip().lower() in ['1','true']:
                                self.stickyBrowser = 1
                            elif configValue.strip().lower() in ['0','false']:
                                self.stickyBrowser = 0
                                
                        if configItem == 'flashcard':
                            if configValue.strip().lower() in ['1','true','on']:
                                self.flashcardMode = 1
                            elif configValue.strip().lower() in ['0','false','off']:
                                self.flashcardMode = 0
                            
                # if in flashcard mode, next line needs to be marked Q as well, 
                # although it is really an answer.
                # Both lines will be consumed.
                elif self.flashcardMode == True and \
                     onString < len(string_types) - 1 and \
                     string_types[ onString + 1 ] == "Q":
                    # first add current Q 
                    question.append( strings[ onString ].rstrip() )
                    # make this into a flashcard answer
                    answer.append( _(u'[flashcard]') )
                    # add next Q as response to an answer
                    response.append(strings[ onString + 1 ].rstrip() )
                    # and skip it in next pass through loop
                    onString += 1
                    action.append(1)
                    destination.append(u'')
                    link.append(u'')
                    inputFlags.append(1)
                    sticky.append(0)
                    visited.append(0)
                    flashcard = onQuestion
                    
                # check if next string is a link
                # if so, this Q is really an A and will consume both lines
                elif onString < len(string_types) - 1 and string_types[ onString + 1 ] == "L":
                    answer.append( '[' + strings[ onString ].strip() + ']' )
                    response.append(u'')
                    action.append(1)
                    destination.append(u'')
                    link.append( strings[ onString + 1 ].strip() )
                    inputFlags.append(0)
                    sticky.append(self.stickyBrowser)
                    visited.append(0)
                else:
                    question.append( strings[ onString ].rstrip() )
            elif string_types[ onString ] == "N":
                # add a default response if no subsequent response is provided
                # (also test whether next or final types are N)
                nextOrFinalType = string_types[ min( onString + 1, len(string_types) - 1) ]
                if len(question) and not len(answer) and \
                not self.defaultAnswer == '' and \
                nextOrFinalType == 'Q':
                    if self.defaultAnswer == 'next':
                        answer.append(_(u'[next]'))
                        response.append(u'')
                        action.append(1)
                        destination.append(u'')
                        link.append(u'')
                        inputFlags.append(1)
                        sticky.append(self.stickyBrowser)
                        visited.append(0)
                    elif self.defaultAnswer == 'input':
                        answer.append(_(u'[input]'))
                        response.append(u'')
                        action.append(0)
                        destination.append(u'nltkResponse.txt')
                        link.append(u'')
                        inputFlags.append(1)
                        sticky.append(self.stickyBrowser)
                        visited.append(0)
                # signal for end of question IF there are responses
                if len(response):
                    # add to sequence and reset
                    if len(question) == 0:
                        question.append(u'')
                    sequence.append( [question, answer, response, action,
                                      destination, link, inputFlags, photos, tag, sticky, visited, flashcard] )
                    onQuestion += 1
                    question    = []
                    answer      = []
                    response    = []
                    action      = []
                    destination = []
                    link        = []
                    inputFlags  = []
                    photos      = []
                    tag         = u''
                    sticky      = []
                    visited     = []
                    flashcard   = None
                    rules       = []
            elif string_types[ onString ] == "C":
                # skip over comment strings
                pass
            elif string_types[ onString ] == "L":
                # skip over link strings (used by prior answer)
                pass
            elif string_types[ onString ] == "R":
                # collect script-based rules
                rules.append( strings[ onString ] )
            else:
                # use number to break string into answer and response
                answerString = strings[ onString ][ :int( string_types[ onString ] ) ].rstrip()

                # examine answerString to determine if it contains
                # 1/ an [input] instruction
                # 2/ a link in the wiki format [link label]
                linkString = u''
                inputFlag = 0
                if answerString.startswith(_(u'[input]')):
                    # no text will be displayed until the user types it,
                    # but the instruction can be passed through as the answer string
                    # to serve as a prompt
                    label = _(u'[input]')
                    inputFlag = 1
                elif answerString.startswith(_(u'[next]')):
                    # no text will be displayed until the user types it,
                    # but the instruction can be passed through as the answer string
                    # to serve as a prompt
                    label = _(u'[next]')
                    inputFlag = 1
                elif answerString.startswith(u'['):
                    spaceAt = answerString.find(u' ')
                    closeBracketAt = answerString.find(u']')
                    # The syntax only has a chance of being correct if the space comes before the closing bracket
                    if spaceAt > 0 and closeBracketAt > 0 and spaceAt < closeBracketAt:
                        linkString = answerString[ 1 : spaceAt]
                        label = u'[' + answerString[ spaceAt + 1 : ]
                    else:
                        # If a space is not found between the brackets AND
                        # the string did not match the translated values of [input] or [next]
                        # then we are probably trying to make Open Allure work in the wrong language
                        print( _(u"Incorrect syntax in answer on line ") + "%(onString)d: %(answerString)s " % 
                               {"onString" : onString + 1, "answerString" :answerString } )
                        print( _(u"This is probably due to your language setting") + " (%s)" % self.language)
                        sequence = []
                        sequence.append( [ [_(u'Sorry. There is a problem with line') + ' ' + str(onString+1) + _(u' of the script.'),
                                            _(u'The line reads'),
                                            answerString], \
                                           [_(u'Discuss some possible solutions'),_(u'[input]')],
                                           [u'',u''],
                                           [0,0],
                                           [u'fixSyntax',u''],
                                           [u'',u''],
                                           [1,1],
                                           [u''], 
                                           u'',
                                           [0,0],
                                           ((u'', u'', u'', u''),) ])
                        
                        return sequence
                        # raise SystemExit
                elif answerString.startswith(u'http://'):
                    spaceAt = answerString.find(u' ')
                    # The syntax only has a chance of being correct if the space comes before the closing bracket
                    if spaceAt > 0:
                        linkString = answerString[ : spaceAt]
                        label = u'[' + answerString[ spaceAt + 1 : ] + u']'
                    else:
                        linkString = answerString
                        label = u'[' + answerString + u']'
                else:
                    label = answerString
                link.append(linkString)
                answer.append(label)
                inputFlags.append(inputFlag)
                sticky.append(self.stickyBrowser)
                visited.append(0)

                # NOTE: +1 means to leave off first semi-colon
                responseString = strings[ onString ][ int( string_types[ onString ] ) + 1: ].strip()
                # catch answers with no marking
                if responseString == '':
                    responseString = ';'

                # examine start of responseString to determine if it signals action
                # with additional ;'s or digits ( including + and - ) or brackets
                # IF none found, leave action as 0
                actionValue = 0
                destinationString = u''
                while len( responseString ) and responseString.startswith(u';'):
                    actionValue += 1
                    responseString = responseString[ 1: ].lstrip()
                digits = u''
                while len( responseString ) and \
                         ( responseString[ 0 ].isdigit() or
                           responseString[ 0 ] in [u'+',u'-'] ):
                    digits += responseString[ 0 ]
                    responseString = responseString[ 1: ].lstrip()
                if len( digits ):
                    actionValue = int( digits )
                if responseString.startswith( u'[' ):
                    destinationEnd = responseString.find( u']' )
                    destinationString = responseString[ 1 : destinationEnd ].strip()
                    responseString = responseString[ destinationEnd + 1 : ].lstrip()
                    # now look at link and decide whether it is a page name
                    # that needs help to become a URL
                    # or a tag
                    if not destinationString.startswith(u'http'):
                        # do not put a path in front of a .txt file
                        if not destinationString.endswith(u'.txt'):
                            destinationString = self.path + destinationString
                            # to sort out whether this is a tag
                            # we need a complete parsing of the question sequence
                            # so this evaluation will take place in a second pass
                            # which will convert LINKS to ACTIONS when we find a link that points
                            # to a tag within the sequence
                        #print destinationString

                # If there is [input] in the answerString and no destination
                # in the responseString, default to nltkResponse.txt
                if inputFlag and len( destinationString ) == 0:
                    destinationString = u'nltkResponse.txt'

                destination.append( destinationString )
                response.append( responseString )
                action.append( actionValue )

            onString += 1

        # append last question if not already signaled by N at end of inputs
        if len( question ) > 0 or len( response ) > 0:
            if len(question) == 0:
                question.append(u'')
            if len(question) and not len(answer):
                answer.append(_(u"[input]"))
                response.append(u"")
                action.append(0)
                destination.append(u"")
                link.append(u"")
                inputFlags.append(1)
                sticky.append(self.stickyBrowser)
                visited.append(0)
            sequence.append( [question, answer, response, action,
                              destination, link, inputFlags, photos, tag, sticky, visited, flashcard] )
            onQuestion += 1

        # catch sequence with a question with no answers
        # and turn it into an input
        if len(sequence) == 0:
            sequence.append( [ [_(u'What now? Try another input.')],[_(u'[input]')],[u''],[0], \
                               [u''],[u''],[1],[],['0'],u'' ])
        if len(sequence[0][QUESTION]) == 0:
            sequence[0][QUESTION] = [_(u'[input]')]
            sequence[0][ACTION] = [0]
            sequence[0][DESTINATION] = [u'nltkResponse.txt']
            sequence[0][INPUTFLAG] = [1]
            sequence[0][STICKY] = [0]
            sequence[0][VISITED] = [0]
        # photos will not be changed if they are not found

        # Take second pass at sequence to convert LINKS to TAGS into ACTIONS
        tags = [ question[TAG] for question in sequence ]
        for qnum, question in enumerate( sequence ):
            for lnum, link in enumerate( question[DESTINATION] ):
                if not link == u'' and link[link.rfind('/') + 1:].lower() in tags:
                    # remove link
                    sequence[ qnum ][DESTINATION][ lnum ] = u''
                    # change action to RELATIVE position of question
                    # that is, how much shift from current question, qnum
                    # to tagged question
                    sequence[ qnum ][ACTION][ lnum ] = tags.index(link[link.rfind('/') + 1:].lower()) - qnum

        # build final question(s) with Contents if any
        tagWithQNumTuples = zip(tags,range(len(tags)))
        tagMap = [item for item in tagWithQNumTuples if len(item[0])>0]
        if len(tagMap)>0:
            lastQuestionNumber = len(sequence)
            sectionNamesCount = len(tagMap)
            onSectionName = 0
            for tagTuple in tagMap:
                if 0==onSectionName % 5:
                    if 0!=onSectionName:
                        # add batch of 5 to sequence with More ...
                        lastQuestionNumber += 1
                        answer.append(_(u"More ..."))
                        response.append('')
                        action.append(1)
                        destination.append('')
                        link.append('')
                        inputFlags.append(0)
                        sticky.append(0)
                        visited.append(0)
                        sequence.append( [question, answer, response, action,
                              destination, link, inputFlags, photos, tag, sticky, visited, flashcard] )
                    if 0==onSectionName:
                        question    = [_(u"Contents")]
                    else:
                        question    = [_(u"Contents ...")]
                    answer      = []
                    response    = []
                    action      = []
                    destination = []
                    link        = []
                    inputFlags  = []
                    photos      = []
                    if 0==onSectionName:
                        tag         = u'Contents'
                    else:
                        tag         = u''
                    sticky      = []
                    visited     = []
                answer.append(tagTuple[0])
                response.append('')
                action.append(tagTuple[1]-lastQuestionNumber)
                destination.append('')
                link.append('')
                inputFlags.append(0)
                sticky.append(0)
                visited.append(0)
                if onSectionName == sectionNamesCount-1:
                    # Add last batch
                    sequence.append( [question, answer, response, action,
                              destination, link, inputFlags, photos, tag, sticky, visited, flashcard] )
                onSectionName += 1
        else:
            # Add in Contents with Start link (to question 0)
            question    = []
            answer      = []
            response    = []
            action      = []
            destination = []
            link        = []
            inputFlags  = []
            photos      = []
            tag         = u''
            sticky      = []
            visited     = []
            flashcard   = None
            
            question.append("Contents")
            answer.append("Start");
            response.append('')
            action.append(-len(sequence));
            destination.append('')
            link.append('')
            inputFlags.append(0)
            sticky.append(0)
            visited.append(0)
            sequence.append( [question, answer, response, action,
                      destination, link, inputFlags, photos, tag, sticky, visited, flashcard] )

        # Parse just the lines classified as rules
        if rules:
            ruleStrings = [ str( unicodeStr ) for unicodeStr in rules ]
            scriptRules = ConfigObj( infile = ruleStrings , encoding='utf-8')
            rules = []
            for section in scriptRules.sections:
                for subsection in scriptRules[section].sections:
                    re = ""
                    reply = ""
                    rule = ()
                    # a regular expression overrides an example
                    if 're' in scriptRules[section][subsection]:
                        if 'reply' in scriptRules[section][subsection]:
                            reply = scriptRules[section][subsection]['reply']
                        else:
                            reply = '[' + subsection + ']'
                        rule = ( scriptRules[section][subsection]['re'],
                                 reply,
                                 section, subsection )
                    elif 'example' in scriptRules[section][subsection]:
                        # turn example into a regular expression
                        example = scriptRules[section][subsection]['example']
                        openBracketAt = example.find('[')
                        closeBracketAt = example.find(']', openBracketAt + 1)
                        secondOpenBracketAt = example.find('[', closeBracketAt + 1)
                        secondCloseBracketAt = example.find(']', secondOpenBracketAt + 1)
                        if openBracketAt == -1:
                            # if no brackets, use whole example as the regular expression
                            re = example
                        else:
                            firstPartRE = example[ openBracketAt + 1 : closeBracketAt ].strip()
                            re = '(' + firstPartRE + ')(.*)'
                            if openBracketAt > 0:
                                re = '(.*)' + re
                            if secondOpenBracketAt > closeBracketAt:
                                secondPartRE = example[ secondOpenBracketAt + 1 : secondCloseBracketAt ].strip()
                                re = re + '(' + secondPartRE + ')(.*)'
                        if 'reply' in scriptRules[section][subsection]:
                            reply = scriptRules[section][subsection]['reply']
                        else:
                            reply = '[' + subsection + ']'
                        rule = ( re, reply, section, subsection )
                    if reply == "" and len(scriptRules[section][subsection]['reply']) > 0:
                        # This is an ask rule with no triggering re or example
                        rule = ('', scriptRules[section][subsection]['reply'], section, subsection )
                    if not rule == ():    
                        rules.append(rule)
            sequence[ 0 ].append( tuple( rules ) )
        return sequence


if __name__ == "__main__":
    if len(sys.argv) > 1 and 0 != len(sys.argv[1]):
        seq = QSequence( sys.argv[1])
    else:
        seq = QSequence('welcome.txt')
    for question in seq.sequence:
        print '------------'
        print 'TAG         ',question[8]
        print 'QUESTION    ',question[0]
        print 'ANSWER      ',question[1]
        print 'RESPONSE    ',question[2]
        print 'ACTION      ',question[3]
        print 'DESTINATION ',question[4]
        print 'LINK        ',question[5]
        print 'INPUTFLAG   ',question[6]
        print 'PHOTOS      ',question[7]
        print 'STICKY      ',question[9]
        print 'VISITED     ',question[10]
        if len(question) > FLASHCARD:
            print 'FLASHCARD   ',question[11]
        if len(question) > RULE:
            print 'RULES       ',question[12]
