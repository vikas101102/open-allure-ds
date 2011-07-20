# -*- coding: utf-8 -*-
"""
odp2wts.py
a component of Wiki-to-Speech.py

Extract speaker notes from .odp file and prepare script.txt for Wiki-to-Speech

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""
__version__ = 1.1

import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from zipfile import ZipFile
import easygui
import os
import shutil
import stat
import subprocess
import sys

## Step 0 - obtain file names

odpFilePath = easygui.fileopenbox(title="ODP2WTS Converter", msg="Select an .odp file", 
                              default='~/*.odp', filetypes=None)
if odpFilePath == None:
    sys.exit()
    
(odpFileDirectory, odpFile) = os.path.split(odpFilePath)

## Step 1 - parse the .odp file, prepare script.txt and .zip file
# TODO Does not handle quotes or apostrophes well
def joinContents(textPList):
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
                    justText = justText + " "
                else:
                    # deal with single quote and double quotes
                    justText = justText + \
        str(item.replace(u'\u2019', u'\u0027').replace(u'\u201c', u'\u0022').replace(u'\u201d', u'\u0022'))
            textItems.append(justText)
        joinedItems = "\n".join(textItems)
    return joinedItems

if 0 != len(odpFile) and os.path.exists(odpFilePath):
    odpName = odpFile.replace(".odp","")
    odp = ZipFile(odpFilePath,'r')
    f = odp.read(u'content.xml')
    soup = BeautifulStoneSoup(f)
    notes = soup.findAll(attrs={"presentation:class":"notes"})
    noteTextPLists = [item.findAll("text:p") for item in notes]
    noteText = [joinContents(noteTextPList) for noteTextPList in noteTextPLists]
    
    stem="img"

    suffix="png"
        
    relativePath=""

else:
    sys.exit()
    
# OpenOffice starts numbers at 0    
onImg = 0

firstOnImg = onImg

# Create script.txt file
scriptFile = open(odpFileDirectory+os.sep+'script.txt','w')
for item in noteText:
    # Add a line with a (relative) link to each slide
    scriptFile.write(relativePath + stem+str(onImg)+"."+suffix+"\n")
    # followed by the voice over text for the slide
    scriptFile.write(item)
    scriptFile.write("\n\n")
    onImg += 1
scriptFile.close()

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
        
ensure_dir(odpFileDirectory+os.sep+odpName)

dir = os.listdir(odpFileDirectory+os.sep+odpName)
png = [file for file in dir if file.lower().endswith(".png")]
if len(png)==0:
    # look for .png files in local directory and copy them to target directory
    dir = os.listdir(odpFileDirectory)
    png = [file for file in dir if file.lower().endswith(".png")]
    if len(png)==0:
        easygui.msgbox("Need some .png files for this presentation.")
        sys.exit()
    else:
        for file in png:
            shutil.copy(odpFileDirectory+os.sep+file, odpFileDirectory+os.sep+odpName)

# Collect script and image files into ZIP file
outputFile = ZipFile(odpFileDirectory+os.sep+odpName+".zip",'w')
outputFile.write(odpFileDirectory+os.sep+"script.txt")

dir = os.listdir(odpFileDirectory)
imageFiles = [file for file in dir if file.endswith(suffix)]
for file in imageFiles:
    outputFile.write(odpFileDirectory+os.sep+odpName+os.sep+file)
easygui.msgbox("Zipped script.txt and image files to "+odpFileDirectory+os.sep+odpName+".zip")

## Step 2 - Make and run convert.bat

# Make convert.bat to say questionText
f = open(odpFileDirectory+os.sep+"convert.bat","w")
os.chmod(odpFileDirectory+os.sep+"convert.bat",stat.S_IRWXU)
onImg = firstOnImg
for item in noteText:
    f.write("/usr/bin/say -o img"+str(onImg)+'.aiff "')
    f.write(item)
    f.write('"\n')
    f.write("~/bin/sox img"+str(onImg)+".aiff "+odpFileDirectory+os.sep+odpName+os.sep+"img"+str(onImg)+".ogg\n")
    f.write("~/bin/sox img"+str(onImg)+".aiff "+odpFileDirectory+os.sep+odpName+os.sep+"img"+str(onImg)+".mp3\n")
    onImg += 1
f.close()

## Step 3 - create HTML wrapper


maxNum = 0
for file in png:
    stem = file.split(".")[0]
    number = stem[3:]
    num = int(number)
    if num>maxNum:
        maxNum=num
maxImgHtml = 'img' + str(maxNum) + '.htm'

def writeHtmlHeader():
    htmlFile.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"' + "\n")
    htmlFile.write('"http://www.w3.org/TR/html4/transitional.dtd">' + "\n")
    htmlFile.write("<html>\n<head>\n")
    htmlFile.write('<meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">' + "\n")
    htmlFile.write('<title>Wiki-to-Speech</title>\n</head>\n')
    htmlFile.write('<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">' + "\n")
    htmlFile.write('<center>' + "\n")
    
for file in png:
    stem = file.split(".")[0]
    if stem.startswith("Slide"):
        number = stem[5:]
    else:
        number = stem[3:]
    num = int(number)

    if num==0:
        htmlFile = open(odpFileDirectory+os.sep+odpName+ ".htm","w")
    else:
        htmlFile = open(odpFileDirectory+os.sep+odpName +"/" + stem+".htm","w")
        
    writeHtmlHeader()
        
    # First page and Back Navigation    
    if num==0:    
        htmlFile.write("""First page Back """)
    elif num==1:    
        htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> <a href="../""" + odpName + """.htm">Back</a> """)
    else:
        htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> <a href="img""" + str(num-1) + """.htm">Back</a> """)
    
    # Continue and Last Page navigation
    if num==maxNum: 
        htmlFile.write(""" Continue Last page<br>""" + "\n")
    elif num==0:
        htmlFile.write("""<a href=""" + '"' + odpName +"""/img1.htm">Continue</a> """)
        htmlFile.write("""<a href=""" + '"' + odpName +"/" + maxImgHtml + '"' + """>Last page</a><br>""" + "\n")
    else:
        htmlFile.write("""<a href="img""" + str(num+1) + """.htm">Continue</a> <a href=""" + '"' + maxImgHtml + '"' + \
        """>Last page</a><br>""" + "\n")

    # image src and link to next slide
    if (num==maxNum and num>0):
        # src but no link
        htmlFile.write("""<img src=""" + '"' + file + '" style="border:0px"><br>' + "\n")
    elif (num==maxNum and num==0): 
        # src but no link
        htmlFile.write("""<img src=""" + '"' + odpName +'/' + file + '" style="border:0px"><br>' + "\n")
    elif num==0:      
        htmlFile.write("""<a href=""" + '"' + odpName +"/img" + str(num+1) + """.htm"><img src=""" + '"' + odpName +'/' + file + '" style="border:0px"></a><br>' + "\n")
    else:
        htmlFile.write("""<a href="img""" + str(num+1) + """.htm"><img src=""" + '"' + file + '" style="border:0px"></a><br>' + "\n")
 
    # include audio
    if num==0:
        htmlFile.write("""<p id="playaudio"><audio controls="controls" autoplay="autoplay"><source src=""" + '"' + odpName +'/' + stem + """.ogg" /><source src=""" + '"' + odpName +'/' + stem + """.mp3" />\nYour browser does not support the <code>audio</code> element.\n</audio></p>\n""")
        htmlFile.write("""<!--[if IE 7]>\n<script>\ndocument.getElementById("playaudio").innerHTML='<embed src=""" + '"' + odpName +'/' + stem + """.mp3" autostart="true">';\n</script>\n<![endif]-->\n""")
    else:    
        htmlFile.write("""<p id="playaudio"><audio controls="controls" autoplay="autoplay"><source src=""" + '"' + stem + """.ogg" /><source src=""" + '"' + stem + """.mp3" />\nYour browser does not support the <code>audio</code> element.\n</audio></p>\n""")
        htmlFile.write("""<!--[if IE 7]>\n<script>\ndocument.getElementById("playaudio").innerHTML='<embed src=""" + '"' + stem + """.mp3" autostart="true">';\n</script>\n<![endif]-->\n""")
        
    htmlFile.write('</center>' + "\n")
    htmlFile.write('</body>\n</html>\n')
    htmlFile.close()
    
p = subprocess.Popen(odpFileDirectory+os.sep+"convert.bat",shell=True).wait()
p = subprocess.Popen("open "+odpFileDirectory+os.sep+odpName+".htm", shell=True).pid        