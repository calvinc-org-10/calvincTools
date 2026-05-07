cmake_minimum_required(VERSION 3.16)
project(calvincToolsCpp VERSION 2.2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/include/calvinc_tools/version_config.hpp.in
    ${CMAKE_CURRENT_BINARY_DIR}/generated/calvinc_tools/version_config.hpp
    @ONLY
)

add_library(calvincToolsCpp STATIC
    src/version.cpp
)

target_include_directories(calvincToolsCpp
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
)
