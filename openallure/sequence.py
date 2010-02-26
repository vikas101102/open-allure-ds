"""
sequence.py
a component of openallure.py

Parses separate content file

**Usage**

sequence(filename) returns a sequence object

An input file is plain text with the format::

   Question part1
   [optional Question part2]
   [optional blank line]
   Answer 1 <separator> Response 1
   Answer 2 <separator> Response 2
    etc ...
   up to 6 answers
   [blank line]
   Next question ...

where <separator> can be::

   ;                no action
   ;; or ;1 or ;+1  advance to next question
   ;-1              return to prior question (in order exposed in sequence)
   ;;; or ;2 or ;+2 advance two questions


**Output**

List of lists::

   #   [   The whole sequence of questions is outermost list,
   #                             so seq[0] is everything about the first question
   #    [  The parts of the a question including the question set, answer set, response set and action set are next level list,
   #                             so seq[ ][0] is the question set
   #                                seq[ ][1] is the answer set
   #                                seq[ ][2] is the response set
   #                                seq[ ][3] is the action set
   #     [ The parts of the question are the next level list,
   #                             so seq[ ][0][0] is the first part of the question, for example "What color"
   #                            and seq[ ][0][1] is the next  part of the question, for example "is the sky?" ],
   #     [ The answers are the next list,
   #                             so seq[ ][1][0] is the first  answer, for example "Black"
   #                            and seq[ ][1][1] is the second answer, for example "Blue" ],
   #     [ The response are the next list,
   #                             so seq[ ][2][0] is the first  response, for example "Yes, at night."
   #                            and seq[ ][2][1] is the second response, for example "Yes, during the day." ],
   #     [ The actions are the next list,
   #                             so seq[ ][3][0] is the first  action, for example 0 (meaning take no action)
   #                            and seq[ ][3][1] is the second action, for example 1 (meaning advance one question) ]]]

See `Open Allure wiki`_ for details and examples.

.. _Open Allure wiki: http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

class Sequence(object):

    def classify(self,strings):
        """
Create list of string types::

   Identify strings which contain new line only   (type N)
   #             or which contain ; or ;; markers (type indicated by offset of marker between Answer ; Response)
   #             or else mark as question         (type Q)

        """
        string_types = []
        for i in strings:
            if i.rstrip() == "": string_types.append("N")
            else:
               slash_at = i.find(";")
               if slash_at > 0:  string_types.append(str(slash_at))
               else:             string_types.append("Q")

        return string_types

    def regroup(self,strings,string_types):
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

    def __init__(self, filename="openallure.txt"):
        # read file
        inputs = open(filename).readlines()

        # parse into sequence
        self.sequence = self.regroup(inputs, self.classify(inputs))

