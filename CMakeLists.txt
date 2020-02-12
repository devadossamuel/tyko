cmake_minimum_required(VERSION 3.14)
project(tyko)
find_package(Python3 COMPONENTS Interpreter)
find_package(Qt5
    COMPONENTS
        Core
        Quick
        QuickControls2
        Widgets
    OPTIONAL_COMPONENTS
        QuickTest
        )
if (Qt5_FOUND)
    option(${PROJECT_NAME}_QT_CLIENT "Qt based desktop client" ON)
endif()

option(${PROJECT_NAME}_SERVER "Python-Flask based server" ON)

if(${PROJECT_NAME}_QT_CLIENT)
    set(CMAKE_INCLUDE_CURRENT_DIR ON)
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTORCC ON)

    add_subdirectory(client)
endif()

if(${PROJECT_NAME}_SERVER)

    add_custom_target(server
            COMMAND
                ${Python3_EXECUTABLE} setup.py
                    build
                        --build-base ${PROJECT_BINARY_DIR}/server
            WORKING_DIRECTORY
                ${PROJECT_SOURCE_DIR}
    )

endif()

include(CPackConfig.cmake)
include(CPack)
