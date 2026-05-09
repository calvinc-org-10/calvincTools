#include <iostream>
#include <cassert>
#include "calvinc_tools/mathexpr/evaluate.hpp"

using namespace calvinc::tools::mathexpr;

int main() {
    std::cout << "Running Math Expression Parser Tests\n";
    
    // Test basic arithmetic
    assert(evaluate("2 + 3") == 5.0);
    assert(evaluate("10 - 3") == 7.0);
    assert(evaluate("2 * 3") == 6.0);
    assert(evaluate("10 / 2") == 5.0);
    
    // Test precedence
    assert(evaluate("2 + 3 * 4") == 14.0);
    assert(evaluate("(2 + 3) * 4") == 20.0);
    
    // Test unary negation
    assert(evaluate("-5") == -5.0);
    assert(evaluate("-(2 + 3)") == -5.0);
    
    // Test constants
    double pi = evaluate("pi");
    assert(pi > 3.14 && pi < 3.15);
    
    // Test functions
    double sqrt_result = evaluate("sqrt(4)");
    assert(sqrt_result == 2.0);
    
    // Test with variables
    std::map<std::string, double> vars = {{"x", 10.0}};
    assert(evaluate("x + 5", vars) == 15.0);
    
    std::cout << "All math expression tests passed!\n";
    return 0;
}
