cmake_minimum_required(VERSION 3.14)
project(avdatabaseEditor LANGUAGES CXX)

#find_package(CURL REQUIRED)
#find_package(OpenSSL REQUIRED)
#find_package(ZLIB REQUIRED)
#find_package(Qt5 REQUIRED
#        COMPONENTS
#            Core
#            Quick
#            QuickControls2
#            Widgets
##        OPTIONAL_COMPONENTS
##            QuickTest
#    )
#add_library(PostCurl OBJECT
#        CurlPostBehavior.cpp
#        )
#
#target_link_libraries(PostCurl
#    PRIVATE
#        CURL::libcurl
#        )
#
#add_library(ProjectAdder
#        projectadder.cpp
#        qtPostBehavior.cpp qtPostBehavior.h
#    )

#target_link_libraries(ProjectAdder
#    PUBLIC
#        Qt5::Core
#        Qt5::Quick
#    PRIVATE
#        PostCurl
#    )


add_executable(avdatabaseEditor
        "main.cpp"
        "qml.qrc"
        )
set_target_properties(avdatabaseEditor PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    )

#target_link_libraries(avdatabaseEditor PRIVATE Qt5::Core Qt5::Widgets Qt5::Quick)

target_link_libraries(avdatabaseEditor
        PRIVATE
            Qt5::Core
            Qt5::Quick
#            ProjectAdder
            Qt5::Qml
            Qt5::QuickControls2
            Qt5::Widgets

        )
#get_target_property(editor_apple_bundle avdatabaseEditor MACOSX_BUNDLE)
install(TARGETS avdatabaseEditor RUNTIME DESTINATION bin)
#
#
#if(editor_apple_bundle)
#
#    install(CODE [[
#        include(BundleUtilities)
#        copy_and_fixup_bundle($<TARGET_BUNDLE_DIR:avdatabaseEditor> ${CMAKE_INSTALL_PREFIX}/avdatabaseEditor.app "" "")
#    ]])
#
#endif()
#
if(WIN32)
    include(InstallRequiredSystemLibraries)
#
#    #========================================================================
#    #    the root for QT should be one directory up from the Qt5 core runtime
#    get_target_property(Qt_root_path Qt5::Core LOCATION)
#    get_filename_component(Qt_root_path ${Qt_root_path} DIRECTORY)
#    get_filename_component(Qt_root_path ${Qt_root_path} DIRECTORY)
#    #========================================================================
#
    find_file(platform_plugin
        NAMES
            qwindows
            qwindows.dll
        PATHS
            ${CMAKE_BINARY_DIR}/platforms
            ${Qt_root_path}/plugins/platforms
            )
#
    install(FILES ${platform_plugin} DESTINATION bin/platforms)
    find_path(QML_DIR
            NAMES
                builtins.qmltypes
            PATHS
                ${CMAKE_BINARY_DIR}/qml
            )
    install(DIRECTORY ${QML_DIR} DESTINATION bin)
endif()
install(CODE [[
            if(WIN32)
                set(CMAKE_FIND_LIBRARY_SUFFIXES ".dll")
                set(CMAKE_FIND_LIBRARY_PREFIXES "")
            endif()
            find_library(QTQUICK2PLUGIN
                NAMES
                    qtquick2plugin
                    qtquick2plugin.dll
                HINTS
                    ${CMAKE_INSTALL_PREFIX}/bin/qml/QtQuick.2
            )
            list(APPEND PLUGIN_LIBRARIES ${QTQUICK2PLUGIN})

            find_library(QTQUICKCONTROLS2PLUGIN
                NAMES
                    qtquickcontrols2plugin
                    qtquickcontrols2plugin.dll
                HINTS
                    ${CMAKE_INSTALL_PREFIX}/bin/qml/QtQuick/Controls.2
            )
            list(APPEND PLUGIN_LIBRARIES  ${QTQUICKCONTROLS2PLUGIN})

            find_library(QTQUICKCONTROLSPLUGIN
                NAMES
                    qtquickcontrolsplugin
                    qtquickcontrolsplugin.dll
                HINTS
                    ${CMAKE_INSTALL_PREFIX}/bin/qml/QtQuick/Controls
            )
            list(APPEND PLUGIN_LIBRARIES  ${QTQUICKCONTROLSPLUGIN})

            include(BundleUtilities)
            set(EXE_TO_FIXUP "${CMAKE_INSTALL_PREFIX}/bin/$<TARGET_FILE_NAME:avdatabaseEditor>")

            fixup_bundle("${EXE_TO_FIXUP}"
                    "${PLUGIN_LIBRARIES}"
                    ""
                     "${lib_paths}"
                     IGNORE_ITEM "OPENGL32.dll;opengl32.dll")
]])
#

##
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
