# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-22

### Added
- Initial release of Code Change Summarizer
- Multi-language support for Python, JavaScript, TypeScript, Java, Go, Rust, and more
- Multiple output formats: plain text, Markdown, and JSON
- Custom template support for personalized output formatting
- Configuration file support (.code-summarizer.json)
- Command-line interface with comprehensive options
- Git integration for automated workflows
- Intelligent code analysis and change detection
- Purpose inference based on code patterns
- Robust error handling for malformed diffs
- Comprehensive test suite with 132+ tests
- Support for:
  - Function and class detection
  - Import and dependency analysis
  - Structural change identification
  - Complexity scoring
  - Change impact assessment
  - Automated recommendations

### Features
- **Smart Analysis**: Detects functions, classes, imports, and structural changes
- **Language Detection**: Automatic programming language identification
- **Change Categorization**: Classifies changes as feature additions, bug fixes, refactoring, etc.
- **Template System**: Customizable output templates with variable substitution
- **Configuration**: JSON-based configuration with custom templates
- **CLI Integration**: Easy integration with git workflows and CI/CD pipelines
- **Error Recovery**: Graceful handling of malformed or incomplete diffs

### Technical Details
- Python 3.8+ support
- Comprehensive test coverage
- Cross-platform compatibility (Windows, macOS, Linux)
- Minimal dependencies
- Fast processing of large diffs
- Memory-efficient parsing

### Documentation
- Complete README with usage examples
- API documentation for all modules
- Integration examples for git hooks and CI/CD
- Configuration guide with template examples