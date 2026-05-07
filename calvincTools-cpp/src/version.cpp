#include "calvinc_tools/version.hpp"
#include "calvinc_tools/version_config.hpp"

namespace calvinc::tools {

std::string version() {
    return CALVINC_TOOLS_VERSION;
}

std::string package_name() {
    return "calvincTools";
}

}  // namespace calvinc::tools
