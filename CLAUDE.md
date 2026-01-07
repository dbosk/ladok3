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

### Planning Changes to .nw Files

When modifying a .nw file, follow this process:

1. **Read the existing .nw file** to understand the current structure and narrative
2. **Plan changes with literate programming in mind:**
   - What is the "why" behind this change? (Explain in documentation)
   - How does this fit into the existing narrative?
   - Should I use contrast to explain the change? (old vs new approach)
   - What new chunks are needed? What are their meaningful names?
3. **Design the documentation BEFORE writing code:**
   - Write prose explaining the problem and solution
   - Use subsections to structure complex explanations
   - Explain design decisions and trade-offs
4. **Decompose code into well-named chunks:**
   - Each chunk = one coherent concept
   - Names describe purpose (like pseudocode), not syntax
5. **Write the code chunks referenced in documentation**
6. **Regenerate and test**

**Key principle:** If you find yourself writing code comments to explain logic, that explanation belongs in the TeX/documentation chunks instead!

### Core Literate Programming Philosophy

From Donald Knuth:

1. **Explain to human beings what we want a computer to do** - Focus on human readers, not compilers
2. **Introduce concepts in psychological order** - Write for human understanding, not computer requirements

Use variation theory: contrast different approaches, start with the whole, examine parts, then synthesize.

### .nw File Structure

**Documentation Chunks:**
- Begin with `@` followed by space or newline
- Contain LaTeX text explaining the code
- Are copied verbatim by noweave

**Code Chunks:**
- Begin with `<<chunk name>>=` (must start in column 1)
- End when another chunk begins or at EOF
- Can reference other chunks using `<<chunk name>>`
- Multiple chunks with same name are concatenated

**Syntax Rules:**
- Quote code in documentation using `[[code]]` notation
- Escape special sequences: `@<<` for literal `<<`, `@@` in column 1 for literal `@`
- Chunks are ordered pedagogically (for human readers), not by compiler requirements

### Writing Quality Literate Programs

1. **Start with the human story** - Explain problem, approach, design (the whole)
2. **Introduce concepts in pedagogical order** - Not compiler order
3. **Use meaningful chunk names** - 2-5 word summary of purpose (like pseudocode)
4. **Decompose by concept, not syntax** - Break by logical thought units
5. **Explain the "why"** - Not just what (visible) but why this approach
6. **Keep chunks focused** - One coherent idea per chunk
7. **Use the web structure** - Define chunks out of order when pedagogically better
8. **Structured programming still applies** - Use helper functions, don't replace everything with chunks

### Reviewing Literate Quality

When reviewing .nw files, evaluate:

1. **Narrative flow**: Coherent story? Pedagogical order (not compiler order)?
2. **Variation theory**: Contrasts to highlight concepts? Whole→parts→synthesis?
3. **Chunk quality**: Meaningful names? Appropriate size? Effective web structure?
4. **Explanation quality**: Explains "why" not just "what"? Design decisions documented?
5. **Proper syntax**: Code references use `[[code]]`? Chunk definitions properly formatted?

### Noweb Commands

```bash
# Tangling (extract code)
notangle -Rchunkname file.nw > output.py    # Extract specific root chunk
noroots file.nw                              # List all root chunks

# Weaving (create documentation)
noweave -latex -x -index file.nw > output.tex  # Generate LaTeX with cross-refs
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
