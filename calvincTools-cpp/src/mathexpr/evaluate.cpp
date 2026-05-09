#include "calvinc_tools/mathexpr/evaluate.hpp"
#include "calvinc_tools/mathexpr/parser.hpp"
#include <cmath>

namespace calvinc::tools::mathexpr {

double evaluate(const std::string& expression, const std::map<std::string, double>& in_vars) {
    MathParser parser(expression, in_vars);
    double value = parser.getValue();
    
    // Return an integer type if the answer is an integer
    if (static_cast<int>(value) == value) {
        return static_cast<int>(value);
    }
    
    // If C++ made some silly precision error like x.99999999999996, just return x+1 as an integer
    const double epsilon = 0.0000000001;
    if (static_cast<int>(value + epsilon) != static_cast<int>(value)) {
        return static_cast<int>(value + epsilon);
    }
    if (static_cast<int>(value - epsilon) != static_cast<int>(value)) {
        return static_cast<int>(value);
    }
    
    return value;
}

}  // namespace calvinc::tools::mathexpr
