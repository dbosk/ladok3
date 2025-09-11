# GitHub Copilot Instructions for ladok3

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

This is a Python package that provides a wrapper for the LADOK3 REST API. LADOK3 is the Swedish national student information system used by higher education institutions for managing student data, course registrations, and grade reporting.

The project uses **literate programming** with noweb - Python source files are auto-generated from .nw files.

## Working Effectively

Bootstrap, build, and test the repository:

### Prerequisites Installation
- `sudo apt-get update && sudo apt-get install -y noweb` -- installs noweb tools (notangle, noweave)
- `pip3 install poetry` -- installs Poetry package manager (takes ~30 seconds)
- `pip3 install black argcomplete` -- installs required formatters and CLI tools

### Repository Setup
- `git submodule update --init --recursive` -- initializes required submodules (takes ~5 seconds)

### Build Process 
- ALWAYS run the bootstrapping steps first before building
- `export PATH="$HOME/.local/bin:$PATH"` -- ensures poetry is in PATH
- `make compile` -- compiles .nw files to .py files. Takes ~1.2 seconds. NEVER CANCEL.
- `poetry install --only main` -- installs runtime dependencies. Takes ~11 seconds. NEVER CANCEL.
- `poetry build` -- creates wheel and sdist packages. Takes ~0.6 seconds.

### Alternative Development Install
- `make install` -- attempts pip install -e . (may fail due to network issues in restricted environments)
- If make install fails, use `poetry install && poetry run ladok [command]` instead

### Testing
- `poetry install` -- installs ALL dependencies including dev/test deps (takes ~15 seconds)  
- `cd tests && make all` -- generates and runs tests. NEVER CANCEL. Set timeout to 5+ minutes.
- Tests require environment variables: `LADOK_INST`, `LADOK_USER`, `LADOK_PASS`, `KTH_LOGIN`, `KTH_PASSWD`
- Unit tests can run with mock values: `LADOK_INST="Test" LADOK_USER="test" LADOK_PASS="test" KTH_LOGIN="test" KTH_PASSWD="test"`
- 60 tests collected, unit tests pass with proper environment

### Running the CLI
- `poetry run ladok --help` -- shows main CLI help
- `poetry run ladok login --help` -- credential management
- `poetry run ladok course --help` -- course data export
- `poetry run ladok report --help` -- grade reporting
- CLI supports tab completion via argcomplete

## Validation

- Always build the complete project after making changes: run `make compile` then `poetry install`  
- ALWAYS test CLI functionality after changes: `poetry run ladok --help` and test subcommands
- Run unit tests that don't require LADOK credentials: `poetry run pytest tests/test_ladok3.py::test_filter_on_keys -v`
- The application is a CLI tool - test it by running commands, not by starting a server
- Test examples in `examples/` directory - they show real usage patterns

## Critical File Management Rules

- **NEVER edit .py files directly** - they are auto-generated from .nw files
- **NEVER commit .py or .tex files** - they are build artifacts
- **ONLY edit .nw files in src/ladok3/** for source changes
- Generated files have these extensions: `.py`, `.tex` from `.nw` sources
- Build process: .nw → (notangle) → .py + (black) → formatted Python code

## Project Structure

### Source Code Locations
- `src/ladok3/*.nw` -- Literate programming source files (EDIT THESE)
- `src/ladok3/Makefile` -- Build system for generating Python from noweb
- `examples/` -- Usage examples and real-world scripts
- `tests/` -- Test suite (generates test files from .nw sources)
- `doc/` -- Documentation source files
- `makefiles/` -- Build system utilities (git submodule)

### Key Generated Files (DO NOT EDIT)
- `src/ladok3/__init__.py` -- Main library (generated from ladok3.nw, api.nw, undoc.nw)
- `src/ladok3/cli.py` -- CLI implementation (generated from cli.nw)
- `src/ladok3/data.py` -- Data models (generated from data.nw) 
- `src/ladok3/report.py` -- Reporting functionality (generated from report.nw)
- `src/ladok3/student.py` -- Student operations (generated from student.nw)
- `src/ladok3/ladok.bash` -- Bash completion script

### Package Management
- `pyproject.toml` -- Poetry configuration and dependencies
- **Package Manager**: Poetry (required for dependency management)
- **Python Version**: 3.8+
- **Entry Point**: `ladok` command via `ladok3.cli:main`

## Domain Knowledge

### Swedish Education Context
- **Personnummer**: Swedish personal identity numbers (YYYYMMDD-XXXX)
- **Course codes**: Format like "AB1234" for course identification  
- **Grading**: Pass/Fail (P/F) and letter grades (A-F)
- **Components**: Courses have components like LAB1, TEN1 (lab work, written exam)

### LADOK3 API Integration
- REST API requiring authenticated sessions
- Supports both test and production environments  
- Handles course instances, student participations, grade reporting
- Uses weblogin for KTH/Swedish university SAML authentication

### Common Usage Patterns
```python
# Standard session usage
ls = ladok3.LadokSession("University Name", credentials)
student = ls.get_student("123456-1234")

# Grade reporting
component_result = course_participation.results(component="LAB1")[0]
component_result.set_grade("P", "2021-03-15") 
component_result.finalize()

# CLI integration
ls = ladok3.LadokSession(*ladok3.cli.load_credentials())
```

## Common Commands Reference

### Repository Root Files
```
.github/copilot-instructions.md  -- This file
.gitignore                       -- Excludes generated .py/.tex files
Makefile                        -- Top-level build orchestration  
pyproject.toml                  -- Poetry package configuration
README.md                       -- User documentation
CONTRIBUTING.md                 -- Developer setup guide
```

### Build Timing Expectations
- Source compilation: 1-2 seconds (`make compile`)
- Dependency install: 10-15 seconds (`poetry install --only main`) 
- Full install with dev deps: 15-30 seconds (`poetry install`)
- Package build: Under 1 second (`poetry build`)
- Test generation and run: 1-5 minutes (`cd tests && make all`)

## When Suggesting Code

1. **Edit .nw files only** - never suggest editing .py files directly
2. Follow existing authentication patterns using `LadokSession`
3. Handle Swedish personal numbers (personnummer) correctly
4. Include docstrings explaining LADOK3/Swedish education context
5. Support both CLI and library usage patterns
6. Test changes by rebuilding: `make compile && poetry install`
7. Validate CLI still works: `poetry run ladok --help`