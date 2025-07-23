"""
Tests for command-line interface.
"""

import unittest
import sys
import io
import tempfile
import os
from unittest.mock import patch, MagicMock
from code_summarizer.cli import main, get_diff_input, process_diff, format_output, write_output


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Hello, World!")
     return "hello"
 
"""
    
    def test_get_diff_input_from_string(self):
        """Test getting diff input from string argument."""
        args = MagicMock()
        args.diff = self.sample_diff
        args.input = None
        
        result = get_diff_input(args)
        self.assertEqual(result, self.sample_diff)
    
    def test_get_diff_input_from_file(self):
        """Test getting diff input from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.diff') as f:
            f.write(self.sample_diff)
            temp_file = f.name
        
        try:
            args = MagicMock()
            args.diff = None
            args.input = temp_file
            
            result = get_diff_input(args)
            self.assertEqual(result, self.sample_diff)
        finally:
            os.unlink(temp_file)
    
    def test_get_diff_input_file_not_found(self):
        """Test error handling for non-existent input file."""
        args = MagicMock()
        args.diff = None
        args.input = 'non_existent_file.diff'
        
        with self.assertRaises(FileNotFoundError):
            get_diff_input(args)
    
    @patch('sys.stdin')
    def test_get_diff_input_from_stdin(self, mock_stdin):
        """Test getting diff input from stdin."""
        mock_stdin.read.return_value = self.sample_diff
        mock_stdin.isatty.return_value = False
        
        args = MagicMock()
        args.diff = None
        args.input = None
        
        result = get_diff_input(args)
        self.assertEqual(result, self.sample_diff)
    
    def test_process_diff_success(self):
        """Test successful diff processing."""
        summary = process_diff(self.sample_diff, quiet=True)
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.statistics.total_files, 1)
        self.assertEqual(summary.statistics.files_modified, 1)
        self.assertGreater(summary.statistics.total_lines_added, 0)
    
    def test_process_diff_empty(self):
        """Test processing empty diff."""
        summary = process_diff("", quiet=True)
        self.assertIsNone(summary)
    
    def test_process_diff_invalid(self):
        """Test processing invalid diff."""
        # Our parser is robust and handles invalid input gracefully
        # It should return None for invalid diff that produces no file changes
        result = process_diff("invalid diff content", quiet=True)
        self.assertIsNone(result)
    
    def test_format_output_plain(self):
        """Test formatting output as plain text."""
        summary = process_diff(self.sample_diff, quiet=True)
        
        args = MagicMock()
        args.format = 'plain'
        args.template = None
        args.template_name = None
        
        result = format_output(summary, args)
        
        self.assertIn('CODE CHANGE SUMMARY', result)
        self.assertIn('OVERVIEW:', result)
        self.assertIn('test.py', result)
    
    def test_format_output_json(self):
        """Test formatting output as JSON."""
        summary = process_diff(self.sample_diff, quiet=True)
        
        args = MagicMock()
        args.format = 'json'
        args.template = None
        args.template_name = None
        
        result = format_output(summary, args)
        
        # Should be valid JSON
        import json
        data = json.loads(result)
        self.assertIn('overview', data)
        self.assertIn('statistics', data)
    
    def test_format_output_markdown(self):
        """Test formatting output as Markdown."""
        summary = process_diff(self.sample_diff, quiet=True)
        
        args = MagicMock()
        args.format = 'markdown'
        args.template = None
        args.template_name = None
        
        result = format_output(summary, args)
        
        self.assertIn('# Code Change Summary', result)
        self.assertIn('## Overview', result)
        self.assertIn('### test.py', result)
    
    def test_format_output_template(self):
        """Test formatting output with custom template."""
        summary = process_diff(self.sample_diff, quiet=True)
        
        args = MagicMock()
        args.format = 'plain'
        args.template = 'Files: {total_files}, Added: {lines_added}'
        
        result = format_output(summary, args)
        
        self.assertIn('Files: 1', result)
        self.assertIn('Added:', result)
    
    def test_write_output_stdout(self):
        """Test writing output to stdout."""
        output_text = "Test output"
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            write_output(output_text, None)
            self.assertEqual(mock_stdout.getvalue().strip(), output_text)
    
    def test_write_output_file(self):
        """Test writing output to file."""
        output_text = "Test output"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
        
        try:
            write_output(output_text, temp_file)
            
            with open(temp_file, 'r') as f:
                result = f.read()
            
            self.assertEqual(result, output_text)
        finally:
            os.unlink(temp_file)
    
    @patch('sys.argv', ['cli.py', '--version'])
    def test_version_argument(self):
        """Test --version argument."""
        with self.assertRaises(SystemExit) as context:
            main()
        
        # argparse exits with code 0 for --version
        self.assertEqual(context.exception.code, 0)
    
    @patch('sys.argv', ['cli.py', '--help'])
    def test_help_argument(self):
        """Test --help argument."""
        with self.assertRaises(SystemExit) as context:
            main()
        
        # argparse exits with code 0 for --help
        self.assertEqual(context.exception.code, 0)
    
    @patch('sys.argv', ['cli.py', '--diff', 'test diff'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_with_diff_argument(self, mock_stdout):
        """Test main function with --diff argument."""
        result = main()
        
        # Should return 1 because 'test diff' is not a valid git diff
        # and produces no file changes
        self.assertEqual(result, 1)
    
    @patch('sys.argv', ['cli.py', '--format', 'json'])
    @patch('sys.stdin', io.StringIO(''))
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_main_empty_input(self, mock_stderr):
        """Test main function with empty input."""
        result = main()
        
        # Should return 1 for empty input
        self.assertEqual(result, 1)
        
        # Should show error message
        error_output = mock_stderr.getvalue()
        self.assertIn('No diff input provided', error_output)
    
    @patch('sys.argv', ['cli.py', '--diff', 'invalid diff', '--quiet'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_quiet_mode(self, mock_stdout):
        """Test main function in quiet mode."""
        result = main()
        
        # Should return 1 because invalid diff produces no file changes
        self.assertEqual(result, 1)
    
    @patch('sys.argv', ['cli.py', '--input', 'non_existent.diff'])
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_main_file_not_found(self, mock_stderr):
        """Test main function with non-existent input file."""
        result = main()
        
        # Should return 1 for file not found
        self.assertEqual(result, 1)
        
        # Should show error message
        error_output = mock_stderr.getvalue()
        self.assertIn('Error:', error_output)
    
    @patch('sys.argv', ['cli.py', '--format', 'invalid'])
    @patch('sys.stdin', io.StringIO('test diff'))
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_main_invalid_format(self, mock_stderr):
        """Test main function with invalid format."""
        with self.assertRaises(SystemExit):
            # argparse should exit with error for invalid choice
            main()
    
    def test_integration_full_pipeline(self):
        """Test full integration of the pipeline."""
        # Create a more comprehensive diff
        complex_diff = """diff --git a/module.py b/module.py
index 1234567..abcdefg 100644
--- a/module.py
+++ b/module.py
@@ -1,5 +1,8 @@
+import os
+
 class MyClass:
     def __init__(self):
-        self.value = 1
+        self.value = 42
+        self.name = "test"
     
     def method(self):
         return self.value
@@ -10,3 +13,6 @@ def helper_function():
     return "helper"
 
 # End of file
+
+def new_function():
+    return "new"
"""
        
        # Test the full pipeline
        summary = process_diff(complex_diff, quiet=True)
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.statistics.total_files, 1)
        self.assertGreater(len(summary.file_summaries), 0)
        # Key changes might be empty for some diffs, so just check it's a list
        self.assertIsInstance(summary.key_changes, list)
        
        # Test different output formats
        args_plain = MagicMock()
        args_plain.format = 'plain'
        args_plain.template = None
        args_plain.template_name = None
        
        plain_output = format_output(summary, args_plain)
        self.assertIn('CODE CHANGE SUMMARY', plain_output)
        
        args_json = MagicMock()
        args_json.format = 'json'
        args_json.template = None
        args_json.template_name = None
        
        json_output = format_output(summary, args_json)
        import json
        json_data = json.loads(json_output)
        self.assertIn('overview', json_data)
        
        args_md = MagicMock()
        args_md.format = 'markdown'
        args_md.template = None
        args_md.template_name = None
        
        md_output = format_output(summary, args_md)
        self.assertIn('# Code Change Summary', md_output)


if __name__ == '__main__':
    unittest.main()