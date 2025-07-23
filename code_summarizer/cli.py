"""
Command-line interface for the code change summarizer.
"""

import argparse
import sys
import os
from typing import Optional

from .parser import DiffParser
from .analyzer import CodeAnalyzer
from .generator import SummaryGenerator
from .formatter import OutputFormatter
from .config import config


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Analyze and summarize code changes from git diffs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze git diff from stdin
  git diff | python -m code_summarizer.cli
  
  # Analyze git diff from file
  python -m code_summarizer.cli --input diff.txt
  
  # Output in different formats
  git diff | python -m code_summarizer.cli --format markdown
  git diff | python -m code_summarizer.cli --format json
  
  # Use custom template
  git diff | python -m code_summarizer.cli --template "Summary: {overview}"
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='Input file containing git diff (default: read from stdin)'
    )
    input_group.add_argument(
        '--diff', '-d',
        type=str,
        help='Git diff text as string argument'
    )
    
    # Output options
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['plain', 'text', 'markdown', 'md', 'json'],
        default=config.get('output_format', 'plain'),
        help=f'Output format (default: {config.get("output_format", "plain")})'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file (default: write to stdout)'
    )
    
    parser.add_argument(
        '--template', '-t',
        type=str,
        help='Custom template for output formatting'
    )
    
    parser.add_argument(
        '--template-name',
        type=str,
        help='Use a named template from configuration'
    )
    
    # Configuration options
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create a sample configuration file'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available custom templates'
    )
    
    # Other options
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        default=config.get('quiet', False),
        help='Suppress informational messages'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Code Change Summarizer 0.1.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Handle configuration-only commands
        if args.create_config:
            config.create_sample_config()
            return 0
        
        if args.list_templates:
            templates = config.list_templates()
            if templates:
                print("Available templates:")
                for name, template in templates.items():
                    print(f"  {name}: {template}")
            else:
                print("No custom templates configured.")
            return 0
        
        # Load custom config if specified
        if args.config:
            if not os.path.exists(args.config):
                print(f"Error: Configuration file not found: {args.config}", file=sys.stderr)
                return 1
            # Note: In a full implementation, we'd reload config from the specified file
        
        # Validate configuration
        if not config.validate_config():
            print("Warning: Configuration validation failed. Using defaults.", file=sys.stderr)
        
        # Get input diff text
        diff_text = get_diff_input(args)
        
        if not diff_text or not diff_text.strip():
            if not args.quiet:
                print("No diff input provided or input is empty", file=sys.stderr)
            return 1
        
        # Process the diff
        summary = process_diff(diff_text, args.quiet)
        
        if summary is None:
            return 1
        
        # Format output
        output_text = format_output(summary, args)
        
        # Write output
        write_output(output_text, args.output)
        
        return 0
        
    except KeyboardInterrupt:
        if not args.quiet:
            print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_diff_input(args) -> str:
    """Get diff input from various sources."""
    if args.diff:
        return args.diff
    elif args.input:
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")
        
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(args.input, 'r', encoding='latin-1') as f:
                return f.read()
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("Reading from stdin... (Press Ctrl+D when done, Ctrl+C to cancel)")
        
        try:
            return sys.stdin.read()
        except UnicodeDecodeError:
            raise ValueError("Unable to decode input. Please ensure input is valid text.")


def process_diff(diff_text: str, quiet: bool = False) -> Optional[object]:
    """Process diff text and return summary."""
    try:
        if not quiet:
            print("Parsing git diff...", file=sys.stderr)
        
        # Parse diff
        diff_parser = DiffParser()
        file_changes = diff_parser.parse_diff(diff_text)
        
        if not file_changes:
            if not quiet:
                print("No file changes detected in diff", file=sys.stderr)
            return None
        
        if not quiet:
            print(f"Found {len(file_changes)} file(s) changed", file=sys.stderr)
            print("Analyzing changes...", file=sys.stderr)
        
        # Analyze changes
        analyzer = CodeAnalyzer()
        analyzed_changes = analyzer.analyze_changes(file_changes)
        
        if not quiet:
            print("Generating summary...", file=sys.stderr)
        
        # Generate summary
        generator = SummaryGenerator()
        summary = generator.generate_summary(analyzed_changes)
        
        return summary
        
    except Exception as e:
        raise RuntimeError(f"Failed to process diff: {e}")


def format_output(summary, args) -> str:
    """Format summary according to specified options."""
    formatter = OutputFormatter()
    
    try:
        if args.template:
            return formatter.apply_template(summary, args.template)
        elif args.template_name:
            template = config.get_template(args.template_name)
            if template is None:
                raise ValueError(f"Template '{args.template_name}' not found in configuration")
            return formatter.apply_template(summary, template)
        else:
            return formatter.format_output(summary, args.format)
    except Exception as e:
        raise RuntimeError(f"Failed to format output: {e}")


def write_output(output_text: str, output_file: Optional[str]):
    """Write output to file or stdout."""
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
        except Exception as e:
            raise RuntimeError(f"Failed to write output file: {e}")
    else:
        try:
            print(output_text)
        except UnicodeEncodeError:
            # Fallback for systems with limited unicode support
            print(output_text.encode('ascii', 'replace').decode('ascii'))


def validate_args(args):
    """Validate command line arguments."""
    # Validate format
    formatter = OutputFormatter()
    if not formatter.validate_format(args.format):
        raise ValueError(f"Unsupported output format: {args.format}")
    
    # Validate template if provided
    if args.template and args.format != 'plain':
        print("Warning: --template option overrides --format option", file=sys.stderr)
    
    # Validate output file path
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        # Check if we can write to the output file
        try:
            with open(args.output, 'w') as f:
                pass
            os.remove(args.output)  # Clean up test file
        except PermissionError:
            raise ValueError(f"Permission denied: cannot write to {args.output}")
        except Exception as e:
            raise ValueError(f"Cannot write to output file {args.output}: {e}")


if __name__ == '__main__':
    sys.exit(main())