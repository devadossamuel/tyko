# escape=`

ARG FROM_IMAGE=microsoft/dotnet-framework:3.5-sdk-windowsservercore-1709
FROM ${FROM_IMAGE}

# Reset the shell.
SHELL ["cmd", "/S", "/C"]

#COPY Install.cmd C:/TEMP/
ADD https://aka.ms/vscollect.exe C:/TEMP/collect.exe

# Install Node.js LTS
ADD https://nodejs.org/dist/v8.11.3/node-v8.11.3-x64.msi C:/TEMP/node-install.msi
RUN start /wait msiexec.exe /i C:/TEMP/node-install.msi /l*vx "%TEMP%\MSI-node-install.log" /qn ADDLOCAL=ALL

# Download channel for fixed install.
ARG CHANNEL_URL=https://aka.ms/vs/15/release/channel
ADD ${CHANNEL_URL} C:/TEMP/VisualStudio.chman

# Download and install Build Tools for Visual Studio 2017 for native desktop workload.
ADD https://aka.ms/vs/15/release/vs_buildtools.exe C:/TEMP/vs_buildtools.exe
RUN C:\\TEMP\\vs_buildtools.exe `
    --quiet --wait --norestart --nocache `
    --channelUri C:\\TEMP\\VisualStudio.chman `
    --installChannelUri C:\\TEMP\\VisualStudio.chman `
    --add Microsoft.VisualStudio.Workload.VCTools `
    --add Microsoft.VisualStudio.Component.VC.140 `
    --add Microsoft.VisualStudio.Component.VC.ATL `
    --add Microsoft.VisualStudio.Component.VC.CLI.Support `
    --includeRecommended `
    --installPath C:\BuildTools `
  || IF "%ERRORLEVEL%"=="3010" EXIT 0

#RUN @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
#RUN choco install -y cmake --installargs 'ADD_CMAKE_TO_PATH=System'
#RUN choco install -y python ninja
#RUN python -m pip install --upgrade pip && python -m pip install conan

RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://github.com/git-for-windows/git/releases/download/v2.22.0.windows.1/Git-2.22.0-64-bit.exe -OutFile C:\TEMP\Git-2.22.0-64-bit.exe ; `
  Start-Process C:\TEMP\Git-2.22.0-64-bit.exe -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /NOCANCEL' -Wait ; `
  Remove-Item C:\TEMP\Git-2.22.0-64-bit.exe -Force


RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://github.com/ninja-build/ninja/releases/download/v1.9.0/ninja-win.zip -OutFile C:\TEMP\ninja-win.zip ;`
  Expand-Archive -Path C:\TEMP\ninja-win.zip -DestinationPath C:\TEMP\ ;`
#   Start-Process msiexec -ArgumentList '/i C:\TEMP\cmake.msi /q ADD_CMAKE_TO_PATH=System' -Wait ; `
  Remove-Item C:\TEMP\ninja-win.zip -Force



RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2-win64-x64.msi -OutFile C:\TEMP\cmake.msi ; `
  Start-Process msiexec -ArgumentList '/i C:\TEMP\cmake.msi /q ADD_CMAKE_TO_PATH=System' -Wait ; `
  Remove-Item C:\TEMP\cmake.msi -Force

RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://github.com/wixtoolset/wix3/releases/download/wix3111rtm/wix311.exe -OutFile C:\TEMP\wix311.exe ; `
  Start-Process C:\TEMP\wix311.exe -ArgumentList '/q' -Wait ; `
  Remove-Item C:\TEMP\wix311.exe -Force

RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe -OutFile C:\TEMP\python-3.7.4-amd64.exe ; `
  Start-Process C:\TEMP\python-3.7.4-amd64.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait ; `
  Remove-Item C:\TEMP\python-3.7.4-amd64.exe -Force

RUN python -m pip install pip --upgrade && pip install conan

COPY conanfile.txt C:/TEMP/
ENV CONAN_COLOR_DISPLAY=0
ENV CONAN_NON_INTERACTIVE=1
RUN conan remote add -f bincrafters https://api.bintray.com/conan/bincrafters/public-conan
RUN set PYTHONUNBUFFERED=TRUE && conan install C:/TEMP/ --build  missing --no-import && conan remove * --src -f

RUN powershell.exe -Command `
  $ErrorActionPreference = 'Stop'; `
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
  Invoke-WebRequest https://iweb.dl.sourceforge.net/project/nsis/NSIS%203/3.04/nsis-3.04-setup.exe -OutFile C:\TEMP\nsis-3.04-setup.exe ; `
  Start-Process C:\TEMP\nsis-3.04-setup.exe -ArgumentList "/S" -Wait; `
  Remove-Item C:\TEMP\nsis-3.04-setup.exe -Force

ADD opengl32.dll c:\windows\system32


ENTRYPOINT C:\\BuildTools\\Common7\\Tools\\VsDevCmd.bat &&
CMD ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
