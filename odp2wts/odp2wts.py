# -*- coding: utf-8 -*-
"""
odp2wts.py
a component of Wiki-to-Speech.py

Extract speaker notes from .odp file and prepare script.txt for Wiki-to-Speech

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""
from easygui import *
from ConfigParser import ConfigParser
import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from zipfile import ZipFile
import sys
import os
import shutil
import subprocess

# Utility functions
def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def getOdpName(odpFileWithPath):
    (path, odpFile) = os.path.split(odpFileWithPath)
    odpName = odpFile.replace(".odp","")
    return (path, odpName)

def joinContents(textPList):
    # item is list of all the XML for a single slide
    if len(textPList)>0:
        textItems = []
        i = 0
        for textP in textPList:
            # break the XML into a list of tagged pieces (text:span)
            textAndTags = sum([item.contents for item in textP("text:span")],[])
            justText = u""
            for item in textAndTags:
                if type(item)==BeautifulSoup.Tag:
                    justText = justText + " "
                else:
                    # deal with single quote and double quotes and dashes
                    justText = justText + \
                               str(item.replace(u'\u2019',
                                                u'\u0027').replace(u'\u201c',
                                                u'\u0022').replace(u'\u201d',
                                                u'\u0022').replace(u'\u2013',
                                                u'\u002D'))
            textItems.append(justText)
        joinedItems = "\n".join(textItems)
    return joinedItems

# User interface
def main():

    # Check for Dropbox folder in config file and obtain if not found
    config = ConfigParser()
    try:
        config.read('odp2wts.ini')
        DROPBOX_FOLDER = config.get("Directory","DROPBOX_FOLDER")
    except:
        DROPBOX_FOLDER = diropenbox(msg=None
        , title="Browse to Public Dropbox folder, then select OK"
        , default=None
        )
        config.add_section("Directory")
        config.set("Directory","DROPBOX_FOLDER",DROPBOX_FOLDER)
        with open('odp2wts.ini', 'wb') as configfile:
            config.write(configfile)

    # Select an .odp file
    odpFileWithPath = fileopenbox(msg=None
        , title="Select an OpenOffice Presentation File"
        , default="*.odp"
        , filetypes=[".odp","ODP Files"]
        )

    # Convert file
    if odpFileWithPath:
        file = os.path.split(odpFileWithPath)
        msg = "Convert " + file[1] + "\n(Conversion will run in the background.)"
        title = "ODP to Wiki-to-Speech"
        # show a Continue/Cancel dialog
        if ccbox(msg, title):
            odp2script(odpFileWithPath, DROPBOX_FOLDER)
            convert(odpFileWithPath, DROPBOX_FOLDER)
            makehtml(odpFileWithPath, DROPBOX_FOLDER)
            msg = "Conversion complete"
            msgbox(msg, title)
        else:  # user chose Cancel
            sys.exit(0)

def odp2script(odpFileWithPath, DROPBOX_FOLDER):

    # Extract speaker notes from .odp zip file
    odp = ZipFile(odpFileWithPath,'r')
    f = odp.read(u'content.xml')
    soup = BeautifulStoneSoup(f)
    notes = soup.findAll(attrs={"presentation:class":"notes"})
    noteTextPLists = [item.findAll("text:p") for item in notes]
    noteText = [joinContents(noteTextPList) for noteTextPList in noteTextPLists]

    if sys.platform == "win32":
        stem="Slide"
        onImg = 1
    else:
        stem="img"
        onImg = 0

    # Parse out name of odpFile without extension
    (path, odpName) = getOdpName(odpFileWithPath)

    # Create script and batch files
    scriptFile = open('script.txt','w')

    batchFile = open('convert.bat','w')
    batchFile.write("echo off\n")
    batchFile.write("echo Converting text to MP3 Files ...\n")

    # Add speaker notes
    for item in noteText:
        scriptFile.write(odpName+"/"+stem+str(onImg)+".PNG\n")
        scriptFile.write(item)
        scriptFile.write("\n\n")

        batchFile.write('sapi2wav.exe '+stem+str(onImg)+'.wav 1 -t "' + item + '"\n')
        batchFile.write('lame.exe -h '+stem+str(onImg)+'.wav '+ \
                         DROPBOX_FOLDER+os.sep+odpName+os.sep+stem+str(onImg)+'.mp3\n')
        batchFile.write('del '+stem+str(onImg)+'.wav\n')

        onImg += 1

    # Close files
    scriptFile.close()
    batchFile.close()

    print "Created script.txt"
    print "Created convert.bat"


def convert(odpFileWithPath, DROPBOX_FOLDER):

    # Move PNG file folder to DROPBOX_FOLDER
    (path, odpName) = getOdpName(odpFileWithPath)
    pathToPNG = path + '\\' + odpName
    ensure_dir(DROPBOX_FOLDER)
    try:
        if os.path.exists(pathToPNG):
            shutil.move(pathToPNG, DROPBOX_FOLDER)
##        print "Shifted "+odpName+" directory with PNG files to "+DROPBOX_FOLDER
    except:
        msgbox("Unable to move folder \n"+pathToPNG+"\nto\n"+DROPBOX_FOLDER+\
               "\n\nDelete the " + odpName +" folder there and try again.\n\n" + \
               "NOTE: You may also need to press F5\nto refresh your browser window.", "Error")
        sys.exit()
##    except:
##        dir = os.listdir(".")
##        png = [file for file in dir if file.lower().endswith(".png")]
##        for file in png:
##            ensure_dir("static")
##            ensure_dir("static/"+odpName)
##            shutil.copy(file,"static/"+odpName)
##        print "Copied "+stem+" PNG files to static/"+odpName+" directory"

    retcode = subprocess.call(['convert.bat',''])
##    if retcode==0:
##        print "Converted text to MP3 files in Dropbox "+odpName+" directory"
##    else:
##        print "Error in converting text to MP3 files in Dropbox "+odpName+" directory"
##        sys.exit()

def makehtml(odpFileWithPath, DROPBOX_FOLDER):

    (path, odpName) = getOdpName(odpFileWithPath)

    # Write HTML wrappers
    dir = os.listdir(DROPBOX_FOLDER+"\\"+odpName)
    png = [file for file in dir if file.lower().endswith(".png")]
    if len(png)==0:
        print "Place .png and .mp3 files in Dropbox "+odpName+" directory"
        sys.exit()

    maxNum = 0
    for file in png:
        stem = file.split(".")[0]
        if stem.startswith("Slide"):
            number = stem[5:]
        else:
            number = stem[3:]
        num = int(number)
        if num>maxNum:
            maxNum=num

    def writeHtmlHeader():
        htmlFile.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"' + "\n")
        htmlFile.write('"http://www.w3.org/TR/html4/transitional.dtd">' + "\n")
        htmlFile.write("<html>\n<head>\n")
        htmlFile.write('<meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">' + "\n")
        htmlFile.write('<title>Wiki-to-Speech</title>\n</head>\n')
        htmlFile.write('<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">' + "\n")
        htmlFile.write('<center>' + "\n")

    offset = 0
    for file in png:
        print "Preparing HTML wrapper for "+file
        stem = file.split(".")[0]
        if stem.startswith("Slide"):
            offset=1
            number = stem[5:]
            root = "Slide"
        else:
            number = stem[3:]
            root = "img"
        num = int(number)

        maxImgHtml = root + str(maxNum) + '.htm'

        # First slide is one directory above all other files
        if num-offset==0:
            htmlFile = open(DROPBOX_FOLDER+"\\" + odpName+ ".htm","w")
            writeHtmlHeader()
            if num==maxNum:
                # htmlFile.write("""First page Back """)
                # htmlFile.write("Continue Last page<br>\n")
                htmlFile.write("""<img src=""" + '"' + odpName +'/' + file + '" style="border:0px"><br>' + "\n")
            else:
                htmlFile.write("""First page Back """)
                htmlFile.write("""<a href=""" + '"' + odpName +"/"+ root + str(num+1)+""".htm">Continue</a> """)
                htmlFile.write("""<a href=""" + '"' + odpName +"/" + maxImgHtml + '"' + """>Last page</a><br>""" + "\n")
                htmlFile.write("""<a href=""" + '"' + odpName +"/" + root + str(num+1) + """.htm"><img src=""" + '"' + odpName +'/' + file + '" style="border:0px"></a><br>' + "\n")
            htmlFile.write("""<embed src=""" + '"' + odpName +'/' + stem + '.mp3" autostart="true">' + "\n")

        else:
            # All subsequent pages
            htmlFile = open(DROPBOX_FOLDER+"\\" + odpName +"\\" +stem+".htm","w")
            writeHtmlHeader()
            htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> """)
            if num-offset==1:
                htmlFile.write("""<a href="../""" + odpName +""".htm">Back</a> """)
            else:
                htmlFile.write("""<a href=""" + '"' + root + str(num-1) + """.htm">Back</a> """)
            if num==maxNum:
                htmlFile.write("""Continue Last page<br>\n""")
                htmlFile.write("""<img src=""" + '"' + file + '" style="border:0px"><br>' + "\n")
            else:
                htmlFile.write("""<a href=""" + '"' + root + str(num+1) + """.htm">Continue</a> <a href=""" + '"' + maxImgHtml + '"' + \
            """>Last page</a><br>""" + "\n")
                htmlFile.write("""<a href=""" + '"' + root + str(num+1) + """.htm"><img src=""" + '"' + file + '" style="border:0px"></a><br>' + "\n")
            htmlFile.write("""<embed src=""" + '"' + stem + '.mp3" autostart="true">' + "\n")

        htmlFile.write('</center>' + "\n")
        htmlFile.write('</body>\n</html>\n')
        htmlFile.close()

##    print "Done"

if __name__ == '__main__':
    main()

