cmake_minimum_required(VERSION 3.14)
project(avdatabaseEditor LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(CURL REQUIRED)
#find_package(OpenSSL REQUIRED)
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

    message(STATUS "Using ${platform_plugin} for the qt platform plugin")
    install(FILES ${platform_plugin} DESTINATION bin/platforms)

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

    install(DIRECTORY
                ${QML_QtQuick}
                ${QML_QtQuick.2}
                ${QML_QtQML}
            DESTINATION
                bin
        )

    #    ##############################

    set_target_properties(avdatabaseEditor PROPERTIES
            WIN32_EXECUTABLE ON
        )

    set_property(INSTALL "bin/$<TARGET_FILE_NAME:avdatabaseEditor>"
            PROPERTY
                CPACK_START_MENU_SHORTCUTS "AV Database"
        )

    install(FILES
                $<TARGET_FILE:Qt5::Widgets>
                $<TARGET_FILE:Qt5::QuickControls2>
            DESTINATION bin
        )

    install(CODE [[
            get_filename_component(CURL_PARENT_DIR $<TARGET_FILE_DIR:CURL::libcurl> DIRECTORY)
            list(APPEND lib_paths $<TARGET_FILE_DIR:avdatabaseEditor>)
            list(APPEND lib_paths ${CURL_PARENT_DIR}/bin)
            list(APPEND lib_paths $<TARGET_FILE_DIR:Qt5::Core>)
            include(BundleUtilities)
            fixup_bundle("${CMAKE_INSTALL_PREFIX}/bin/$<TARGET_FILE_NAME:avdatabaseEditor>" "${CMAKE_INSTALL_PREFIX}/bin/$<TARGET_FILE_NAME:Qt5::QuickControls2>" "${lib_paths}")
        ]])

endif()

enable_testing()

add_executable(tst_editor "tst_editor.cpp" "tests.qrc")
target_link_libraries(tst_editor
        PRIVATE
            Qt5::QuickTest
            Qt5::Quick
            Qt5::Qml
            ProjectAdder

    )


add_dependencies(tst_editor avdatabaseEditor)
add_test(tst_editor tst_editor -input ${CMAKE_CURRENT_SOURCE_DIR})
