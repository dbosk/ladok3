# GitHub Copilot Instructions for ladok3

## Project Overview

This is a Python package that provides a wrapper for the LADOK3 REST API. LADOK3 is the Swedish national student information system used by higher education institutions for managing student data, course registrations, and grade reporting.

## Project Structure

- **Language**: Python 3.8+
- **Package Manager**: Poetry
- **Documentation Style**: Literate Programming with noweb (.nw files)
- **Architecture**: CLI tool + Python library
- **Testing**: pytest

## Key Components

### Source Files
- `src/ladok3/*.nw` - Literate programming source files (noweb format)
- **Generated Python (.py) and LaTeX (.tex) files are built from these .nw files**
- **⚠️ IMPORTANT: Never commit .py or .tex files as they are auto-generated**
- `examples/` - Example scripts showing usage patterns

### Main Classes
- `LadokSession` - Main session class for authenticated API access
- `Student` - Student data representation
- `Course` - Course and course instance management
- Various data models for LADOK3 entities

### CLI Interface
- Entry point: `ladok` command
- Main operations: login, report grades, query data
- Supports batch operations via CSV input

## Coding Guidelines

### Authentication & Sessions
- Always use `LadokSession` for API access
- Support both test and production environments
- Handle KTH/Swedish university SAML authentication
- Cache sessions for performance

### Error Handling
- Handle network timeouts gracefully
- Provide meaningful error messages for API failures
- Support retry mechanisms for transient failures

### Data Processing
- Work with Swedish personal numbers (personnummer)
- Handle course codes and instances properly
- Support bulk operations efficiently
- Parse and validate LADOK3 API responses

### CLI Design
- Provide tab completion support
- Support verbose/quiet modes
- Accept input from pipes (CSV data)
- Follow Unix conventions for tool design

### Documentation
- This project uses literate programming (noweb)
- Source code is in .nw files with embedded documentation
- Examples should be practical and educational
- Document Swedish education system specifics

### File Management
- **Source files**: Only `.nw` files should be edited and committed
- **Generated files**: `.py` and `.tex` files are auto-generated from `.nw` files
- **Never commit generated files**: They are ignored by `.gitignore` for good reason
- **Build process**: Use `make` commands to generate Python/LaTeX from noweb sources

## Literate Programming with Noweb

### ⚠️ CRITICAL: When Working with .nw Files

**ALWAYS follow literate programming principles when creating or editing .nw files!**

.nw files are NOT regular source code files - they are literate programs that combine documentation and code in a pedagogical narrative. Literate quality is AS IMPORTANT as code correctness.

### Planning Changes to .nw Files

When modifying a .nw file, follow this process:

1. **Read the existing .nw file** to understand the current structure and narrative
2. **Plan changes with literate programming in mind:**
   - What is the "why" behind this change? (Explain in documentation)
   - How does this fit into the existing narrative?
   - Should I use contrast to explain the change? (old vs new approach)
   - What new chunks are needed? What are their meaningful names?
   - Where in the pedagogical order should this be explained?
3. **Design the documentation BEFORE writing code:**
   - Write prose explaining the problem and solution
   - Use subsections to structure complex explanations
   - Provide examples showing the new behavior
   - Explain design decisions and trade-offs
4. **Decompose code into well-named chunks:**
   - Each chunk = one coherent concept
   - Names describe purpose (like pseudocode), not syntax
   - Use the web structure effectively
5. **Write the code chunks referenced in documentation**
6. **Regenerate and test**

**Key principle:** If you find yourself writing code comments to explain logic, that explanation belongs in the TeX/documentation chunks instead!

### Core Literate Programming Philosophy

From Donald Knuth:

1. **Explain to human beings what we want a computer to do** - Focus on human readers, not compilers
2. **Introduce concepts in psychological order** - Write for human understanding, not computer requirements

Use variation theory: contrast different approaches, start with the whole, examine parts, then synthesize.

### Noweb File Format

**Documentation Chunks:**
- Begin with `@` followed by space or newline
- Contain LaTeX text explaining the code
- Have no names
- Are copied verbatim by noweave

**Code Chunks:**
- Begin with `<<chunk name>>=` (must start in column 1)
- End when another chunk begins or at EOF
- Can reference other chunks using `<<chunk name>>`
- Multiple chunks with same name are concatenated

**Syntax Rules:**
- Quote code in documentation using `[[code]]` (escapes special characters)
- Escape special sequences: `@<<` for literal `<<`, `@@` in column 1 for literal `@`
- Code chunks form a "web" structure

### Writing Quality Literate Programs

1. **Start with the human story** - Explain problem, approach, design (the whole)
2. **Introduce concepts in pedagogical order** - Not compiler order
3. **Use meaningful chunk names** - 2-5 word summary of purpose (like pseudocode)
4. **Decompose by concept, not syntax** - Break by logical thought units
5. **Explain the "why"** - Not just what (visible) but why this approach
6. **Keep chunks focused** - One coherent idea per chunk
7. **Use the web structure** - Define chunks out of order when pedagogically better
8. **Structured programming still applies** - Use helper functions, don't replace everything with chunks

### Noweb Commands

**Tangling (extract code):**
```bash
# Extract specific root chunk
notangle -Rchunkname file.nw > output.ext

# With line directives for debugging (doesn't work for Python)
notangle -L -Rchunkname file.nw > output.ext

# List all root chunks
noroots file.nw
```

**Weaving (create documentation):**
```bash
# Generate LaTeX
noweave -latex file.nw > output.tex

# With cross-references and index
noweave -latex -x -index -autodefs python file.nw > output.tex

# No wrapper (for inclusion)
noweave -n -latex file.nw > output.tex
```

### Reviewing Literate Quality

When reviewing .nw files, evaluate:

1. **Narrative flow**: Coherent story? Pedagogical order (not compiler order)?
2. **Variation theory**: Contrasts to highlight concepts? Whole→parts→synthesis?
3. **Chunk quality**:
   - Meaningful names (purpose, not syntax)?
   - Appropriate size (single concepts)?
   - Effective web structure?
4. **Explanation quality**:
   - Explains "why" not just "what"?
   - Design decisions and trade-offs explained?
   - Technical context for non-obvious choices?
5. **Proper syntax**:
   - Code references use `[[code]]` notation?
   - Chunk definitions properly formatted?
   - No unused chunks (check with `noroots`)?

### Python-Specific Notes

- No special flags needed for Python tangling
- Line directives (`-L`) don't work with Python
- Consider formatting output: `notangle -Rfile.py file.nw | black - > file.py`
- Remember to regenerate with `make` after changes

### Integration with Development

- **Version control**: Only commit .nw files, regenerate code with make
- **Build process**: CI/CD should tangle before build/test
- **Code review**: Review both code AND explanation quality in .nw files
- **Documentation**: Weave to PDF for readable docs

## Common Patterns

### API Calls
```python
# Standard session usage
ls = ladok3.LadokSession("University Name", credentials)
student = ls.get_student("123456-1234")
```

### Grade Reporting
```python
# Report a grade for a student
component_result = course_participation.results(component="LAB1")[0]
component_result.set_grade("P", "2021-03-15")
component_result.finalize()
```

### CLI Integration
```python
# Use CLI utilities for credential management
ls = ladok3.LadokSession(*ladok3.cli.load_credentials())
```

## Domain Knowledge

### Swedish Education Context
- **Personnummer**: Swedish personal identity numbers (YYYYMMDD-XXXX)
- **Course codes**: Format like "AB1234" for course identification
- **Grading**: Pass/Fail (P/F) and letter grades (A-F)
- **Components**: Courses have components like LAB1, TEN1 (lab work, written exam)

### LADOK3 API
- REST API with JSON responses
- Requires authenticated sessions
- Supports both test and production environments
- Handles course instances, student participations, and grade reporting

## Preferred Libraries
- `requests` for HTTP/API calls
- `weblogin` for authentication handling
- `argcomplete` for CLI tab completion
- `cachetools` for session/data caching
- `cryptography` for secure operations

## Testing Considerations
- Mock LADOK3 API calls for unit tests
- Use test environment for integration tests
- Test with sample Swedish data formats
- Validate error handling for network issues

## When suggesting code:
1. Follow the existing authentication patterns
2. Handle Swedish personal numbers correctly
3. Provide proper error handling for network calls
4. Include docstrings that explain LADOK3/Swedish education context
5. Consider both CLI and library usage patterns
6. Respect the literate programming style when editing .nw files
7. **NEVER suggest committing .py or .tex files - they are auto-generated**