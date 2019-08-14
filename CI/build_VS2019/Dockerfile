# escape=`

ARG FROM_IMAGE=microsoft/dotnet-framework:3.5-sdk-windowsservercore-1709
FROM ${FROM_IMAGE}

# Reset the shell.
SHELL ["cmd", "/S", "/C"]

#COPY Install.cmd C:/TEMP/
ADD https://aka.ms/vscollect.exe C:/TEMP/collect.exe

# Download channel for fixed install.
ARG CHANNEL_URL=https://aka.ms/vs/16/release/channel
ADD ${CHANNEL_URL} C:/TEMP/VisualStudio.chman

# Download and install Build Tools for Visual Studio 2017 for native desktop workload.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe C:/TEMP/vs_buildtools.exe
RUN C:\\TEMP\\vs_buildtools.exe `
    --quiet --wait --norestart --nocache `
    --channelUri C:\\TEMP\\VisualStudio.chman `
    --installChannelUri C:\\TEMP\\VisualStudio.chman `
    --add Microsoft.VisualStudio.Workload.VCTools `
    --add Microsoft.VisualStudio.Component.VC.140 `
    --add Microsoft.VisualStudio.Component.VC.ATL `
    --add Microsoft.VisualStudio.Component.VC.CLI.Support `
    --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64	 `
    --includeRecommended `
    --installPath C:\BuildTools `
  || IF "%ERRORLEVEL%"=="3010" EXIT 0


RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe -OutFile C:\TEMP\python-3.7.4-amd64.exe ; `
  Start-Process C:\TEMP\python-3.7.4-amd64.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait ; `
  Remove-Item C:\TEMP\python-3.7.4-amd64.exe -Force

ADD CI/build_VS2019/deps.py c:\scripts\
RUN powershell.exe -Command `
      $ErrorActionPreference = 'Stop'; `
      [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
      $Env:PYTHONUNBUFFERED = 0 ; `
      python c:\scripts\deps.py ; `
      python -m pip install pip --no-cache-dir --upgrade ; `
      pip install --no-cache-dir conan


RUN powershell.exe -Command `	
  $ErrorActionPreference = 'Stop'; `	
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `	
  Invoke-WebRequest https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2-win64-x64.msi -OutFile C:\TEMP\cmake.msi ; `	
  Start-Process msiexec -ArgumentList '/i C:\TEMP\cmake.msi /q ADD_CMAKE_TO_PATH=System' -Wait ; `	
  Remove-Item C:\TEMP\cmake.msi -Force

RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://iweb.dl.sourceforge.net/project/nsis/NSIS%203/3.04/nsis-3.04-setup.exe -OutFile C:\TEMP\nsis-3.04-setup.exe ; `
  Start-Process C:\TEMP\nsis-3.04-setup.exe -ArgumentList "/S" -Wait; `
  Remove-Item C:\TEMP\nsis-3.04-setup.exe -Force

COPY conanfile.txt C:/TEMP/
ENV CONAN_COLOR_DISPLAY=0
ENV CONAN_NON_INTERACTIVE=1
RUN conan remote add -f bincrafters https://api.bintray.com/conan/bincrafters/public-conan
RUN conan install C:/TEMP/ --build  missing --no-import && conan remove * -b --src -f

ADD opengl32.dll c:\windows\system32

ENTRYPOINT C:\\BuildTools\\Common7\\Tools\\VsDevCmd.bat &&
CMD ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
