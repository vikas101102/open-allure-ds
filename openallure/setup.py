"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['openallure.py']
DATA_FILES = ['openallure.cfg','responses.cfg','responses_pt.cfg','welcome.txt','bem-vindo.txt',
'CHANGES.txt','ethics_notice.txt','LICENSE.txt','music.txt','README.txt','start.txt',('pt/LC_MESSAGES',['pt/LC_MESSAGES/openallure.mo'])]
OPTIONS = {'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
