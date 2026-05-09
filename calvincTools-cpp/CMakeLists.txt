cmake_minimum_required(VERSION 3.16)
project(calvincToolsCpp VERSION 2.2.0 LANGUAGES CXX)

# Enable Qt
find_package(Qt6 COMPONENTS Core Sql Widgets REQUIRED)

# Compiler settings
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Strict warning flags
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Werror)
endif()

# Enable CTest
enable_testing()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/include/calvinc_tools/version_config.hpp.in
    ${CMAKE_CURRENT_BINARY_DIR}/generated/calvinc_tools/version_config.hpp
    @ONLY
)

# Core version library (Phase 0)
add_library(calvincToolsCore STATIC
    src/version.cpp
)

target_include_directories(calvincToolsCore
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
)

target_link_libraries(calvincToolsCore Qt6::Core)

# Math expression parser library (Phase 1)
add_library(calvincToolsMathExpr STATIC
    src/mathexpr/math_parser.cpp
    src/mathexpr/evaluate.cpp
)

target_include_directories(calvincToolsMathExpr
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
)

target_link_libraries(calvincToolsMathExpr Qt6::Core)

# Database layer library (Phase 1)
add_library(calvincToolsDatabase STATIC
    src/database/database_context.cpp
    src/database/models.cpp
    src/database/repository.cpp
)

target_include_directories(calvincToolsDatabase
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
)

target_link_libraries(calvincToolsDatabase Qt6::Core Qt6::Sql calvincToolsCore)

# Authentication layer library (Phase 1)
add_library(calvincToolsAuth STATIC
    src/auth/user.cpp
    src/auth/password_service.cpp
    src/auth/auth_context.cpp
    src/auth/authorization.cpp
)

target_include_directories(calvincToolsAuth
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
)

target_link_libraries(calvincToolsAuth Qt6::Core calvincToolsCore calvincToolsDatabase)

# Menu command layer library (Phase 1)
add_library(calvincToolsMenuCommand STATIC
    src/menucommand/command_types.cpp
    src/menucommand/menu_repository.cpp
)

target_include_directories(calvincToolsMenuCommand
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
)

target_link_libraries(calvincToolsMenuCommand Qt6::Core calvincToolsCore calvincToolsDatabase)

# Aggregate library with all Phase 1 components
add_library(calvincToolsCpp INTERFACE)

target_link_libraries(calvincToolsCpp INTERFACE
    calvincToolsCore
    calvincToolsMathExpr
    calvincToolsDatabase
    calvincToolsAuth
    calvincToolsMenuCommand
)


# Install rules
install(TARGETS 
    calvincToolsCpp
    calvincToolsCore
    calvincToolsMathExpr
    calvincToolsDatabase
    calvincToolsAuth
    calvincToolsMenuCommand
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/calvinc_tools
    DESTINATION include
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/generated/calvinc_tools/version_config.hpp
    DESTINATION include/calvinc_tools
)

# Add test subdirectory
add_subdirectory(tests)

