echo off
rem 20110910 JG Build script for odp2wts.exe for Windows
echo ====================
echo Building odp2wts.exe
echo ====================
if exist dist (rmdir dist /S)
python odp2exe.py py2exe
D:\NSIS\makensisw.exe Wiki-to-Speech-from-ODP.nsi
