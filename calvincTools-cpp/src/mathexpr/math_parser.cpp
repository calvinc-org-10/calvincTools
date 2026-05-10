#define _USE_MATH_DEFINES

#include "calvinc_tools/mathexpr/parser.hpp"
#include <cmath>
#include <cctype>
#include <sstream>
#include <iomanip>
#include <functional>
#include <algorithm>
#include <vector>

namespace calvinc::tools::mathexpr {

// Constants
static const std::map<std::string, double> CONSTANTS = {
    {"pi", M_PI},
    {"e", M_E},
    {"phi", (1.0 + std::sqrt(5.0)) / 2.0},
};

// Math functions that accept variable arguments
using MathFunc = std::function<double(const std::vector<double>&)>;
static const std::map<std::string, MathFunc> FUNCTIONS = {
    {"abs", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("abs() requires exactly 1 argument");
        return std::abs(args[0]);
    }},
    {"acos", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("acos() requires exactly 1 argument");
        return std::acos(args[0]);
    }},
    {"asin", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("asin() requires exactly 1 argument");
        return std::asin(args[0]);
    }},
    {"atan", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("atan() requires exactly 1 argument");
        return std::atan(args[0]);
    }},
    {"atan2", [](const std::vector<double>& args) {
        if (args.size() != 2) throw ParseException("atan2() requires exactly 2 arguments");
        return std::atan2(args[0], args[1]);
    }},
    {"ceil", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("ceil() requires exactly 1 argument");
        return std::ceil(args[0]);
    }},
    {"cos", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("cos() requires exactly 1 argument");
        return std::cos(args[0]);
    }},
    {"cosh", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("cosh() requires exactly 1 argument");
        return std::cosh(args[0]);
    }},
    {"degrees", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("degrees() requires exactly 1 argument");
        return args[0] * 180.0 / CONSTANTS.at("pi");
    }},
    {"exp", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("exp() requires exactly 1 argument");
        return std::exp(args[0]);
    }},
    {"fabs", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("fabs() requires exactly 1 argument");
        return std::fabs(args[0]);
    }},
    {"floor", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("floor() requires exactly 1 argument");
        return std::floor(args[0]);
    }},
    {"fmod", [](const std::vector<double>& args) {
        if (args.size() != 2) throw ParseException("fmod() requires exactly 2 arguments");
        return std::fmod(args[0], args[1]);
    }},
    {"frexp", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("frexp() requires exactly 1 argument");
        int exp = 0;
        return std::frexp(args[0], &exp);
    }},
    {"hypot", [](const std::vector<double>& args) {
        if (args.size() != 2) throw ParseException("hypot() requires exactly 2 arguments");
        return std::hypot(args[0], args[1]);
    }},
    {"ldexp", [](const std::vector<double>& args) {
        if (args.size() != 2) throw ParseException("ldexp() requires exactly 2 arguments");
        return std::ldexp(args[0], static_cast<int>(args[1]));
    }},
    {"log", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("log() requires exactly 1 argument");
        return std::log(args[0]);
    }},
    {"log10", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("log10() requires exactly 1 argument");
        return std::log10(args[0]);
    }},
    {"modf", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("modf() requires exactly 1 argument");
        double intpart;
        return std::modf(args[0], &intpart);
    }},
    {"pow", [](const std::vector<double>& args) {
        if (args.size() != 2) throw ParseException("pow() requires exactly 2 arguments");
        return std::pow(args[0], args[1]);
    }},
    {"radians", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("radians() requires exactly 1 argument");
        return args[0] * CONSTANTS.at("pi") / 180.0;
    }},
    {"sin", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("sin() requires exactly 1 argument");
        return std::sin(args[0]);
    }},
    {"sinh", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("sinh() requires exactly 1 argument");
        return std::sinh(args[0]);
    }},
    {"sqrt", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("sqrt() requires exactly 1 argument");
        return std::sqrt(args[0]);
    }},
    {"tan", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("tan() requires exactly 1 argument");
        return std::tan(args[0]);
    }},
    {"tanh", [](const std::vector<double>& args) {
        if (args.size() != 1) throw ParseException("tanh() requires exactly 1 argument");
        return std::tanh(args[0]);
    }},
};

MathParser::MathParser(const std::string& expression, const std::map<std::string, double>& in_vars)
    : string_(expression), index_(0), in_vars_(in_vars) {
    // Check that no constant names are being redefined
    for (const auto& constant : CONSTANTS) {
        if (in_vars_.find(constant.first) != in_vars_.end()) {
            throw NameException("Cannot redefine the value of " + constant.first);
        }
    }
}

double MathParser::getValue() {
    double value = parseExpression();
    skipWhitespace();
    
    if (hasNext()) {
        std::string msg = "Unexpected character found: '";
        msg += peek();
        msg += "' at index " + std::to_string(index_);
        throw SyntaxException(msg);
    }
    
    return value;
}

char MathParser::peek() const {
    if (index_ < string_.length()) {
        return string_[index_];
    }
    return '\0';
}

bool MathParser::hasNext() const {
    return index_ < string_.length();
}

bool MathParser::isNext(const std::string& value) const {
    return string_.substr(index_) == value.substr(0, string_.length() - index_);
}

bool MathParser::popIfNext(const std::string& value) {
    if (string_.substr(index_).find(value) == 0) {
        index_ += value.length();
        return true;
    }
    return false;
}

void MathParser::popExpected(const std::string& value) {
    if (!popIfNext(value)) {
        throw SyntaxException("Expected '" + value + "' at index " + std::to_string(index_));
    }
}

void MathParser::skipWhitespace() {
    while (hasNext()) {
        char c = peek();
        if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
            index_++;
        } else {
            break;
        }
    }
}

double MathParser::parseExpression() {
    return parseAddition();
}

double MathParser::parseAddition() {
    std::vector<double> values;
    values.push_back(parseMultiplication());
    
    while (true) {
        skipWhitespace();
        char c = peek();
        
        if (c == '+') {
            index_++;
            values.push_back(parseMultiplication());
        } else if (c == '-') {
            index_++;
            values.push_back(-1.0 * parseMultiplication());
        } else {
            break;
        }
    }
    
    double sum = 0.0;
    for (double v : values) {
        sum += v;
    }
    return sum;
}

double MathParser::parseMultiplication() {
    std::vector<double> values;
    values.push_back(parseParenthesis());
    
    while (true) {
        skipWhitespace();
        char c = peek();
        
        if (c == '*') {
            index_++;
            values.push_back(parseParenthesis());
        } else if (c == '/') {
            size_t div_index = index_;
            index_++;
            double denominator = parseParenthesis();
            
            if (denominator == 0.0) {
                throw ZeroDivisionException(
                    "Division by 0 kills baby whales (occurred at index " + std::to_string(div_index) + ")"
                );
            }
            values.push_back(1.0 / denominator);
        } else {
            break;
        }
    }
    
    double product = 1.0;
    for (double v : values) {
        product *= v;
    }
    return product;
}

double MathParser::parseParenthesis() {
    skipWhitespace();
    char c = peek();
    
    if (c == '(') {
        index_++;
        double value = parseExpression();
        skipWhitespace();
        
        if (peek() != ')') {
            throw SyntaxException("No closing parenthesis found at character " + std::to_string(index_));
        }
        index_++;
        return value;
    } else {
        return parseNegative();
    }
}

std::vector<double> MathParser::parseArguments() {
    std::vector<double> args;
    skipWhitespace();
    popExpected("(");
    
    while (!popIfNext(")")) {
        skipWhitespace();
        if (!args.empty()) {
            popExpected(",");
            skipWhitespace();
        }
        args.push_back(parseExpression());
        skipWhitespace();
    }
    
    return args;
}

double MathParser::parseNegative() {
    skipWhitespace();
    char c = peek();
    
    if (c == '-') {
        index_++;
        return -1.0 * parseParenthesis();
    } else {
        return parseValue();
    }
}

double MathParser::parseValue() {
    skipWhitespace();
    char c = peek();
    
    if (c >= '0' && c <= '9') {
        return parseNumber();
    } else if (c == '.') {
        return parseNumber();
    } else {
        return parseVariable();
    }
}

double MathParser::parseVariable() {
    skipWhitespace();
    std::string var;
    
    while (hasNext()) {
        char c = peek();
        
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || 
            (c >= '0' && c <= '9') || c == '_') {
            var += c;
            index_++;
        } else {
            break;
        }
    }
    
    // Convert to lowercase for lookup
    std::string var_lower = var;
    for (auto& ch : var_lower) {
        ch = std::tolower(ch);
    }
    
    // Check for functions
    auto func_it = FUNCTIONS.find(var_lower);
    if (func_it != FUNCTIONS.end()) {
        auto args = parseArguments();
        return func_it->second(args);
    }
    
    // Check for constants
    auto const_it = CONSTANTS.find(var_lower);
    if (const_it != CONSTANTS.end()) {
        return const_it->second;
    }
    
    // Check for variables
    auto var_it = in_vars_.find(var);
    if (var_it != in_vars_.end()) {
        return var_it->second;
    }
    
    throw NameException("Unrecognized variable: '" + var + "'");
}

double MathParser::parseNumber() {
    skipWhitespace();
    std::string str_value;
    bool decimal_found = false;
    
    while (hasNext()) {
        char c = peek();
        
        if (c == '.') {
            if (decimal_found) {
                throw SyntaxException(
                    "Found an extra period in a number at character " + std::to_string(index_) + 
                    ". Are you European?"
                );
            }
            decimal_found = true;
            str_value += '.';
        } else if (c >= '0' && c <= '9') {
            str_value += c;
        } else {
            break;
        }
        index_++;
    }
    
    if (str_value.empty()) {
        if (!hasNext()) {
            throw SyntaxException("Unexpected end found");
        } else {
            throw SyntaxException(
                "I was expecting to find a number at character " + std::to_string(index_) +
                " but instead I found a '" + std::string(1, peek()) + "'. What's up with that?"
            );
        }
    }
    
    return std::stod(str_value);
}

}  // namespace calvinc::tools::mathexpr
