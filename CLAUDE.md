# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python wrapper and CLI for the LADOK3 REST API - Sweden's national student information system used by higher education institutions for managing student data, course registrations, and grade reporting.

## Build Commands

```bash
make install          # pip install -e . (editable development install)
make compile          # Generate .py/.tex from .nw literate source files
make test             # Run pytest test suite
make all              # Full build (compile + documentation)
make build            # Build distribution packages with poetry
poetry run pytest tests/ -v    # Run tests directly with verbose output
```

## Critical: Literate Programming Workflow

**This project uses noweb literate programming. Source files are `.nw` files that contain both documentation and code.**

### ⚠️ NEVER edit `.py` or `.tex` files directly - they are auto-generated

When making changes:
1. Edit the `.nw` files in `src/ladok3/`
2. Run `make compile` to regenerate Python files
3. Test with `make test`
4. Only commit the `.nw` files

### .nw File Structure
- Documentation chunks: Begin with `@` followed by LaTeX text
- Code chunks: `<<chunk name>>=` ... defines a chunk, `<<chunk name>>` references it
- Quote code in docs using `[[code]]` notation
- Chunks are ordered pedagogically (for human readers), not by compiler requirements

### Noweb Commands
```bash
notangle -Rchunkname file.nw > output.py    # Extract code chunk
noweave -latex -x -index file.nw > output.tex  # Generate documentation
noroots file.nw                              # List all root chunks
```

## Architecture

### Core Classes (src/ladok3/)
- **LadokSession** (`ladok3.nw`): Central class for authenticated API access, handles SSO auth via weblogin
- **Student** (`student.nw`): Student data representation
- **CLI** (`cli.nw`): Command-line interface with argparse/argcomplete

### Exception Hierarchy (api.nw)
```
LadokError
├── LadokServerError      # Server-side errors
├── LadokValidationError  # Data validation errors
├── LadokAPIError         # HTTP/API errors
└── LadokNotFoundError    # Resource not found
```

### CLI Commands
- `ladok login` - Authenticate and cache credentials
- `ladok report` - Report grades to LADOK
- `ladok course` - Extract course statistics

## Common Patterns

```python
# Using CLI credentials (recommended)
import ladok3
import ladok3.cli
ls = ladok3.LadokSession(*ladok3.cli.load_credentials())

# Reusing cached session
_, credentials = ladok3.cli.load_credentials()
ls = ladok3.cli.restore_ladok_session(credentials)
# ... work with session ...
ladok3.cli.store_ladok_session(ls, credentials)

# Grade reporting
student = ls.get_student("123456-1234")
course_participation = student.courses(code="AB1234")[0]
component_result = course_participation.results(component="LAB1")[0]
component_result.set_grade("P", "2021-03-15")
component_result.finalize()
```

## Testing

Tests require authentication credentials via environment variables:
- `LADOK_INST`, `LADOK_USER`, `LADOK_PASS`
- `KTH_LOGIN`, `KTH_PASSWD`

## Swedish Education Domain

- **Personnummer**: Personal ID format YYYYMMDD-XXXX
- **Course codes**: Format like "AB1234"
- **Components**: LAB1 (lab), TEN1 (exam), PRO1 (project)
- **Grades**: P/F (pass/fail) or A-F letter grades

## Development Setup

```bash
git clone --recurse-submodules https://github.com/dbosk/ladok3.git
cd ladok3
make install
```

Requires: Python 3.8+, Poetry, NOWEB (for literate programming compilation)
