# escape=`
# Wix Toolset needs dotnet 3.5 to run
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:3.5
FROM ${FROM_IMAGE}

# Reset the shell.
SHELL ["cmd", "/S", "/C"]
RUN mkdir c:\\TEMP
#COPY Install.cmd C:/TEMP/
ADD https://aka.ms/vscollect.exe C:/TEMP/collect.exe

# Download channel for fixed install.
ARG CHANNEL_URL=https://aka.ms/vs/16/release/channel
ADD ${CHANNEL_URL} C:/TEMP/VisualStudio.chman

# Download and install Build Tools for Visual Studio 2017 for native desktop workload.

ADD https://aka.ms/vs/16/release/vs_buildtools.exe C:/TEMP/vs_buildtools.exe
#--add Microsoft.VisualStudio.Component.VC.140 `
RUN (C:\\TEMP\\vs_buildtools.exe `
    --quiet --wait --norestart --nocache `
    --channelUri C:\\TEMP\\VisualStudio.chman `
    --installChannelUri C:\\TEMP\\VisualStudio.chman `
    --add Microsoft.VisualStudio.Workload.VCTools;includeRecommended `
    --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest `
    --add Microsoft.VisualStudio.Component.VC.ATL `
    --add Microsoft.VisualStudio.Component.VC.CLI.Support `
    --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64	 `
    --includeRecommended `
    --installPath C:\BuildTools `
  || IF "%ERRORLEVEL%"=="3010" EXIT 0 )`
  && @echo Cleaning up temp files`
  && del /S /F /Q %temp% `
  && del /S /F /Q %Windir%\Temp `
  && @echo Done cleaning up files in temp directories

RUN @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" `
    && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

RUN choco install -y git python nsis wixtoolset ninja`
    && choco install -y cmake --installargs 'ADD_CMAKE_TO_PATH=System' `
    && del /S /F /Q %ChocolateyInstall%
#    rmdir C:\ProgramData\chocolatey /s /q
ARG CONAN_USER_HOME=C:\\conan
ENV CONAN_COLOR_DISPLAY=0 CONAN_NON_INTERACTIVE=1 CONAN_USER_HOME=${CONAN_USER_HOME}

ADD CI/build_VS2019/conan/profiles/default ${CONAN_USER_HOME}\.conan\profiles\default
ADD CI/build_VS2019/conan/remotes.json ${CONAN_USER_HOME}\.conan\remotes.json
RUN powershell.exe -Command `
      $ErrorActionPreference = 'Stop'; `
      [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
      $Env:PYTHONUNBUFFERED = 0 ; `
      python -m pip install pip --no-cache-dir --upgrade ; `
      pip install --no-cache-dir conan ;`
      Write-Output "Finished installing Conan"

COPY conanfile.txt C:/TEMP/
# THIS is needed for CPack to not fail at the fixup stage. This DLL shouldn't actually be included in distributions
ADD opengl32.dll c:\windows\system32
ADD ["CI/build_VS2019/vcvarsall.bat", "C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/VC/Auxiliary/Build/vcvarsall.bat"]
RUN conan install C:/TEMP/ --build  missing --no-import `
    && conan remove * -b --src -f

ENTRYPOINT C:\\BuildTools\\Common7\\Tools\\VsDevCmd.bat -no_logo -arch=amd64 -host_arch=amd64 -vcvars_ver=14.2 &&
CMD ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
