FIRST, try this command in Ubuntu/Linux:
```
sudo apt-get install  python-beautifulsoup python-pygame python-nltk python-yaml python-buzhug python-espeak
```

If that doesn't work (or you have a different operating system), try:

Bash script to prompt users for dependencies

# Introduction #

Working on a more helpful install wizard/ script. Help appreciated in sorting out bash call commands.


# Details #

```


#!/bin/bash
#absolutely amazing the number of dependencies a user has to get through in order for OADS to work!
#spacing counts in a bash script!
#need to figure out how to get script values out to console for debugging the equivalent of println for bash?
#would like to launch a browser to go to the page automatically=done
#zenity --info --title="Open Allure DS Installer" 
#######START#############
zenity --question --text="You are about to _attempt_ 
	an installation of Open Allure DS. Are you ready?"
rc=$?
if [ "${rc}" == "1" ]; then
	zenity --error --text "Installation terminated by user! Go read why you should install "	
	google-chrome http://code.google.com/p/open-allure-ds/
	echo $rc     
   echo "Value of 1 equals program terminated."
   exit 1
	echo "Proceeding"
fi

###########BEAUTIFUl soup############
zenity --question --text "Do you have Beautiful Soup installed?"
rc=$?
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install beautiful Soup before going on! 
	You can find it here: http://www.crummy.com/software/BeautifulSoup/ Click OK to go there now." 
	google-chrome http://www.crummy.com/software/BeautifulSoup/
	echo $rc    
   echo "Value of 1 equals NO. Go install Beautiful Soup and come back."
   exit 1
#if [ "${rc}" == "0" ];then
#	echo "Proceeding"
fi

#############dragonfly##############
zenity --question --text "Do you have Dragonfly installed? Click no to go there now."
rc=$?
if [ "${rc}" == "1" ]; then
   google-chrome http://code.google.com/p/dragonfly/downloads/list	
	echo "Go install Dragonfly and come back"	

fi

#############pygame###########
zenity --question --text "Do you have pygame installed?"
rc=$?
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install Pygame before going on! 
	You can find it here: c Click ok to go there now."
   google-chrome http://www.pygame.org/download.shtml
	echo "Go install Pygame and come back"
	exit 1
fi
##############ipython###################
zenity --question --text "Do you have ipython installed? 
Ipython satifies configobj requirement"
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install ipython before going on! 
	You can find it here: http://ipython.scipy.org/moin/Download. Click OK to go there now."
   google-chrome http://ipython.scipy.org/moin/Download
	echo "Go install ipython and come back"
	exit 1
fi
################nltk####################
zenity --question --text "Do you have NLTK installed? 
It has lots of sub dependencies so look carefully."
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install NLTK before going on! 
	You can find it here: http://www.nltk.org/download. Click OK to go there now."
   google-chrome http://www.nltk.org/download
	echo "Go install ipython and come back"
	exit 1
fi

##################pyyaml################
zenity --question --text "Do you have PyYAML installed? 
It has lots of sub dependencies so look carefully."
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install PyYAML before going on! 
	You can find it here: http://code.google.com/p/nltk/downloads/list. Click OK to go there now."
   google-chrome http://code.google.com/p/nltk/downloads/list
	echo "Go install ipython and come back. Or you could use sudo yum install PyYAML"
	exit 1
fi

####################buzhug##################
zenity --question --text "Do you have espeak installed? 
It has lots of sub dependencies so look carefully."
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install buzhug before going on! 
	You can find it here: http://buzhug.sourceforge.net/. Click OK to go there now."
   google-chrome http://buzhug.sourceforge.net/
	echo "Go install buzhug and come back."
	exit 1
fi


###############espeak#######################

zenity --question --text "Do you have espeak installed?"
if [ "${rc}" == "1" ]; then
	zenity --error --text "Please install espeak before going on! 
	You can find it here: http://code.google.com/p/nltk/downloads/list. Click OK to go there now."
   google-chrome http://espeak.sourceforge.net/download.html
	echo "Go install espeak and come back. Or you could use: sudo yum install espeak"
	exit 1
fi



```