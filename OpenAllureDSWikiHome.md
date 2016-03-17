# Introduction #

OpenAllureDS (for Dialog System) Wiki

A bold vision for this project:

Evolution provides a great way to create high levels of sophistication (for example,  [human language](http://wwwiz.com/issue02/wiz_f05.html)). This project aims to evolve a new style of interaction with the computer -- one based more on the context in which we humans live: a world where sound and light are perceived and where that world has [salience](http://en.wikipedia.org/wiki/Salience_(neuroscience)).

Without a microphone and a webcam, most computers are deaf, blind and oblivious to their surroundings.  With additional hardware, we can develop systems with more (and eventually better-than-human) _perception_ -- as shown in the proof-of-concept videos linked below.

Perception alone, however, is not enough. Behind our eyes and ears is an engine that generates **actions** and **reactions**.  Most computer programs are primarily _reactive_ and not _**proactive**_.  A dialog system has the potential to change that, moving toward (and beyond) the primarily proactive (one way) communication of printed words.

Imagine, in short, a system which could explain itself or explain anything we want to have explained (to the extent possible) by controlling sounds and images on the screen while _simultaneously_ attending to how well the message is getting across -- just as we do in a normal conversation. Think of a talking, multimedia version of Wikipedia that keeps track of which topics you are familiar with and how you learn best.

[Andragogy more than pedagogy.](http://www.floridatechnet.org/inservice/abe/abestudent/andravsped.pdf)

[Collaborating via artifacts.](http://www.slideshare.net/eekim/collaborating-via-artifacts)

[We-Think: the more we share, the richer we are.](http://www.charlesleadbeater.net/cms/xstandard/ChapterOne.pdf)

[Here Comes Everybody:](http://www.shirky.com/herecomeseverybody/2008/04/looking-for-the-mouse.html) Let's use our cognitive surplus productively.

## Where to start? ##

Games! For example, [PlayStation](http://www.us.playstation.com/) has had gesture recognition with the [EyeToy](http://en.wikipedia.org/wiki/EyeToy) since 2003. Software tools, some illustrated below, now make it easier for us to build and modify our own voice-and-vision enabled chatterbots.  Python is particularly well suited for this development work due to the (relative) ease with which it can be written and read-with-understanding by other developers.

Please begin at the stage most appropriate for you:

**Not interested in coding, just want to play the games**: see [downloads](http://code.google.com/p/open-allure-ds/downloads/list) as the project develops

**New to Python**: get started at [python.org](http://www.python.org/) and watch how-to videos at [ShowMeDo](http://showmedo.com/)

**Python programmer, but new to voice and vision**: download [dragonfly](http://code.google.com/p/dragonfly/) and [pycam](http://code.google.com/p/pycam/) and [source code for this project](http://code.google.com/p/open-allure-ds/source/checkout). Tim Harper has done [an in-depth video tutorial on dragonfly](http://vimeo.com/9156942).

**Ready to contribute to the Open Allure DS project**: get set with [Mercurial](http://mercurial.selenic.com/guide/), the project's distributed source code management system

[Work to be Done](http://spreadsheets.google.com/ccc?key=0AqJtCBHzLJcXdEdaM0tBSDl0T0NhNUxONXRqblpMdnc&hl=en)
[Issues with Open Allure ](http://code.google.com/p/open-allure-ds/issues/list)

Enjoy!

# Details #

Discussion of this project can be found on [Ning](http://openallureds.ning.com/).

Progress on this project is being documented with [a series of short proof-of-concept videos on YouTube](http://bit.ly/JohnGravesYouTube).

**Open Allure DS**<br>
One Minute Introduction to Open Allure DS: Voice and Vision Dialog System in Python.<br>
<br>
<b>Python No Hands with dragonfly</b><br>
Demonstrates programming in Python using speech recognition alone (no keyboard or mouse) with voice macros coded using dragonfly (<a href='http://code.google.com/p/dragonfly/'>http://code.google.com/p/dragonfly/</a>). Presented at Kiwi PyCon 2009 (<a href='http://nz.pycon.org'>http://nz.pycon.org</a>) on 8 November 2009.<br>
<br>
<b>Python Listens and Repeats</b><br>
Demonstrates a voice mirror in Python using speech recognition (no keyboard or mouse) and text-to-speech using dragonfly (<a href='http://code.google.com/p/dragonfly/'>http://code.google.com/p/dragonfly/</a>).<br>
<br>
<b>Face Tracking with OpenCV in Python</b><br>
After downloading OpenCV from Sourceforge (<a href='http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.0/'>http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.0/</a>) and copying the Python2.6 folder contents to Python26\Lib\site-packages to bind the library, this video was made with the sample program by typing<br>
<pre><code>python c:\OpenCV2.0\samples\python\camshift.py<br>
</code></pre>

<b>Voice and Gesture Demo</b><br>
Shows interaction with both voice and gesture control in context of webcam video<br>
<br>
<h2>Video from Other Projects</h2>

<b>XBOX Project Natal - voice and gesture recognition</b>
(<a href='http://bit.ly/JGnatal'>http://bit.ly/JGnatal</a>)<br>
<br>
<b>MIT Media Lab demo of display being used as lenless camera to track gestures</b>
(<a href='http://link.brightcove.com/services/player/bcpid36804639001?bctid=55998893001'>http://link.brightcove.com/services/player/bcpid36804639001?bctid=55998893001</a>)<br>
<br>
<h1>Code Documentation Tool</h1>

<a href='http://sphinx.pocoo.org/'>Sphinx</a>