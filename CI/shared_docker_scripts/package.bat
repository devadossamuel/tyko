 setlocal
 if not exist c:\TEMP\build mkdir c:\TEMP\build
 xcopy c:\build c:\TEMP\build
 cd c:\TEMP\build && cpack -G ZIP;NSIS;WIX -C Release || EXIT 1
 copy *.msi c:\dist\
 copy *.exe c:\dist\
 copy *.zip c:\dist\
 endlocal
