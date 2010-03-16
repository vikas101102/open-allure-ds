"""
qsequence.py
a component of openallure.py

Parses separate content file

**Usage**

QSequence( *filename* ) returns a question sequence object

*filename* can be either a local file or a URL

An input file is plain text with the format::

   Question part1
   [ optional Question part2 ]
   [ optional blank line ]
   Answer 1 <separator> Response 1
   Answer 2 <separator> Response 2
    etc ...
   up to 6 answers
   [ blank line ]
   Next question ...

where Answer can be::

   [link label]     to open link in separate browser when label is selected
   [input]          to enable user input

where <separator> can be::

   ;                no action
   ;; or ;1 or ;+1  advance to next question
   ;-1              return to prior question ( in order exposed in sequence )
   ;;; or ;2 or ;+2 advance two questions
   ;[filename]      advance to first question found in filename
   ;[url]           advance to first question found in text marked <pre> </pre> at URL (webpage)


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
   #     [ The inputs are the next list,
   #                             so seq[ ][ 6 ][ 0 ] is the first  input, for example 0 (indicating no input on this answer)
   #                            and seq[ ][ 6 ][ 1 ] is the second link, for example 1 (indicating input allowed on this answer)

See `Open Allure wiki`_ for details and examples.

.. _Open Allure wiki: http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

import ConfigParser
import urllib
import os
from BeautifulSoup import BeautifulSoup, SoupStrainer          # For processing HTML

class QSequence( object ):
    """A Question Sequence contains (multiple) question blocks consisting of a question with answers/responses/actions"""

    def __init__( self, filename="openallure.txt", path='' ):
        """
        Read either a local plain text file or text tagged <pre> </pre> from a webpage
        """
        # attribute storing path to sequence (excludes name)
        self.path = path

        if filename.startswith("http://"):
           # read text tagged with <pre> </pre> from website
           try:
              urlOpen = urllib.urlopen( filename )
           except urlOpenError:
              print( "Could not open %s" % filename )

           # parse out text marked with <pre> </pre>
           links = SoupStrainer('pre')
           taggedPreText = [tag for tag in BeautifulSoup(urlOpen, parseOnlyThese=links)]
#           print 'taggedPreText', taggedPreText

           # filter out <pre> and any other embedded tags
           def isunicode(x): return isinstance(x,unicode)
           def lstrip(x): return x.lstrip()
#           def notEmpty(x):
#              if len(x) > 0 : return True
           cleanUnicodeText = [ map( lstrip, filter( isunicode, taggedPreText[ x ].contents ) )  for x in range( 0, len( taggedPreText ) ) ]

           # get it all down to one text string
           cleanUnicodeTextStr = "\n".join(["\n".join(list) for list in cleanUnicodeText])

           if len(cleanUnicodeTextStr) == 0:
##              print( "\n\n   No text marked with <pre> </pre> found at %s" % filename )
##              print( "   Check view source for &lt;pre&gt; which is currently not supported.\n\n" )
##              os.sys.exit()
               inputs = ["Hmmm. It seems " + url,"does not have a script","marked with <pre> </pre>.","What now?","[input];;"]
           else:
               # split back into lines (inputs)
               inputs = cleanUnicodeTextStr.splitlines()

               # set path attribute to be everything up to through last slash in url
               slashAt = filename.rfind( '/' ) + 1
               self.path = filename[0:slashAt]

        else:
           # read file
           try:
               inputs = open( filename ).readlines()
           except IOError:
               inputs = ["Well, it seems " + filename,"could not be opened.","What now?","[input];;"]

        # parse into sequence
        self.sequence = self.regroup( inputs, self.classify( inputs ) )

    def classify( self,strings ):
        """
        Create list of string types::

        Identify strings which contain new line only   ( type N )
        #             or which contain ; or ;; markers ( type indicated by offset of marker between Answer ; Response )
        #             or else mark as question         ( type Q )

        """
        string_types = []
        for i in strings:
            if i.strip() in ["","\n","\\n"]:
                string_types.append( "N" )
            else:
               slash_at = i.find( ";" )
               if slash_at > 0:
                   string_types.append( str( slash_at ) )
               else:
                   string_types.append( "Q" )
#            print i, string_types[-1]
        return string_types

    def regroup( self,strings,string_types ):
        """Use string_types to sort strings into Questions, Answers, Responses and Subsequent Actions"""
        onString    = 0
        sequence    = []
        question    = []
        answer      = []
        response    = []
        action      = []
        destination = []
        link        = []
        inputFlags  = []
        while onString < len( strings ):
            if string_types[ onString ] == "Q": question.append( strings[ onString ].rstrip() )
            elif string_types[ onString ] == "N":
                # signal for end of question IF there are responses
                if len( response ):
                    # add to sequence and reset
                    sequence.append( [question, answer, response, action, destination, link, inputFlags] )
                    question    = []
                    answer      = []
                    response    = []
                    action      = []
                    destination = []
                    link        = []
                    inputFlags  = []
            else:
                # use number to break string into answer and response
                answerString = strings[ onString ][ :int( string_types[ onString ] ) ].rstrip()

                # examine answerString to determine if it contains
                # 1/ an [input] instruction
                # 2/ a link in the wiki format [link label]
                linkString = ""
                inputFlag = 0
                if answerString.startswith('[input]'):
                    # no text will be displayed until the user types it,
                    # but the instruction can be passed through as the answer string to serve as a prompt
                    label = "[input]"
                    inputFlag = 1
                elif answerString.startswith('['):
                    spaceAt = answerString.find(' ')
                    closeBracketAt = answerString.find(']')
                    # The syntax only has a chance of being correct if the space comes before the closing bracket
                    if spaceAt > 0 and closeBracketAt > 0 and spaceAt < closeBracketAt:
                       linkString = answerString[ 1 : spaceAt]
                       label = '[' + answerString[ spaceAt + 1 :  ]
                    else:
                       print( "Incorrect syntax in answer: %s " % answerString )
                else:
                    label = answerString
                link.append( linkString )
                answer.append( label )
                inputFlags.append( inputFlag )

                # NOTE: +1 means to leave off first semi-colon
                responseString = strings[ onString ][ int( string_types[ onString ] ) + 1: ].strip()

                # examine start of responseString to determine if it signals action
                # with additional ;'s or digits ( including + and - ) or brackets
                # IF none found, leave action as 0
                actionValue = 0
                linkString = ''
                while len( responseString ) and responseString.startswith(';'):
                    actionValue += 1
                    responseString = responseString[ 1: ].lstrip()
                digits = ''
                while len( responseString ) and ( responseString[ 0 ].isdigit() or responseString[ 0 ] in ['+','-'] ):
                    digits += responseString[ 0 ]
                    responseString = responseString[ 1: ].lstrip()
                if len( digits ): actionValue = int( digits )
                if responseString.startswith('['):
                    linkEnd = responseString.find(']')
                    linkString    = responseString[1:linkEnd]
                    responseString = responseString[ linkEnd + 1: ].lstrip()
                    actionValue = 88
                    # now look at link and decide whether it is a page name that needs help to become a URL
                    if not linkString.startswith("http"):
                        # do not put a path in front of a .txt file
                        if not linkString.endswith('.txt'):
                            linkString = self.path + linkString
                        #print linkString

##                # If there is [input] in the answerString and no destination in the responseString, default to aimlResponse.txt and actionValue=88
##                if inputFlag and len( linkString ) == 0:
##                    linkString = 'aimlResponse.txt'
##                    actionValue = 88
                # If there is [input] in the answerString and no destination in the responseString,
                # default to nltkResponse.txt and actionValue=88
                if inputFlag and len( linkString ) == 0:
                    linkString = 'nltkResponse.txt'
                    actionValue = 88

                destination.append( linkString )
                response.append( responseString )
                action.append( actionValue )

            onString += 1

        # append last question if not already signaled by N at end of inputs
        if len( question ): sequence.append( [question, answer, response, action, destination, link, inputFlags] )

        # catch sequence with a question with no answers and turn it into an input
        if len(sequence[0][1]) == 0:
            sequence[0][1] = ['[input]']
            sequence[0][3] = [88]
            sequence[0][4] = ['nltkResponse.txt']
            sequence[0][6] = [1]

        return sequence
