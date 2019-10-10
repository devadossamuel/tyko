cmake_minimum_required(VERSION 3.14)
project(avdatabaseEditor LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(CURL REQUIRED)
find_package(OpenSSL REQUIRED)
#find_package(ZLIB REQUIRED)
find_package(Qt5 REQUIRED
        COMPONENTS
            Core
            Quick
            QuickControls2
            Widgets
        OPTIONAL_COMPONENTS
            QuickTest
    )
add_library(PostCurl OBJECT
        CurlPostBehavior.cpp
        )

target_link_libraries(PostCurl
    PRIVATE
        CURL::libcurl
        )

add_library(ProjectAdder
        projectadder.cpp
        qtPostBehavior.cpp qtPostBehavior.h
    )

target_link_libraries(ProjectAdder
    PUBLIC
        Qt5::Core
        Qt5::Quick
    PRIVATE
        PostCurl
    )


add_executable(avdatabaseEditor
        "main.cpp"
        "qml.qrc"
        )
set_target_properties(avdatabaseEditor PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    )


target_link_libraries(avdatabaseEditor
        PRIVATE
            Qt5::Core
            Qt5::Quick
            ProjectAdder
            Qt5::Qml
            Qt5::QuickControls2
            Qt5::Widgets

        )

get_target_property(editor_apple_bundle avdatabaseEditor MACOSX_BUNDLE)
install(TARGETS avdatabaseEditor)


if(editor_apple_bundle)

    install(CODE [[
        include(BundleUtilities)
        copy_and_fixup_bundle($<TARGET_BUNDLE_DIR:avdatabaseEditor> ${CMAKE_INSTALL_PREFIX}/avdatabaseEditor.app "" "")
    ]])

endif()

if(WIN32)

    #========================================================================
    #    the root for QT should be one directory up from the Qt5 core runtime
    get_target_property(Qt_root_path Qt5::Core LOCATION)
    get_filename_component(Qt_root_path ${Qt_root_path} DIRECTORY)
    get_filename_component(Qt_root_path ${Qt_root_path} DIRECTORY)
    #========================================================================

    find_file(platform_plugin
        NAMES
            qwindows
            qwindows.dll
        PATHS
            ${Qt_root_path}/plugins/platforms
            )

#    message(STATUS "Using ${platform_plugin} for the qt platform plugin")
#    install(FILES ${platform_plugin} DESTINATION bin/platforms)

#    FIND QML PATHS:
    find_path(QML_QtQuick
        NAMES
            Controls/qtquickcontrolsplugin.dll
            Controls/libqtquickcontrolsplugin.dylib
        PATHS
            ${Qt_root_path}/qml
        PATH_SUFFIXES
            QtQuick
        )

    find_path(QML_QtQuick.2
        NAMES
            qtquick2plugin.dll
            libqtquick2plugin.dylib
        PATHS
            ${Qt_root_path}/qml
        PATH_SUFFIXES
            QtQuick.2
        )

    find_path(QML_QtQML
        NAMES
            Models.2/modelsplugin.dll
            Models.2/libmodelsplugin.dylib
        PATHS
            ${Qt_root_path}/qml
        PATH_SUFFIXES
            QtQML
        )

#    install(DIRECTORY
#                ${QML_QtQuick.2}
#                ${QML_QtQuick}
#                ${QML_QtQML}
#            DESTINATION
#                bin
#        )

    #    ##############################

    set_target_properties(avdatabaseEditor PROPERTIES
            WIN32_EXECUTABLE OFF
        )

    set_property(INSTALL "bin/$<TARGET_FILE_NAME:avdatabaseEditor>"
            PROPERTY
                CPACK_START_MENU_SHORTCUTS "Tyko"
        )

#    install(FILES
##                $<TARGET_FILE:Qt5::Widgets>
#                $<TARGET_FILE:Qt5::QuickControls2>
#            DESTINATION bin
#        )

#     set(CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP TRUE)
    set(CMAKE_INSTALL_UCRT_LIBRARIES TRUE)
    include(InstallRequiredSystemLibraries)
    install(PROGRAMS ${CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS}
                    DESTINATION bin
                    )
    get_filename_component(CURL_PARENT_DIR $<TARGET_FILE_DIR:CURL::libcurl> DIRECTORY)

    get_target_property(_qmake_executable Qt5::qmake IMPORTED_LOCATION)
    get_filename_component(_qt_bin_dir "${_qmake_executable}" DIRECTORY)
    find_program(WINDEPLOYQT_EXECUTABLE windeployqt HINTS "${_qt_bin_dir}")
    install(CODE [[
            find_program(WINDEPLOYQT_EXECUTABLE windeployqt HINTS $<TARGET_FILE_DIR:Qt5::qmake>)
#            get_filename_component(CURL_PARENT_DIR $<TARGET_FILE_DIR:CURL::libcurl> DIRECTORY)
            list(APPEND lib_paths "$<TARGET_FILE_DIR:avdatabaseEditor>")
#            list(APPEND lib_paths "${CURL_PARENT_DIR}/bin")
#            list(APPEND lib_paths "$<TARGET_FILE_DIR:Qt5::Core>")
            set(QML_PATH $<TARGET_PROPERTY:avdatabaseEditor,SOURCE_DIR>)
            execute_process(
                COMMAND "${CMAKE_COMMAND}" -E
                    env PATH="${_qt_bin_dir}" "${WINDEPLOYQT_EXECUTABLE}"
                        --qmldir ${QML_PATH}
                        --dry-run
                        --no-compiler-runtime
                        --list mapping
                        $<TARGET_FILE:avdatabaseEditor>
                OUTPUT_VARIABLE _output
                OUTPUT_STRIP_TRAILING_WHITESPACE
            )
            separate_arguments(_files WINDOWS_COMMAND ${_output})
            while(_files)
                list(GET _files 0 _src)
                list(GET _files 1 _dest)
                execute_process(
                    COMMAND "${CMAKE_COMMAND}" -E
                        copy_if_different ${_src} "${CMAKE_INSTALL_PREFIX}/bin/${_dest}"
                )
                list(REMOVE_AT _files 0 1)
            endwhile()
            include(BundleUtilities)
            set(EXE_TO_FIXUP "${CMAKE_INSTALL_PREFIX}/bin/$<TARGET_FILE_NAME:avdatabaseEditor>")
            message("Fixing up ${EXE_TO_FIXUP}")
            fixup_bundle("${EXE_TO_FIXUP}"
#                         "${CMAKE_INSTALL_PREFIX}/bin/$<TARGET_FILE_NAME:Qt5::QuickControls2>"
                         ""
                         "${lib_paths}"
                         IGNORE_ITEM "OPENGL32.dll")
        ]])

endif()
#
#enable_testing()
#
#add_executable(tst_editor "tst_editor.cpp" "tests.qrc")
#target_link_libraries(tst_editor
#        PRIVATE
#            Qt5::QuickTest
#            Qt5::Quick
#            Qt5::Qml
##            ProjectAdder
#
#    )
#
#
#add_dependencies(tst_editor avdatabaseEditor)
#add_test(tst_editor tst_editor -input ${CMAKE_CURRENT_SOURCE_DIR})
