#pragma once

#include <QString>
#include <map>
#include <string>

namespace calvinc::tools::menucommand {

/**
 * Command type enumeration for menu commands.
 * Maps command names to numeric IDs.
 */
enum class CommandType {
    NullCommand = 0,
    LoadMenu = 1,
    FormBrowse = 11,
    OpenTable = 15,
    RunCode = 21,
    RunSQLStatement = 31,
    LoadExtWebPage = 36,
    ChangePW = 51,
    EditMenu = 91,
    EditParameters = 92,
    EditGreetings = 93,
    EditUsers = 94,
    ShowHelp = 110,
    ShowRoutes_URLs = 111,
    ShowForms = 112,
    ExitApplication = 200,
};

/**
 * Convert CommandType enum to its numeric value.
 */
inline int commandTypeToInt(CommandType cmd) {
    return static_cast<int>(cmd);
}

/**
 * Convert numeric value to CommandType enum.
 * Returns NullCommand if the value is not recognized.
 */
CommandType intToCommandType(int value);

/**
 * Get the string name for a command type.
 */
QString getCommandName(CommandType cmd);
QString getCommandName(int cmdInt);

/**
 * Get the CommandType enum for a string name.
 * Returns NullCommand if not found.
 */
CommandType getCommandType(const QString& name);

/**
 * Map of all available commands.
 */
class CommandRegistry {
public:
    static const std::map<int, QString> commandMap_;
    static const std::map<QString, int> nameMap_;

    /**
     * Get all available commands as a map.
     */
    static const std::map<int, QString>& getCommandMap();
    
    /**
     * Check if a command exists.
     */
    static bool hasCommand(CommandType cmd);
    static bool hasCommand(int cmdInt);
    static bool hasCommand(const QString& name);
};

}  // namespace calvinc::tools::menucommand
