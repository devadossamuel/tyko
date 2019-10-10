import urllib.request
import tempfile
import os
import subprocess
from zipfile import ZipFile

EXE_DEPS = [
    ("Git", "https://github.com/git-for-windows/git/releases/download/v2.22.0.windows.1/Git-2.22.0-64-bit.exe",  "Git-2.22.0-64-bit.exe", ['/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' '/NOCANCEL']),
    ("Wix Toolset", "https://github.com/wixtoolset/wix3/releases/download/wix3111rtm/wix311.exe", "wix311.exe", ["/quiet", "/install", "/norestart"]),
]

MSI_DEPS = [
    ("CMake", "https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2-win64-x64.msi", "cmake-3.15.2-win64-x64.msi", 'ADD_CMAKE_TO_PATH=System'),
]


ZIP_EXE_DEPS = [
    ("Ninja", "https://github.com/ninja-build/ninja/releases/download/v1.9.0/ninja-win.zip", "ninja-win.zip", 'C:\TEMP'),
]

def main():
    print("Downloading and installing required tools!")
    with tempfile.TemporaryDirectory() as tmpdir:
        installed_programs = set()

        for program_name, url, save_name, cli_args in EXE_DEPS:
            save_location = os.path.join(tmpdir, save_name)

            print("Installing {}".format(program_name))
            print("Downloading {}".format(url))
            urllib.request.urlretrieve(url, save_location)
            print("Saved {}".format(save_location))
            cmd = [save_location]
            cmd += cli_args
            print("Installing {}".format(save_name), flush=True)
            subprocess.run(cmd)
            installed_programs.add(program_name)

            
        for program_name, url, save_name, cli_args in MSI_DEPS:
            save_location = os.path.join(tmpdir, save_name)

            print("Installing {}".format(program_name))
            print("Downloading {}".format(url))
            urllib.request.urlretrieve(url, save_location)
            print("Saved {}".format(save_location))
            print("Installing {}".format(save_name), flush=True)
            cmd = ["msiexec", "/i", save_location, "/q"]
            cmd += cli_args
        
        for program_name, url, save_name, extract_path in ZIP_EXE_DEPS:
            save_location = os.path.join(tmpdir, save_name)

            print("Installing {}".format(program_name))
            print("Downloading {}".format(url))
            urllib.request.urlretrieve(url, save_location)
            print("Saved {}".format(save_location))
            print("Unzipping {}".format(save_name), flush=True)
            with ZipFile(save_location, 'r') as zip_obj:
                zip_obj.extractall(path=extract_path)

        print("Done installing {}".format(", ".join(installed_programs)))


if __name__ == "__main__":
    main()
