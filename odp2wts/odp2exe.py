# -*- coding: utf-8 -*-
"""
odp2exe.py
a component of Wiki-to-Speech.py

Creates odp2wts.exe for Windows

python odp2wts.py py2exe

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""
from distutils.core import setup
import py2exe

setup(console=['odp2wts.py'],
      options = {"py2exe": { "dll_excludes": ["POWRPROF.dll",
                                              "tk85.dll",
                                              "tcl85.dll"],
                             "bundle_files" : 1,
                           }
                },
      data_files=[(".",['CHANGES.txt',
                       'ethics_notice.txt',
                       'README.txt',
                       'LICENSE.txt'])],
      zipfile=None,
     )
