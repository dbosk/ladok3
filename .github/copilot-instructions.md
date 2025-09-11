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