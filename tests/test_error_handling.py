"""
Tests for error handling and validation.
"""

import unittest
import logging
from unittest.mock import patch, MagicMock
from code_summarizer.parser import DiffParser
from code_summarizer.analyzer import CodeAnalyzer
from code_summarizer.generator import SummaryGenerator
from code_summarizer.formatter import OutputFormatter
from code_summarizer.models import FileChange, AnalyzedChange, Summary, ChangeStatistics


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable logging during tests to avoid noise
        logging.disable(logging.CRITICAL)
        
        self.parser = DiffParser()
        self.analyzer = CodeAnalyzer()
        self.generator = SummaryGenerator()
        self.formatter = OutputFormatter()
    
    def tearDown(self):
        """Clean up after tests."""
        # Re-enable logging
        logging.disable(logging.NOTSET)
    
    def test_parser_empty_input(self):
        """Test parser with empty input."""
        result = self.parser.parse_diff("")
        self.assertEqual(len(result), 0)
        
        result = self.parser.parse_diff(None)
        self.assertEqual(len(result), 0)
        
        result = self.parser.parse_diff("   \n  \n  ")
        self.assertEqual(len(result), 0)
    
    def test_parser_malformed_diff(self):
        """Test parser with malformed diff."""
        malformed_diff = """
        This is not a valid git diff
        Random text here
        @@@ invalid hunk header
        +++ some content
        """
        
        # Should not raise exception, but return empty list
        result = self.parser.parse_diff(malformed_diff)
        self.assertIsInstance(result, list)
    
    def test_parser_validate_diff_format(self):
        """Test diff format validation."""
        # Valid diff
        valid_diff = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
 line1
+line2"""
        self.assertTrue(self.parser.validate_diff_format(valid_diff))
        
        # Invalid diff
        invalid_diff = "This is not a diff"
        self.assertFalse(self.parser.validate_diff_format(invalid_diff))
        
        # Empty diff
        self.assertFalse(self.parser.validate_diff_format(""))
        self.assertFalse(self.parser.validate_diff_format(None))
    
    def test_analyzer_empty_input(self):
        """Test analyzer with empty input."""
        result = self.analyzer.analyze_changes([])
        self.assertEqual(len(result), 0)
        
        result = self.analyzer.analyze_changes(None)
        self.assertEqual(len(result), 0)
    
    def test_analyzer_invalid_file_change(self):
        """Test analyzer with invalid file change."""
        # File change with no filename
        invalid_file_change = FileChange(filename="", change_type="modified")
        
        result = self.analyzer.analyze_changes([invalid_file_change])
        # Should skip invalid file changes
        self.assertEqual(len(result), 0)
    
    def test_analyzer_exception_handling(self):
        """Test analyzer handles exceptions gracefully."""
        # Create a file change that might cause issues
        file_change = FileChange(filename="test.py", change_type="modified")
        
        # Mock a method to raise an exception
        with patch.object(self.analyzer, '_analyze_structural_changes', side_effect=Exception("Test error")):
            result = self.analyzer.analyze_changes([file_change])
            
            # Should still return a result, but with error indicators
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].purpose_inference, "Analysis failed")
            self.assertEqual(result[0].impact_assessment, "Unable to assess impact")
    
    def test_generator_empty_input(self):
        """Test generator with empty input."""
        result = self.generator.generate_summary([])
        
        self.assertIsInstance(result, Summary)
        self.assertEqual(result.overview, "No changes detected")
        self.assertEqual(len(result.file_summaries), 0)
    
    def test_generator_exception_handling(self):
        """Test generator handles exceptions gracefully."""
        # Create a mock analyzed change
        file_change = FileChange(filename="test.py", change_type="modified")
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference="Test",
            impact_assessment="Test",
            complexity_score=1
        )
        
        # Mock a method to raise an exception
        with patch.object(self.generator, '_create_file_summary', side_effect=Exception("Test error")):
            result = self.generator.generate_summary([analyzed_change])
            
            # Should still return a summary
            self.assertIsInstance(result, Summary)
            self.assertEqual(len(result.file_summaries), 1)
            self.assertIn("Error generating summary", result.file_summaries[0].summary)
    
    def test_formatter_none_summary(self):
        """Test formatter with None summary."""
        with self.assertRaises(ValueError) as context:
            self.formatter.format_output(None, 'plain')
        
        self.assertIn("Summary cannot be None", str(context.exception))
    
    def test_formatter_empty_format_type(self):
        """Test formatter with empty format type."""
        summary = Summary(overview="Test")
        
        with self.assertRaises(ValueError) as context:
            self.formatter.format_output(summary, "")
        
        self.assertIn("Format type cannot be empty", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.formatter.format_output(summary, None)
        
        self.assertIn("Format type cannot be empty", str(context.exception))
    
    def test_formatter_invalid_format_type(self):
        """Test formatter with invalid format type."""
        summary = Summary(overview="Test")
        
        with self.assertRaises(ValueError) as context:
            self.formatter.format_output(summary, 'invalid_format')
        
        self.assertIn("Unsupported format type", str(context.exception))
    
    def test_template_none_summary(self):
        """Test template application with None summary."""
        with self.assertRaises(ValueError) as context:
            self.formatter.apply_template(None, "Test template")
        
        self.assertIn("Summary cannot be None", str(context.exception))
    
    def test_template_empty_template(self):
        """Test template application with empty template."""
        summary = Summary(overview="Test")
        
        with self.assertRaises(ValueError) as context:
            self.formatter.apply_template(summary, "")
        
        self.assertIn("Template cannot be empty", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.formatter.apply_template(summary, None)
        
        self.assertIn("Template cannot be empty", str(context.exception))
    
    def test_template_invalid_variable(self):
        """Test template application with invalid variable."""
        summary = Summary(overview="Test")
        template = "Invalid variable: {invalid_var}"
        
        with self.assertRaises(ValueError) as context:
            self.formatter.apply_template(summary, template)
        
        self.assertIn("Template variable not found", str(context.exception))
    
    def test_template_malformed_template(self):
        """Test template application with malformed template."""
        summary = Summary(overview="Test")
        template = "Malformed template: {unclosed_brace"
        
        with self.assertRaises(ValueError) as context:
            self.formatter.apply_template(summary, template)
        
        self.assertIn("Error applying template", str(context.exception))
    
    def test_json_formatting_with_none_values(self):
        """Test JSON formatting handles None values gracefully."""
        # Create summary with potential None values
        summary = Summary(
            overview=None,
            file_summaries=[],
            statistics=ChangeStatistics(),
            key_changes=None,
            recommendations=None
        )
        
        # Should not raise exception
        result = self.formatter.format_output(summary, 'json')
        self.assertIsInstance(result, str)
        
        # Should be valid JSON
        import json
        data = json.loads(result)
        self.assertIsInstance(data, dict)
    
    def test_markdown_formatting_with_empty_sections(self):
        """Test Markdown formatting handles empty sections gracefully."""
        summary = Summary(
            overview="Test overview",
            file_summaries=[],
            statistics=ChangeStatistics(),
            key_changes=[],
            recommendations=[]
        )
        
        result = self.formatter.format_output(summary, 'markdown')
        self.assertIsInstance(result, str)
        self.assertIn("# Code Change Summary", result)
        self.assertIn("Test overview", result)
    
    def test_plain_text_formatting_with_empty_sections(self):
        """Test plain text formatting handles empty sections gracefully."""
        summary = Summary(
            overview="Test overview",
            file_summaries=[],
            statistics=ChangeStatistics(),
            key_changes=[],
            recommendations=[]
        )
        
        result = self.formatter.format_output(summary, 'plain')
        self.assertIsInstance(result, str)
        self.assertIn("CODE CHANGE SUMMARY", result)
        self.assertIn("Test overview", result)
    
    def test_language_detection_edge_cases(self):
        """Test language detection with edge cases."""
        # Empty filename
        result = self.analyzer.detect_language("")
        self.assertEqual(result, "unknown")
        
        # Filename with no extension (but README is special case)
        result = self.analyzer.detect_language("README")
        self.assertEqual(result, "markdown")  # README files are detected as markdown
        
        # Truly unknown filename
        result = self.analyzer.detect_language("randomfile")
        self.assertEqual(result, "unknown")
        
        # Filename with multiple dots
        result = self.analyzer.detect_language("test.backup.py")
        self.assertEqual(result, "python")
        
        # Very long filename
        long_filename = "a" * 1000 + ".py"
        result = self.analyzer.detect_language(long_filename)
        self.assertEqual(result, "python")
    
    def test_code_structure_parsing_edge_cases(self):
        """Test code structure parsing with edge cases."""
        # Empty code
        result = self.analyzer.parse_code_structure("", "python")
        self.assertEqual(result, {})
        
        # Unknown language
        result = self.analyzer.parse_code_structure("some code", "unknown_language")
        self.assertEqual(result, {})
        
        # Code with special characters
        special_code = "def test_函数():\n    pass"
        result = self.analyzer.parse_code_structure(special_code, "python")
        self.assertIsInstance(result, dict)
    
    def test_complexity_score_bounds(self):
        """Test complexity score stays within bounds."""
        # Create a file change that might produce high complexity
        file_change = FileChange(filename="test.py", change_type="modified")
        file_change.lines_added = 10000  # Very high number
        file_change.lines_removed = 10000
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference="Test",
            impact_assessment="Test",
            complexity_score=0
        )
        
        # Calculate complexity score
        score = self.analyzer._calculate_complexity_score(file_change, [])
        
        # Should be capped at 10
        self.assertLessEqual(score, 10)
        self.assertGreaterEqual(score, 0)
    
    def test_robust_diff_parsing(self):
        """Test diff parsing with various edge cases."""
        # Diff with binary files
        binary_diff = """diff --git a/image.png b/image.png
index 1234567..abcdefg 100644
Binary files a/image.png and b/image.png differ
"""
        result = self.parser.parse_diff(binary_diff)
        self.assertIsInstance(result, list)
        
        # Diff with very long lines
        long_line_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
 short_line
+""" + "a" * 10000
        
        result = self.parser.parse_diff(long_line_diff)
        self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()