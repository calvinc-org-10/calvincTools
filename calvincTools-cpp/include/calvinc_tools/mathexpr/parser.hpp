#pragma once

#include <string>
#include <map>
#include <memory>
#include <vector>
#include <stdexcept>

namespace calvinc::tools::mathexpr {

/**
 * Exception thrown when parsing fails.
 */
class ParseException : public std::runtime_error {
public:
    explicit ParseException(const std::string& message) : std::runtime_error(message) {}
};

/**
 * Exception thrown on syntax errors.
 */
class SyntaxException : public ParseException {
public:
    explicit SyntaxException(const std::string& message) : ParseException("SyntaxError: " + message) {}
};

/**
 * Exception thrown when an unrecognized variable is encountered.
 */
class NameException : public ParseException {
public:
    explicit NameException(const std::string& message) : ParseException("NameError: " + message) {}
};

/**
 * Exception thrown on division by zero.
 */
class ZeroDivisionException : public ParseException {
public:
    explicit ZeroDivisionException(const std::string& message) : ParseException("ZeroDivisionError: " + message) {}
};

/**
 * MathParser: Recursive descent parser for mathematical expressions.
 * 
 * Supported operations:
 * - Addition and subtraction: +, -
 * - Multiplication and division: *, /
 * - Parentheses for grouping: ()
 * - Unary negation: -
 * 
 * Supported constants: pi, e, phi
 * 
 * Supported functions: abs, acos, asin, atan, atan2, ceil, cos, cosh, degrees,
 *                      exp, fabs, floor, fmod, frexp, hypot, ldexp, log, log10,
 *                      modf, pow, radians, sin, sinh, sqrt, tan, tanh
 */
class MathParser {
private:
    std::string string_;
    size_t index_;
    std::map<std::string, double> in_vars_;

    // Parsing helper methods
    void skipWhitespace();
    char peek() const;
    bool hasNext() const;
    bool isNext(const std::string& value) const;
    bool popIfNext(const std::string& value);
    void popExpected(const std::string& value);
    
    // Expression parsing (precedence levels)
    double parseExpression();
    double parseAddition();
    double parseMultiplication();
    double parseParenthesis();
    double parseNegative();
    double parseValue();
    double parseVariable();
    double parseNumber();
    
    // Function and constant lookup
    std::vector<double> parseArguments();

public:
    /**
     * Construct a parser for the given expression.
     * 
     * @param expression The mathematical expression to parse.
     * @param in_vars Optional map of variable names to values.
     * @throws NameException if a constant name is redefined in in_vars.
     */
    explicit MathParser(const std::string& expression, 
                       const std::map<std::string, double>& in_vars = {});
    
    /**
     * Parse and evaluate the expression.
     * 
     * @return The numerical result of evaluating the expression.
     * @throws SyntaxException on parsing errors.
     * @throws NameException if an undefined variable is encountered.
     * @throws ZeroDivisionException on division by zero.
     */
    double getValue();
};

}  // namespace calvinc::tools::mathexpr
