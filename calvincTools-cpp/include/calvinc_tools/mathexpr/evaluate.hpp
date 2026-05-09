#pragma once

#include <string>
#include <map>

namespace calvinc::tools::mathexpr {

/**
 * Evaluate a mathematical expression string.
 * 
 * @param expression The mathematical expression to evaluate.
 * @param in_vars Optional map of variable names to values.
 * @return The result as a double value.
 * 
 * Examples:
 *   evaluate("2 + 3 * 4")  // returns 14
 *   evaluate("sin(pi/2)")  // returns 1
 *   evaluate("x + 5", {{"x", 10}})  // returns 15
 */
double evaluate(const std::string& expression, 
                const std::map<std::string, double>& in_vars = {});

}  // namespace calvinc::tools::mathexpr
