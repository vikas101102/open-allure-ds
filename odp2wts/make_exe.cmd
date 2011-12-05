echo off
rem 20110910 JG Build script for odp2wts.exe for Windows
rem 20111129 JG Modified to run for SlideSpeech
echo ====================
echo Building odp2ss.exe
echo ====================
if exist dist (rmdir dist /S)
python odp2exe.py py2exe
D:\NSIS\makensisw.exe SlideSpeech-from-ODP.nsi
