# calvincTools C++ implementation

This directory starts the C++ migration effort for `calvincTools`.

## Current scope

- CMake project scaffold
- Core version metadata module (`version.hpp` / `version.cpp`)
- CMake-generated version config (`version_config.hpp`)

## Planning baseline

- Migration traceability matrix: `docs/migration_traceability_matrix.md`
- Step 1 is complete when the matrix is the authoritative module-to-component plan for the rewrite.

## Building

```bash
cmake -S calvincTools-cpp -B /tmp/calvincTools-cpp-build
cmake --build /tmp/calvincTools-cpp-build
```

## Qt6 setup (Windows)

This project uses CMake `find_package(Qt6 COMPONENTS Core Sql Widgets REQUIRED)` in `CMakeLists.txt`.
If CMake cannot find Qt, set one of the following:

- `CMAKE_PREFIX_PATH` to your Qt kit root (recommended), for example:
	- "D:/AppDev/Qt6/6.11.0/mingw_64"
- `Qt6_DIR` directly to Qt's CMake package directory, for example:
	- "D:/AppDev/Qt6/6.11.0/mingw_64"

Use a Qt kit that matches your compiler toolchain:

- MSVC build -> `msvc2022_64`
- MinGW build -> `mingw_64`

If you use VS Code CMake Tools, configure:

```json
{
	"cmake.configureSettings": {
		"CMAKE_PREFIX_PATH": "D:/AppDev/Qt6/6.11.0/mingw_64"
	}
}
```

After changing Qt paths, clear CMake cache and reconfigure:

```bash
cmake -S calvincTools-cpp -B build/calvincTools-cpp -U *Qt6* -U CMAKE_PREFIX_PATH
cmake -S calvincTools-cpp -B build/calvincTools-cpp
```

If your app links but fails at runtime, add Qt binaries to `PATH`:

- `C:/Qt/6.7.2/msvc2022_64/bin`
