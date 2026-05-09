#include <iostream>
#include <cassert>
#include "calvinc_tools/menucommand/command_types.hpp"

using namespace calvinc::tools::menucommand;

int main() {
    std::cout << "Running Menu Command Tests\n";
    
    // Test command type enum conversion
    assert(intToCommandType(1) == CommandType::LoadMenu);
    assert(intToCommandType(11) == CommandType::FormBrowse);
    assert(intToCommandType(200) == CommandType::ExitApplication);
    
    // Test command name lookup
    assert(getCommandName(CommandType::LoadMenu) == "LoadMenu");
    assert(getCommandName(11) == "FormBrowse");
    assert(getCommandName(CommandType::ExitApplication) == "ExitApplication");
    
    // Test command type lookup
    assert(getCommandType("LoadMenu") == CommandType::LoadMenu);
    assert(getCommandType("FormBrowse") == CommandType::FormBrowse);
    assert(getCommandType("ExitApplication") == CommandType::ExitApplication);
    
    // Test command registry
    assert(CommandRegistry::hasCommand(CommandType::LoadMenu));
    assert(CommandRegistry::hasCommand(11));
    assert(CommandRegistry::hasCommand("FormBrowse"));
    
    // Test that invalid commands don't exist
    assert(!CommandRegistry::hasCommand(9999));
    assert(!CommandRegistry::hasCommand("InvalidCommand"));
    
    // Test command map
    const auto& cmdMap = CommandRegistry::getCommandMap();
    assert(cmdMap.find(1) != cmdMap.end());
    assert(cmdMap.at(1) == "LoadMenu");
    
    std::cout << "All menu command tests passed!\n";
    return 0;
}
