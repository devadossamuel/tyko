import os

from conans import ConanFile, CMake


class TykoConan(ConanFile):
    name = "Tyko QML client"
    version = "0.0.1a1"
    url = "https://github.com/UIUCLibrary/tyko"
    license = "University of Illinois/NCSA Open Source License"
    author = 'University Library at The University of Illinois at Urbana Champaign: Preservation Services'
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake_paths"]
    requires = [
        "qt/5.14.1@bincrafters/stable",
        "bzip2/1.0.8@conan/stable"
    ]

    default_options = {
        "qt:qtquickcontrols": True,
        "qt:qtquickcontrols2": True,
        "qt:with_mysql": False,
        "qt:with_sqlite3": False,
        "qt:qttools": True,
    }

    def build(self):

        cmake = CMake(self)
        cmake_toolchain_file = os.path.join(self.build_folder, "conan_paths.cmake")
        assert os.path.exists(cmake_toolchain_file)
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = cmake_toolchain_file
        if cmake.is_multi_configuration is True:
            cmake.definitions[f"CMAKE_RUNTIME_OUTPUT_DIRECTORY_{cmake.build_type.upper()}"] = self.build_folder
        else:
            cmake.definitions[f"CMAKE_RUNTIME_OUTPUT_DIRECTORY"] = self.build_folder
        cmake.configure()
        cmake.build()

    def configure(self):
        if self.settings.os == "Windows":
            self.options["qt"].opengl = "dynamic"

    def imports(self):
        self.copy("*.dll", "", "bin")
        self.copy("*.dylib", "lib", "lib")
        self.copy("*.dll", "platforms/", "plugins/platforms")
        self.copy("builtins.qmltypes", "qml/", "qml")
        self.copy("*", "qml/QtQuick", "qml/QtQuick")
        self.copy("*", "qml/QtQml", "qml/QtQml")
        self.copy("*", "qml/QtQuick.2", "qml/QtQuick.2")

    def package(self):
        self.copy("avdatabaseEditor", "bin", "")
        self.copy("avdatabaseEditor.exe", "", "")
