echo off
rem 20111205 JG Modified to run for SlideSpeech
echo ====================
echo Building SlideSpeech.exe
echo ====================
if exist dist (rmdir dist /S)
python ss2exe.py py2exe
D:\NSIS\makensisw.exe SlideSpeech.nsi
