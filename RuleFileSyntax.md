
```
# Key to the parts of an Open Allure rule:
#
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

# link rules are used in scripts to allow a match with an ad hoc input
# to cause a jump to a particular question tag
[link]

# text rules return some open allure script to continue the dialog
# NOTE: Two text rules are defined in this section: demo and turing.
[text]
[[demo]]
re="(demo|hi|hello)(.*)"
reply="""Welcome. Here are some choices:
Do simple math;;
Explore a dictionary;;;
Learn about Open Allure;[about.txt]
[input];;;;

OK.
Try some two operand math
like ADD 2 + 2:
[input];;

Look up words
by entering WHAT IS <word>:
[input];;
"""

[[turing]]
re="(.*)(turing|loebner)(.*)"
reply="""I was hoping this would come up.
Look at std-turing.aiml;[turing.txt]"""




# open is a type of control rule, allowing opening of new sequences
# The name of the rule TYPE and the name of the RULE are the same: open.
[open]
[[open]]
re="(open|start)\s*([a-zA-Z0-9\-\_\.\/\:]+)"
reply="""Request to open new sequence%2"""




# quit is another type of control rule, allowing exiting on command
# NOTE: The name of the rule TYPE and the name of the first RULE are the same: quit.
#       The quit rule will only fire when the entire input is "quit" or "exit"
#       so it will NOT file when the input merely contains one of these words,
#       as in "How can I quit smoking?"
#       
#       A second rule of this quit type has been added: give up.
#       The give up rule fires when the input is "I give up"
[quit]
[[quit]]
re="(quit|exit)"
reply="""Request to quit"""

[[give up]]
re="i give up"
reply="""Request to quit"""




# math allows digits connected with operators (+, -, * and /) 
#    to be used in simple math expressions
# The processing of these math expressions is much more complicated
# than the processing of other text and control inputs.  It is likely that 
# as Open Allure develops a separate module will be devoted just to parsing 
# and responding to more complex math inputs.
# For now, this section is here as a proof-of-concept.
[math]
[[math add]]
re="[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\+\s*(\-?[0-9.]+)"
reply="""You want to add%1 and%2"""

[[math subtract]]
re="[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\-\s*(\-?[0-9.]+)"
reply="""You want to subtract%1 minus%2"""

[[math multiply]]
re="[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\*\s*(\-?[0-9.]+)"
reply="""You want to multiply%1 by%2"""

[[math divide]]
re="[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\/\s*(\-?[0-9.]+)"
reply="""You want to divide%1 by%2"""



# wordMath allows numeric words from zero up to twenty to be used 
#     in simple math expressions
# The processing of these math expressions is much more complicated
# than the processing of other text and control inputs.  It is likely that 
# as Open Allure develops a separate module will be devoted just to parsing 
# and responding to more complex wordMath inputs.
# For now, this section is here as a proof-of-concept.
[wordMath]
[[wordMath add]]
re="(what is|what\'s|find|calculate|add)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|[0-9.]+)\s+plus\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)"
reply="""You want to add%2 and%3"""

[[wordMath add2]]
re="add\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(and|plus)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)"
reply="""You want to add%1 and%3"""

[[wordMath subtract]]
re="(what is|what\'s|find|calculate|subtract)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+minus\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)"
reply="""You want to subtract%2 minus%3"""

[[wordMath subtract2]]
re="subtract\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+from\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)"
reply="""You want to subtract%2 minus%1"""

[[wordMath multiply]]
re="(what is|what\'s|find|calculate|multiply)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(times|multiplied by)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)"
reply="""You want to multiply%2 by%4"""

[[wordMath divide]]
re="(what is|what\'s|find|calculate|divide)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(over|divided by|by)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)"
reply="""You want to divide%2 by%4"""



# wordLookup using the NLTK dictionary
# NOTE: 
[wordLookup]
[[define]]
re="(what does|what\'s)\s+(.*)\s+mean(.*)"
reply="""You want to define%2"""

[[define2]]
re="(what is an|what is a|what is the|what is|search for|search|what\'s an|what\'s a|what\'s|find|define|defined)\s+(.*)"
reply="""You want to define%2"""
```