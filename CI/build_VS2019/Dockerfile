# escape=`

ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:3.5
FROM ${FROM_IMAGE}

# Reset the shell.
SHELL ["cmd", "/S", "/C"]
RUN mkdir c:\\TEMP
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
ARG CHOCOLATEY_SOURCE="https://chocolatey.org/api/v2"
ADD CI/build_VS2019/packages.config packages.config
RUN C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --source=$Env:CHOCOLATEY_SOURCE packages.config ;`
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse
ARG CONAN_USER_HOME=C:\\conan
ENV CONAN_COLOR_DISPLAY=0 CONAN_NON_INTERACTIVE=1 CONAN_USER_HOME=${CONAN_USER_HOME}
RUN [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
    $Env:PYTHONUNBUFFERED = 0 ; `
    python -m pip install pip --no-cache-dir --upgrade ; `
    pip install --no-cache-dir conan ;`
    Write-Output "Finished installing Conan"
ADD CI/build_VS2019/conan/profiles/default ${CONAN_USER_HOME}\.conan\profiles\default
ADD CI/build_VS2019/conan/remotes.json ${CONAN_USER_HOME}\.conan\remotes.json
ADD CI/build_VS2019/startup.bat c:\temp\startup.bat

# This is to redirect anything that might require that visual studio vcvarsall.bat be in fixed spot
ADD ["CI/build_VS2019/vcvarsall.bat", "C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/VC/Auxiliary/Build/vcvarsall.bat"]

RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"
RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst
COPY conanfile.txt C:/TEMP/
RUN conan install C:/TEMP/ --build  missing --no-import ;`
    conan remove * -b --src -f
