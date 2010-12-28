=====================
`CHANGES.txt`
=====================

Change history::

  v0.1d29, 28 December 2010
    Ctrl+V for paste now also works in Windows
    Clean (no semi-colon) scripts
    Access chat history with up and down arrows
    
  v0.1d28, 28 December 2010
    Start with selected script from command line
    Allow typing of tilde

  v0.1d27, 11 December 2010
    Added Ctrl + R for refresh
    Added show source command (for Mac)

  v0.1d26, 2 November 2010
    Worked in graph.py for display of question sequence as graph calling GraphViz
    Added support for buzhug database to track progress through question sequence

  v0.1d25, 19 October 2010
    Stripped out video and voice leaving only text-to-speech

  v0.1d23, 6 October 2010
    Resize text with Ctrl+(+/-)
    Paste with Ctrl+V in OSX
    Force input with Ctrl+I

  v0.1d22, 4 October 2010
    Fade-in text

  v0.1d20, 1 August 2010
    Read questions directly from Etherpad
    Extend answers with underscores for ease of selection at right side of screen

  v0.1d19, 11 June 2010
    Shadow interface testing

  v0.1d18, 17 May 2010
    Comments marked with # are now ignored in scripts
    Answers ending with ... are silenced (for example, Continue ... )
    Converted responses.py into responses.cfg
    Added in-script rule parsing to qsequence.py with regular expression by example
      so scripts can now specify both FIXED and AD HOC responses. See example in new_rules.txt

  v0.1d17, 13 May 2010
    Replaced web browser selection in configuration with import webbrowser

  v0.1d16, 12 May 2010
    Added tags to script syntax so questions can be inserted in a sequence without renumbering
    Pulled chat.py and responses.py out of openallure.py
    Put in first unittests for chat.py

  v0.1d15, 28 April 2010
    Voice commands next and back added
    Keyboard commands left arrow (back) and right arrow (next) added
    Voice selection by last word and (correct number plus at least one matching word)
    Window title includes Open Allure version number

  v0.1d14, 27 April 2010
    systemHasX configuration options changed to useX (and then only if possible).

  v0.1d13, 19 April 2010
    Override speaker avatar in scripts
    Stop using .txt file for nltkResponse

  v0.1d12, 19 April 2010
    [next] variant of [input] with automatic page turn after delay set in openallure.cfg

  v0.1d11, 17 April 2010
    Allow change of font and font size in openallure.cfg.  Permits Chinese characters.

  v0.1d10, 16 April 2010
    Changed to use os.platform
    Changed to using unicode for sequence text

  v0.1d9, 14 April 2010
    Added systemHasSay to openallure.cfg and voice.py to use Mac say for text to speech
    Allowed keys 1 through 6 when [input] is part of question to retain answer selection function
    Made browser command line call dependent on os.name

  v0.1d8, 29 March 2010
    Added open/start commands

  v0.1d7, 25 March 2010
    New three panel interface and smile/talk/listen photos

  v0.1d6, 15 March 2010
    Cleaned up regular expression matches a bit

  v0.1d5, 10 March 2010
    Added NLTK-based chatbot text input capabilities.

  v0.1d4, 6 March 2010
    Brought back voice recognition code.

  v0.1d3, 4 March 2010
    In sequence.py, Sequence has path attribute to allow navigation
    to follow to new local source

  v0.1d2, 2 March 2010
    Added connection to AIML

  v0.1d1, 26 February 2010
    Added ability to read text from URL
    Added openallure.cfg configuration file
    Removed utils.py

  v0.1d0, 12 February 2010
    Initial release.

