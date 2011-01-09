"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['openallure.py']
DATA_FILES = ['CHANGES.txt','ethics_notice.txt','README.txt','LICENSE.txt',
        'openallure.cfg',
        'music.txt','start.txt','silent_start.txt','fixSyntax.txt','help.rtf',
        ('locale/en/LC_MESSAGES',['locale/en/LC_MESSAGES/openallure.mo']),
        'welcome.txt',
        'responses.cfg',
        ('locale/it/LC_MESSAGES',['locale/it/LC_MESSAGES/openallure.mo']),
        'benvenuti.txt',
        'responses_it.cfg',
        ('locale/pt/LC_MESSAGES',['locale/pt/LC_MESSAGES/openallure.mo']),
        'bem-vindo.txt',
        'responses_pt.cfg']
OPTIONS = {'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
