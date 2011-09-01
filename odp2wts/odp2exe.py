#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        odp2exe.py
# Purpose:     Compile odp2wts.py into Windows .exe
# Author:      John Graves
#
# Created:     1 September 2011
# Copyright:   (c) John Graves 2011
# License:     MIT License
#
# Usage:       python odp2exe.py
#-------------------------------------------------------------------------------

from setuptools import setup
import operator
import os
import py2exe
import shutil
import sys


class BuildApp:
    def __init__(self):
        self.APP = ['odp2wts.py']
        self.DATA_FILES = ['CHANGES.txt',
                       'ethics_notice.txt',
                       'README.txt',
                       'LICENSE.txt',
                       'lame.exe',
                       'MP4Box.exe',
                       'ffmpeg.exe',
                       'js32.dll',
                       'sapi2wav.exe',
                       'sox.exe',
                       'soxi.exe',
                       'pthreadgc2.dll',
                       'libgomp-1.dll',
                       'zlib1.dll',
                       '_tkinter.pyd',
                       'tcl85.dll',
                       'tk85.dll']
        self.OPTIONS = { "dll_excludes": ["POWRPROF.dll",
                                              "tk85.dll",
                                              "tcl85.dll"],
                             "bundle_files" : 1,
                           }
        #Dist directory
        self.dist_dir ='dist'

    def run(self):
        if os.path.isdir(self.dist_dir): #Erase previous destination dir
            shutil.rmtree(self.dist_dir)

        setup(
            console=self.APP,
            data_files=self.DATA_FILES,
            options={'py2exe': self.OPTIONS},
            setup_requires=['py2exe'],
        )

        if os.path.isdir('build'): #Clean up build dir
            shutil.rmtree('build',True)

if __name__ == '__main__':
    if operator.lt(len(sys.argv), 2):
        sys.argv.append('py2exe')
    BuildApp().run() #Run generation
    raw_input("Press any key to continue") #Pause to let user see that things ends

