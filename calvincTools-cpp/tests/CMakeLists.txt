enable_testing()

# Test executable for mathexpr module
add_executable(test_mathexpr
    test_mathexpr.cpp
)

target_link_libraries(test_mathexpr
    calvincToolsMathExpr
    Qt6::Core
)

add_test(NAME MathExprTests COMMAND test_mathexpr)

# Test executable for database module
add_executable(test_database
    test_database.cpp
)

target_link_libraries(test_database
    calvincToolsDatabase
    Qt6::Core
    Qt6::Sql
)

add_test(NAME DatabaseTests COMMAND test_database)

# Test executable for auth module
add_executable(test_auth
    test_auth.cpp
)

target_link_libraries(test_auth
    calvincToolsAuth
    calvincToolsDatabase
    Qt6::Core
)

add_test(NAME AuthTests COMMAND test_auth)

# Test executable for menucommand module
add_executable(test_menucommand
    test_menucommand.cpp
)

target_link_libraries(test_menucommand
    calvincToolsMenuCommand
    calvincToolsDatabase
    Qt6::Core
    Qt6::Sql
)

add_test(NAME MenuCommandTests COMMAND test_menucommand)
