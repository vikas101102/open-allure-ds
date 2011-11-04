; check for latest version of UltraModernUI at https://sourceforge.net/projects/ultramodernui/files/UltraModernUI/
!include "D:\open-allure-ds\odp2wts\UMUI.nsh"
!include Library.nsh

Var ALREADY_INSTALLED ; variable - no {} needed, just $

!define WIKI_TO_SPEECH_VERSION "0.1.18" ; define - ${} needed

!define MUI_ICON "D:\open-allure-ds\odp2wts\openallure_32x32.ico"
!define UMUI_LEFTIMAGE_BMP "D:\open-allure-ds\odp2wts\openallure_left.bmp"

; Welcome
!define MUI_PAGE_HEADER_TEXT "Wiki-to-Speech from ODP"
!define MUI_WELCOMEPAGE_TITLE "Wiki-to-Speech from ODP v.${WIKI_TO_SPEECH_VERSION}"
!define MUI_WELCOMEPAGE_TEXT "Wiki-to-Speech from ODP turns your presentation \
into a slide show with voice over and a video. \
\r\n\r\nClick Next to start installation."
!insertmacro MUI_PAGE_WELCOME

; Licence
; !insertmacro MUI_PAGE_LICENSE "D:\open-allure-ds\odp2wts\LICENSE.txt"

; Location folder
!insertmacro MUI_PAGE_DIRECTORY

; Install files
!insertmacro MUI_PAGE_INSTFILES

; Finish
!define MUI_FINISHPAGE_TITLE "Wiki-to-Speech from ODP should now be ready to use"
!define MUI_FINISHPAGE_TEXT "See on-line documentation for details."
!define MUI_FINISHPAGE_LINK "Wiki-to-Speech Documentation"
!define MUI_FINISHPAGE_LINK_LOCATION "http://code.google.com/p/wiki-to-speech/wiki/Resources"
!insertmacro MUI_PAGE_FINISH

; Uninstall
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; http://forums.winamp.com/printthread.php?s=4d90165acf6fa187290bbbe00bb790b7&threadid=202244
;after all the other insertmacros
!insertmacro MUI_LANGUAGE "English"

;--------------------------------

; The name of the installer
Name "Wiki-to-Speech from ODP"

; The file to write
OutFile "Wiki-to-Speech-from-ODP-win-${WIKI_TO_SPEECH_VERSION}.exe"

; Default installation directory
InstallDir "$PROGRAMFILES\Wiki-to-Speech-from-ODP"
; The text to prompt the user to enter a directory
DirText "Please choose the directory where you would like Wiki-to-Speech from ODP installed."
;ShowInstDetails show
;ShowUnInstDetails show

; Request application privileges for Windows Vista
RequestExecutionLevel admin # http://forums.gforums.winamp.com/showthread.php?s=8a0906800e16ffd51be2d2fda1a23c4c&threadid=306563
; user is the other option I used to use

; http://nsis.sourceforge.net/Docs/Chapter4.html#4.8.1
;4.8.1.32 RequestExecutionLevel
;none|user|highest|admin
;Specifies the requested execution level for Windows Vista and Windows 7. The value is embedded in the installer and
; uninstaller's XML manifest and tells Vista/7, and probably future versions of Windows, what privileges level the
; installer requires. user requests the a normal user's level with no administrative privileges. highest will request
; the highest execution level available for the current user and will cause Windows to prompt the user to verify
; privilege escalation. The prompt might request for the user's password. admin requests administrator level and
; will cause Windows to prompt the user as well. Specifying none, which is also the default, will keep the manifest
; empty and let Windows decide which execution level is required. Windows Vista/7 automatically identifies NSIS
; installers and decides administrator privileges are required. Because of this, none and admin have virtually the same effect.
;It's recommended, at least by Microsoft, that every application will be marked with the required execution level.
; Unmarked installers are subject to compatibility mode. Workarounds of this mode include automatically moving any
; shortcuts created in the user's start menu to all users' start menu. Installers that need not install anything into
; system folders or write to the local machine registry (HKLM) should specify user execution level.
;More information about this topic can be found at MSDN. Keywords include "UAC", "requested execution level",
; "vista manifest" and "vista security".

;--------------------------------

Section ""

  CreateDirectory $INSTDIR
  SetOutPath "$INSTDIR"

  File "D:\open-allure-ds\odp2wts\openallure_32x32.ico"

  File /r "D:\open-allure-ds\odp2wts\dist\*.*"

  ; http://osdir.com/ml/python.db.pysqlite.user/2005-05/msg00040.html (can be missing)
  ; http://nsis.sourceforge.net/Docs/AppendixB.html
  IfFileExists "$INSTDIR\odp2wts.exe" 0 new_installation ; continue if true, else jump to new_installation label
    StrCpy $ALREADY_INSTALLED 1 ;set to non-zero value if already installed
  new_installation: ; already installed stays as initialised

  ; WAIT FOR JOHN TO SUPPLY
  ;!insertmacro InstallLib REGDLL $ALREADY_INSTALLED REBOOT_NOTPROTECTED "G:\openallure\msvcr71.dll" $SYSDIR\msvcr100.dll $SYSDIR

  SetOutPath $INSTDIR
  ;Create shortcuts etc
  ;create desktop shortcut
  CreateShortCut "$DESKTOP\Wiki-to-Speech from ODP.lnk" \
                 "$INSTDIR\odp2wts.exe" "" \
                 "$INSTDIR\openallure_32x32.ico"

  CreateDirectory "$SMPROGRAMS\Wiki-to-Speech"
  CreateShortCut "$SMPROGRAMS\Wiki-to-Speech\Wiki-to-Speech from ODP.lnk" \
                 "$INSTDIR\odp2wts.exe" "" \
                 "$INSTDIR\openallure_32x32.ico"
  CreateShortCut "$SMPROGRAMS\Wiki-to-Speech\Uninstall.lnk" \
                 "$INSTDIR\Uninstall.exe" "" \
                 "$INSTDIR\uninstall.exe" 0
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd ; end the section

;--------------------------------

;Uninstaller Section

Section "Uninstall"

  RMDir /r /REBOOTOK $INSTDIR
  RMDir /r /REBOOTOK "$PROFILE\Wiki-to-Speech"
  RMDir /r "$SMPROGRAMS\Wiki-to-Speech"
  Delete "$DESKTOP\Wiki-to-Speech from ODP.lnk"

SectionEnd

