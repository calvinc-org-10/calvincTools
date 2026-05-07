# calvincTools C++ implementation

This directory starts the C++ migration effort for `calvincTools`.

## Current scope

- CMake project scaffold
- Core version metadata module (`version.hpp` / `version.cpp`)
- CMake-generated version config (`version_config.hpp`)

## Building

```bash
cmake -S calvincTools-cpp -B /tmp/calvincTools-cpp-build
cmake --build /tmp/calvincTools-cpp-build
```
