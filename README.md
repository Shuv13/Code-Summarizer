# Code Change Summarizer

A Python tool that analyzes git diffs and generates intelligent, human-readable summaries of code changes. Perfect for code reviews, change tracking, and understanding what modifications were made to your codebase.

## Features

- **Multi-language support**: Detects and analyzes Python, JavaScript, TypeScript, Java, Go, Rust, and many other programming languages
- **Intelligent analysis**: Identifies structural changes like function additions, class modifications, and import changes
- **Purpose inference**: Attempts to understand why changes were made based on code patterns
- **Multiple output formats**: Plain text, Markdown, and JSON output
- **Custom templates**: Support for custom output formatting
- **Robust error handling**: Gracefully handles malformed diffs and edge cases
- **Command-line interface**: Easy integration into development workflows

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/Shuv13/Code-Summarizer.git
cd Code-Summarizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Using pip (when published)

```bash
pip install code-change-summarizer
```

## Usage

### Basic Usage

Analyze changes from git diff:

```bash
# From git diff output
git diff | code-summarizer

# From a diff file
code-summarizer --input changes.diff

# Direct diff input
code-summarizer --diff "$(git diff)"
```

### Output Formats

Choose your preferred output format:

```bash
# Plain text (default)
git diff | code-summarizer --format plain

# Markdown
git diff | code-summarizer --format markdown

# JSON for programmatic use
git diff | code-summarizer --format json
```

### Custom Templates

Use custom templates for personalized output:

```bash
git diff | code-summarizer --template "Changed {total_files} files: +{lines_added}/-{lines_removed} lines"
```

Available template variables:
- `{overview}` - Overall summary
- `{total_files}` - Number of files changed
- `{files_added}` - Number of files added
- `{files_modified}` - Number of files modified
- `{files_deleted}` - Number of files deleted
- `{lines_added}` - Total lines added
- `{lines_removed}` - Total lines removed
- `{key_changes}` - List of key changes
- `{recommendations}` - List of recommendations
- `{file_summaries}` - Detailed file summaries

### Save Output

Save analysis to a file:

```bash
git diff | code-summarizer --output summary.md --format markdown
```

### Quiet Mode

Suppress progress messages:

```bash
git diff | code-summarizer --quiet
```

## Examples

### Example 1: Simple Python Change

Input diff:
```diff
diff --git a/calculator.py b/calculator.py
index 1234567..abcdefg 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,3 +1,4 @@
 def add(x, y):
+    print(f"Adding {x} + {y}")
     return x + y
```

Output:
```
CODE CHANGE SUMMARY
==================================================

OVERVIEW:
1 file changed. 1 modified. (+1 lines). Primary focus: Debugging or logging enhancement.

STATISTICS:
  Total files changed: 1
  Files modified: 1
  Lines added: +1
  Lines removed: -0

FILE DETAILS:
------------------------------
File: calculator.py
Summary: Modified 'calculator.py' - (+1 lines) - Purpose: Debugging or logging enhancement
```

### Example 2: Multiple Files with JSON Output

```bash
git diff | code-summarizer --format json
```

```json
{
  "overview": "3 files changed (1 added, 2 modified). (+25, -5 lines). Primary focus: Feature addition.",
  "statistics": {
    "total_files": 3,
    "files_added": 1,
    "files_modified": 2,
    "files_deleted": 0,
    "total_lines_added": 25,
    "total_lines_removed": 5
  },
  "file_summaries": [
    {
      "filename": "new_feature.py",
      "summary": "Added new file 'new_feature.py' - (+20 lines) - Purpose: Feature addition",
      "key_changes": ["Added function 'new_feature'"]
    }
  ],
  "key_changes": [
    "New file: new_feature.py",
    "Modified function in existing.py"
  ],
  "recommendations": [
    "Consider adding tests for the new functionality"
  ]
}
```

## Supported Languages

The tool provides intelligent analysis for:

- **Python** (.py) - Functions, classes, imports, decorators
- **JavaScript** (.js, .jsx) - Functions, classes, imports, variables
- **TypeScript** (.ts, .tsx) - Functions, classes, interfaces, types
- **Java** (.java) - Classes, methods, imports
- **Go** (.go) - Functions, structs, interfaces
- **Rust** (.rs) - Functions, structs, enums, traits
- **C/C++** (.c, .cpp, .h, .hpp) - Basic structure detection
- **And many more...**

For unsupported languages, the tool still provides basic change statistics and diff analysis.

## Integration Examples

### Git Hooks

Add to your git hooks for automatic change summaries:

```bash
#!/bin/bash
# .git/hooks/pre-commit
git diff --cached | code-summarizer --quiet --format markdown > CHANGES.md
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Generate Change Summary
  run: |
    git diff HEAD~1 | code-summarizer --format markdown > change-summary.md
    cat change-summary.md >> $GITHUB_STEP_SUMMARY
```

### Code Review Automation

```bash
# Generate summary for pull request
git diff main...feature-branch | code-summarizer --format markdown
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_parser.py -v
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=code_summarizer
```

### Project Structure

```
code_summarizer/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── parser.py           # Git diff parsing
├── analyzer.py         # Code analysis and language detection
├── generator.py        # Summary generation
├── formatter.py        # Output formatting
└── models.py           # Data models

tests/
├── test_parser.py      # Parser tests
├── test_analyzer.py    # Analyzer tests
├── test_generator.py   # Generator tests
├── test_formatter.py   # Formatter tests
├── test_cli.py         # CLI tests
├── test_error_handling.py  # Error handling tests
└── test_integration.py # End-to-end integration tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.