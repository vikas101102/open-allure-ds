# -*- coding: utf-8 -*-
"""
odp2wts.py
a component of Wiki-to-Speech.py

Extract speaker notes from .odp file and prepare script.txt for Wiki-to-Speech

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""
__version__ = "0.1.8"

import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from ConfigParser import ConfigParser
import easygui
import os
import shutil
import stat
import subprocess
import sys
import webbrowser
from zipfile import ZipFile

## Obtain odpFile name and directory

# Check for last .odp file in config file
lastOdpFile = '~/*.odp'
config = ConfigParser()
try:
    config.read('odp2wts.ini')
    lastOdpFile = config.get("Files","lastOdpFile")
except:
    config.add_section("Files")
    config.set("Files","lastOdpFile","")
    with open('odp2wts.ini', 'wb') as configfile:
        config.write(configfile)

odpFile = ""
while odpFile[-4:]!=".odp":
    odpFilePath = easygui.fileopenbox(title="ODP2WTS Converter", msg="Select an .odp file",
                                  default=lastOdpFile, filetypes=None)
    if odpFilePath == None:
        sys.exit()
    
    (odpFileDirectory, odpFile) = os.path.split(odpFilePath)
    (odpName, odpSuffix) = odpFile.split(".")

    if odpFile[-4:]!=".odp":
        easygui.msgbox("Select an .odp file to convert.\nYou selected "+odpFile)

## Find list of .png files

# Create a subdirectory for generated files (if needed)
def ensure_dir(d):
    """Make a directory if it does not exist"""
    if not os.path.exists(d):
        os.makedirs(d)
odpFileSubdirectory = odpFileDirectory+os.sep+odpName
ensure_dir(odpFileSubdirectory)

# Look for .png files (slide images) in the odpName subdirectory
dir = os.listdir(odpFileSubdirectory)
png = [file for file in dir if file.lower().endswith(".png")]

# If no .png files found there ...
if len(png)==0:
    # ... look for .png files in odpFileDirectory and copy to odpName subdirectory
    dir = os.listdir(odpFileDirectory)
    png = [file for file in dir if file.lower().endswith(".png")]
    # If still no .png files, request some.
    if len(png)==0:
        easygui.msgbox("Need some .png files for this presentation.")
        sys.exit()
    else:
        for file in png:
            shutil.copy(odpFileDirectory+os.sep+file, odpFileSubdirectory)

# Find minimum value for slide number for linking to First Slide
# Find maximum value for slide number for linking to Last Slide
# Find imageFilePrefix, imageFileSuffix
# Default values
minNum = 0
maxNum = 0
imageFilePrefix = "img"
imageFileSuffix="png"
# Test contents of png list
for file in png:
    # Parse out file name stem (which includes number) and imageFileSuffix
    (stem, imageFileSuffix) = file.split(".")

    # Parse out just number (num) and imageFilePrefix
    if stem.startswith("Slide"):
        # PowerPoint Slide images are output to PNG with starting index of 1
        imageFilePrefix = "Slide"
        minNum=1
        num = int(stem[5:])
    else:
        # ODP slide images are output to PNG with starting index of 0
        imageFilePrefix = "img"
        num = int(stem[3:])
    if num>maxNum:
        maxNum=num

## Step 1 - parse the .odp file, prepare script.txt and .zip file

def joinContents(textPList):
    """Combine tagged XML into single string"""
    # item is list of all the XML for a single slide
    joinedItems = ""
    if len(textPList)>0:
        textItems = []
        i = 0
        for textP in textPList:
            # break the XML into a list of tagged pieces (text:span)
            textAndTags = sum([item.contents for item in textP("text:span")],[])
            if len(textAndTags)==0:
                textAndTags = textP.contents
            justText = u""
            for item in textAndTags:
                if type(item)==BeautifulSoup.Tag:
                    justText = justText + item.text + " "
                else:
                    # deal with single quote and double quotes and dashes
                    justText = justText + \
                               str(item.replace(u'\u2019',
                                                u'\u0027').replace(u'\u201c',
                                                u'\u0022').replace(u'\u201d',
                                                u'\u0022').replace(u'\u2013',
                                                u'\u002D')) + " "
            textItems.append(justText)
        joinedItems = "\n".join(textItems)
    return joinedItems

if ((0 != len(odpFile)) and (os.path.exists(odpFilePath))):
    # Save file name to config file
    config.set("Files","lastOdpFile",odpFilePath)
    with open('odp2wts.ini', 'wb') as configfile:
        config.write(configfile)

    odpName = odpFile.replace(".odp","")
    odp = ZipFile(odpFilePath,'r')
    f = odp.read(u'content.xml')
    soup = BeautifulStoneSoup(f)
    notes = soup.findAll(attrs={"presentation:class":"notes"})
    noteTextPLists = [item.findAll("text:p") for item in notes]
    noteText = [joinContents(noteTextPList) for noteTextPList in noteTextPLists]
else:
    sys.exit()

# Create script.txt file
scriptFile = open(odpFileSubdirectory+os.sep+'script.txt','w')
onImg = minNum
for item in noteText:
    if onImg-minNum == 0: # first slide
        # insert line with link to first slide image after parameter lines
        # For example, noteText could start with [path=...]
        lines = item.split("\n")
        slideOnLine = -1
        for linenum, line in enumerate(lines):
            if len(line.strip())>0:
                if line.startswith("["):
                    scriptFile.write(line+"\n")
                elif slideOnLine == -1:
                    scriptFile.write(imageFilePrefix+str(onImg)+"."+imageFileSuffix+"\n")
                    slideOnLine = linenum
                    scriptFile.write(line+"\n")
                else:
                    scriptFile.write(line+"\n")
            else:
                scriptFile.write("\n")
    else:
        # Add a line with a link to each slide
        scriptFile.write(imageFilePrefix+str(onImg)+"."+imageFileSuffix+"\n")
        # followed by the voice over text for the slide
        scriptFile.write(item+"\n")
    scriptFile.write("\n")
    onImg += 1
scriptFile.close()

# Collect script and image files into ZIP file
outputFile = ZipFile(odpFileDirectory+os.sep+odpName+".zip",'w')
savePath = os.getcwd()
os.chdir(odpFileSubdirectory)
outputFile.write("script.txt")
for file in png:
    outputFile.write(file)
os.chdir(savePath)
easygui.msgbox("Zipped script.txt and image files to "+odpFileDirectory+os.sep+odpName+".zip")

## Step 2 - Make and run convert.bat

# Make convert.bat to convert questionText into audio files
f = open(odpFileDirectory+os.sep+"convert.bat","w")
os.chmod(odpFileDirectory+os.sep+"convert.bat",stat.S_IRWXU)
onImg = minNum
for item in noteText:

    if sys.platform == "win32":
        # For Windows
        f.write('sapi2wav.exe '+imageFilePrefix+str(onImg)+'.wav 1 -t "')
        lines = item.split("\n")
        for linenum, line in enumerate(lines):
            if not line.startswith("["):
                line.replace('"',' ').replace('`',' ').replace(';',' ')
                f.write(line+" ")
            elif linenum>0:
                break
        f.write('"\n')
        f.write('lame.exe -h '+imageFilePrefix+str(onImg)+'.wav '+ '"' + \
                             odpFileSubdirectory+os.sep+imageFilePrefix+str(onImg)+'.mp3"\n')
        f.write('sox.exe '+imageFilePrefix+str(onImg)+'.wav '+ '"' + \
                         odpFileSubdirectory+os.sep+imageFilePrefix+str(onImg)+'.ogg"\n')
        f.write('del '+imageFilePrefix+str(onImg)+'.wav\n')
    else:
        # For Mac OSX
        f.write("/usr/bin/say -o "+imageFilePrefix+str(onImg)+'.aiff "')
        lines = item.split("\n")
        for linenum, line in enumerate(lines):
            line.replace('"',' ').replace('`',' ').replace(';',' ')
            if not line.startswith("["):
                f.write(line+" ")
            elif linenum>0:
                break
    #    f.write(item)
        f.write('"\n')
        f.write('~/bin/sox '+imageFilePrefix+str(onImg)+'.aiff "'+
          odpFileSubdirectory+os.sep+imageFilePrefix+str(onImg)+'.ogg"\n')
        f.write('~/bin/sox '+imageFilePrefix+str(onImg)+'.aiff "'+
          odpFileSubdirectory+os.sep+imageFilePrefix+str(onImg)+'.mp3"\n')
    onImg += 1
f.close()

## Step 3 - create HTML wrapper
maxImgHtml = imageFilePrefix + str(maxNum) + '.htm'

def writeHtmlHeader():
    htmlFile.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"' + "\n")
    htmlFile.write('"http://www.w3.org/TR/html4/transitional.dtd">' + "\n")
    htmlFile.write("<html>\n<head>\n")
    htmlFile.write('<meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">' + "\n")
    htmlFile.write('<title>Wiki-to-Speech</title>\n</head>\n')
    htmlFile.write('<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">' + "\n")
    htmlFile.write('<center>' + "\n")

for file in png:

    # Parse out file name stem (which includes number)
    stem = file.split(".")[0]

    # Parse out just number (num)
    if stem.startswith("Slide"):
        number = stem[5:]
    else:
        number = stem[3:]
    num = int(number)

    if num-minNum==0:
        # Create first .htm file in same directory as odpFile
        htmlFile = open(odpFileDirectory+os.sep+odpName+".htm","w")
    else:
        # Create subsequent .htm files in folder in same directory as odpFile
        htmlFile = open(odpFileSubdirectory+os.sep+stem+".htm","w")

    writeHtmlHeader()

    # First page and Back navigation
    # First page
    if num-minNum==0:
        htmlFile.write("""First page Back """)
    # Second page
    elif num-minNum==1:
        htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> <a href="../""" +
                                            odpName +""".htm">Back</a> """)
    # Rest of pages
    else:
        htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> <a href=""" + '"' +
                        imageFilePrefix + str(num-1)+""".htm">Back</a> """)

    # Continue and Last Page navigation
    # Last page
    if num==maxNum:
        htmlFile.write('Continue Last page<br>\n')
    # First page
    elif num-minNum==0 and num+1==maxNum:
        htmlFile.write( \
            '<a href="'+
            odpName+"/"+imageFilePrefix+str(num+1)+
            '.htm">Continue</a> ')
        htmlFile.write( \
            '<a href="'+
            odpName+"/"+maxImgHtml+
            '">Last page</a><br>\n')
    # Rest of pages
    else:
        htmlFile.write( \
            '<a href="'+
            imageFilePrefix + str(num+1) +
            '.htm">Continue</a> ')
        htmlFile.write( \
            '<a href="' +
            maxImgHtml +
            '">Last page</a><br>\n')

    # image src and link to next slide
    # Last page which is not (also) the first page
    if (num==maxNum and num-minNum>0):
        # src but no link
        htmlFile.write( \
            '<img src="' +
            file +
            '" style="border:0px"><br>\n')
    # Last page which is also the first page
    elif (num==maxNum and num-minNum==0):
        # src but no link
        htmlFile.write( \
            '<img src="' +
            odpName+"/"+file +
            '" style="border:0px"><br>\n')
    # First page
    elif num-minNum==0:
        htmlFile.write( \
            '<a href="' +
            odpName+"/"+imageFilePrefix+str(num+1) +
            '.htm">')
        htmlFile.write( \
            '<img src="' +
            odpName +"/" + file +
            '" style="border:0px"></a><br>\n')
    # Rest of pages
    else:
        htmlFile.write( \
            '<a href="' +
            imageFilePrefix+str(num+1) +
            '.htm">')
        htmlFile.write( \
            '<img src="' +
            file +
            '" style="border:0px"></a><br>\n')

    # include audio
    # First page
    if num-minNum==0:
        pathToAudio = odpName+'/'+stem
    else:
        pathToAudio = stem
    # For Safari
    htmlFile.write( \
        '<p id="playaudio">' +
        '<audio controls autoplay><source src="' +
        pathToAudio +
        '.mp3" />')
    # For Firefox
    htmlFile.write( \
        '<source src="' +
        pathToAudio +
        '.ogg" />\n')
    # For others
    htmlFile.write( \
        'Your browser does not support the <code>audio</code> element.\n</audio>\n')
    htmlFile.write( \
        '</p>\n')
    # For Internet Explorer
    htmlFile.write( \
        '<!--[if lte IE 8]>\n' +
        '<script>\n' +
        'document.getElementById("playaudio").innerHTML=' + "'" +
        '<embed src="' +
        pathToAudio +
        '.mp3" autostart="true">' + "'" + ';\n' +
        '</script>\n' +
        '<![endif]-->\n')

    htmlFile.write('</center>' + "\n")
    htmlFile.write('</body>\n</html>\n')
    htmlFile.close()

os.chdir(odpFileDirectory)
p = subprocess.Popen(odpFileDirectory+os.sep+"convert.bat",shell=True).wait()
os.chdir(savePath)
#p = subprocess.Popen("open "+odpFileDirectory+os.sep+odpName+".htm", shell=True).pid
webbrowser.open_new_tab(odpFileDirectory+os.sep+odpName+".htm")