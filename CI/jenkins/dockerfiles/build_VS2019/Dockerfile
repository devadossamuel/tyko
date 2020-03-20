# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE}
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

ARG CHOCOLATEY_REPO=https://chocolatey.org/api/v2

ARG ChocolateyEnvironmentDebug=false
ADD CI/jenkins/dockerfiles/shared/install_choco.ps1 choco/install_choco.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_REPO ; `
    choco source remove -n chocolatey ; choco source add -n=chocolatey_repo -s=\"$env:CHOCOLATEY_REPO\" ; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe

# Install packages that can be installed by chocolatey
ADD CI/jenkins/dockerfiles/build_VS2019/chocolatey/packages.config choco/packages.config
RUN choco install -y choco/packages.config --no-progress --stoponfirstfailure;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    Write-Host "Finished install packages with Chocolatey"

# Install WiX toolset for making .msi installers and put the tools on the path
ADD CI/jenkins/dockerfiles/build_VS2019/nuget/packages.config nuget/packages.config
RUN Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force ; `
    nuget update -self ;`
    nuget install nuget/packages.config -OutputDirectory c:\BuildTools\ ; `
    [Environment]::SetEnvironmentVariable('PATH', \"$($env:Path);$((Get-Childitem -Path C:\BuildTools -Include wix.dll -File -Recurse)[0].DirectoryName)\", [EnvironmentVariableTarget]::Machine)


ARG CONAN_USER_HOME=C:\\conan
ENV CONAN_COLOR_DISPLAY=0 CONAN_NON_INTERACTIVE=1 CONAN_USER_HOME=${CONAN_USER_HOME}
RUN [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
    $Env:PYTHONUNBUFFERED = 0 ; `
    python -m pip install pip --no-cache-dir --upgrade ; `
    pip install --no-cache-dir conan ;`
    Write-Output "Finished installing Conan"
ADD CI/jenkins/dockerfiles/build_VS2019/conan/profiles/default ${CONAN_USER_HOME}/.conan/profiles/default
ADD CI/jenkins/dockerfiles/build_VS2019/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
ADD CI/jenkins/dockerfiles/build_VS2019/startup.bat c:/temp/startup.bat

#
## This is to redirect anything that might require that visual studio vcvarsall.bat be in fixed spot
ADD ["CI/jenkins/dockerfiles/build_VS2019/vcvarsall.bat", "C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/VC/Auxiliary/Build/vcvarsall.bat"]
#
RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"
#RUN certutil -generateSSTFromWU roots.sst ; `
#    certutil -addstore -f root roots.sst ; `
#    del roots.sst
COPY conanfile.py C:/TEMP/
RUN conan install C:/TEMP/ --build  missing --no-import ;`
    conan remove * -b --src -f

SHELL ["cmd", "/S", "/C"]
