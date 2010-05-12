=====================
`openallure.cfg`
=====================

Modify this configuration file to suit your needs::

    [Source]
    #
    # Set the source for the starting question sequence
    #
    # This can be the local file name for a plain text file
    # with the syntax specified at
    # http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax
    #
    # OR an internet address (URL) for a web page that contains
    # the question sequence tagged as preformatted text
    # (i.e. text between the tags <pre> and </pre>)
    #
    url = sky.txt
    #url = jg.txt
    #url = cielo.txt
    #url = about.txt
    #url = input_only.txt
    #url = http://openallureds.ning.com/profiles/blogs/introduction-to-open-allure
    #url = http://bit.ly/csdZio
    
    [Options]
    #
    # delayTime determines the default delay for an automatic page turn (in milliseconds)
    #
    # allowNext allows voice command Next or right arrow on keyboard to skip to
    #   next question without giving answer or hearing response
    #
    delayTime = 6000
    allowNext = 1
    
    [Browser]
    #
    # windowsBrowser is the browser that will be used in Windows
    # darwinBrowser is the browser that will be used in Mac
    #
    windowsBrowser = d:\\firefox\\firefox
    darwinBrowser = open
    
    [Colors]
    #
    # Copy the desired (Red, Green, Blue) color codes into the things to color below
    #
    # black = 0,0,0
    # gray  = 200,200,200
    # white = 255,255,255
    # red   = 255,0,0
    # green = 0,255,0
    # blue  = 0,0,255
    # yellow= 255,255,0
    # purple= 255,0,255
    #
    background      = 255,255,255
    unreadText      = 0,255,0
    readText        = 200,200,200
    selectedText    = 255,0,0
    highlightedText = 255,255,0
    
    [Font]
    #
    # Default uses system font
    # heititc supports Chinese characters
    #
    font = heititc
    size = 40
    
    [Photos]
    #
    # Smile is the awaiting-input image
    # Listen is the image when user input has begun
    # Talk is the image when text-to-speech is in progress
    #
    # TODO: Support for multiple speakers (for example, the characters in a play)
    #
    smile  = jg-smile-small.jpg
    listen = jg-listening-small.jpg
    talk   = jg-gesturing-small.jpg
    
    [Voice]
    #
    # Indicate which text-to-speech engine will generate spoken output
    # If none is selected, the default is to just print output to the console
    #
    # Dragonfly may be available on Mac and PC systems
    # eSpeak may be available on Unix systems
    # Say may be available on Mac systems
    #
    # (optional) language is added to the command line string for eSpeak and say
    # to permit different voices/accents
    #
    useDragonfly = 0
    useEspeak = 0
    useSay = 0
    #language = -v french
    #language = -v english
    language =
