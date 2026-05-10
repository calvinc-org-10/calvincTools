#include "calvinc_tools/menucommand/command_types.hpp"

namespace calvinc::tools::menucommand {

const std::map<int, QString> CommandRegistry::commandMap_ = {
    {0, ""},
    {1, "LoadMenu"},
    {11, "FormBrowse"},
    {15, "OpenTable"},
    {21, "RunCode"},
    {31, "RunSQLStatement"},
    {36, "LoadExtWebPage"},
    {51, "ChangePW"},
    {91, "EditMenu"},
    {92, "EditParameters"},
    {93, "EditGreetings"},
    {94, "EditUsers"},
    {110, "ShowHelp"},
    {111, "ShowRoutes_URLs"},
    {112, "ShowForms"},
    {200, "ExitApplication"},
};

const std::map<QString, int> CommandRegistry::nameMap_ = {
    {"", 0},
    {"LoadMenu", 1},
    {"FormBrowse", 11},
    {"OpenTable", 15},
    {"RunCode", 21},
    {"RunSQLStatement", 31},
    {"LoadExtWebPage", 36},
    {"ChangePW", 51},
    {"EditMenu", 91},
    {"EditParameters", 92},
    {"EditGreetings", 93},
    {"EditUsers", 94},
    {"ShowHelp", 110},
    {"ShowRoutes_URLs", 111},
    {"ShowForms", 112},
    {"ExitApplication", 200},
};

CommandType intToCommandType(int value) {
    switch (value) {
    case 0: return CommandType::NullCommand;
    case 1: return CommandType::LoadMenu;
    case 11: return CommandType::FormBrowse;
    case 15: return CommandType::OpenTable;
    case 21: return CommandType::RunCode;
    case 31: return CommandType::RunSQLStatement;
    case 36: return CommandType::LoadExtWebPage;
    case 51: return CommandType::ChangePW;
    case 91: return CommandType::EditMenu;
    case 92: return CommandType::EditParameters;
    case 93: return CommandType::EditGreetings;
    case 94: return CommandType::EditUsers;
    case 110: return CommandType::ShowHelp;
    case 111: return CommandType::ShowRoutes_URLs;
    case 112: return CommandType::ShowForms;
    case 200: return CommandType::ExitApplication;
    default: return CommandType::NullCommand;
    }
}

QString getCommandName(CommandType cmd) {
    return getCommandName(static_cast<int>(cmd));
}

QString getCommandName(int cmdInt) {
    const auto& commandMap = CommandRegistry::getCommandMap();
    auto it = commandMap.find(cmdInt);
    if (it != commandMap.end()) {
        return it->second;
    }
    return "";
}

CommandType getCommandType(const QString& name) {
    const auto& commandMap = CommandRegistry::getCommandMap();
    for (const auto& [cmdInt, cmdName] : commandMap) {
        if (cmdName == name) {
            return intToCommandType(cmdInt);
        }
    }
    return CommandType::NullCommand;
}

const std::map<int, QString>& CommandRegistry::getCommandMap() {
    return commandMap_;
}

bool CommandRegistry::hasCommand(CommandType cmd) {
    return hasCommand(static_cast<int>(cmd));
}

bool CommandRegistry::hasCommand(int cmdInt) {
    return commandMap_.find(cmdInt) != commandMap_.end();
}

bool CommandRegistry::hasCommand(const QString& name) {
    return nameMap_.find(name) != nameMap_.end();
}

}  // namespace calvinc::tools::menucommand
