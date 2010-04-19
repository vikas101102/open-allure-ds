.. OpenAllure documentation master file, created by
   sphinx-quickstart on Fri Feb 12 15:19:58 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Open Allure's documentation!
=======================================

Open Allure is a voice-and-vision enabled dialog system written in Python_.  

Edit the openallure.cfg file to configure the location of the question/answer/response sequence.

.. _Python: http://www.python.org/

Open Allure is part of the output of the `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

`A collection of short videos`_ about the Open Allure project are available and there is `a Google group you can join`_ for updates and discussion.

.. _A collection of short videos: http://bit.ly/openallure

.. _a Google group you can join: http://bit.ly/openalluregg

Dependencies
============

Open Allure uses pyGame_ and BeautifulSoup_ and NLTK_ (Natural Language Toolkit).

Voice recognition depends on the operating system or other software. For Windows, dragonfly_ 
connects to the Windows Speech API. For Mac, dragonfly_ connects to `MacSpeech Dictate`_. For linux, 
we're still looking to connect a voice recognition backend -- please pitch in!

.. _pyGame: http://www.pygame.org/

.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/

.. _NLTK: _http://www.nltk.org/download

.. _dragonfly: http://code.google.com/p/dragonfly/

.. _MacSpeech Dictate: http://www.macspeech.com



Modules
=======

.. toctree::
   :maxdepth: 2

   modules/openallure
   modules/qsequence
   modules/video
   modules/gesture
   modules/text
   modules/voice

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

