"""
Tests for output formatter.
"""

import json
import unittest
from code_summarizer.formatter import OutputFormatter
from code_summarizer.models import Summary, FileSummary, ChangeStatistics


class TestOutputFormatter(unittest.TestCase):
    """Test cases for OutputFormatter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter()
        
        # Create a sample summary for testing
        self.sample_summary = Summary(
            overview="2 files changed (1 added, 1 modified). (+15, -5 lines). Primary focus: Feature addition.",
            file_summaries=[
                FileSummary(
                    filename="new_feature.py",
                    summary="Added new file 'new_feature.py' - (+10 lines) - Purpose: Feature addition",
                    key_changes=["Added function 'new_feature'", "Medium complexity change (score: 4/10)"]
                ),
                FileSummary(
                    filename="existing.py",
                    summary="Modified 'existing.py' - (+5, -5 lines) - Purpose: Bug fix or enhancement",
                    key_changes=["Modified function 'existing_function'"]
                )
            ],
            statistics=ChangeStatistics(
                total_files=2,
                files_added=1,
                files_modified=1,
                files_deleted=0,
                total_lines_added=15,
                total_lines_removed=5
            ),
            key_changes=[
                "New file: new_feature.py",
                "Modified function in existing.py"
            ],
            recommendations=[
                "Consider adding tests for the new functionality",
                "Review medium-complexity changes carefully"
            ]
        )
    
    def test_format_json(self):
        """Test JSON formatting."""
        result = self.formatter.format_output(self.sample_summary, 'json')
        
        # Parse JSON to verify it's valid
        data = json.loads(result)
        
        # Check structure
        self.assertIn('overview', data)
        self.assertIn('statistics', data)
        self.assertIn('file_summaries', data)
        self.assertIn('key_changes', data)
        self.assertIn('recommendations', data)
        
        # Check statistics
        stats = data['statistics']
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['files_added'], 1)
        self.assertEqual(stats['files_modified'], 1)
        self.assertEqual(stats['total_lines_added'], 15)
        self.assertEqual(stats['total_lines_removed'], 5)
        
        # Check file summaries
        self.assertEqual(len(data['file_summaries']), 2)
        self.assertEqual(data['file_summaries'][0]['filename'], 'new_feature.py')
        self.assertEqual(len(data['file_summaries'][0]['key_changes']), 2)
        
        # Check key changes and recommendations
        self.assertEqual(len(data['key_changes']), 2)
        self.assertEqual(len(data['recommendations']), 2)
    
    def test_format_markdown(self):
        """Test Markdown formatting."""
        result = self.formatter.format_output(self.sample_summary, 'markdown')
        
        # Check for Markdown headers
        self.assertIn('# Code Change Summary', result)
        self.assertIn('## Overview', result)
        self.assertIn('## Statistics', result)
        self.assertIn('## Key Changes', result)
        self.assertIn('## File Details', result)
        self.assertIn('## Recommendations', result)
        
        # Check for Markdown formatting
        self.assertIn('**Total files changed:**', result)
        self.assertIn('**Files added:**', result)
        self.assertIn('**Files modified:**', result)
        self.assertIn('**Lines added:**', result)
        self.assertIn('**Lines removed:**', result)
        
        # Check file details
        self.assertIn('### new_feature.py', result)
        self.assertIn('### existing.py', result)
        self.assertIn('**Key changes:**', result)
        
        # Check bullet points
        self.assertIn('- New file: new_feature.py', result)
        self.assertIn('- Consider adding tests', result)
    
    def test_format_plain_text(self):
        """Test plain text formatting."""
        result = self.formatter.format_output(self.sample_summary, 'plain')
        
        # Check for plain text headers
        self.assertIn('CODE CHANGE SUMMARY', result)
        self.assertIn('=' * 50, result)
        self.assertIn('OVERVIEW:', result)
        self.assertIn('STATISTICS:', result)
        self.assertIn('KEY CHANGES:', result)
        self.assertIn('FILE DETAILS:', result)
        self.assertIn('RECOMMENDATIONS:', result)
        
        # Check for indentation and numbering
        self.assertIn('  Total files changed: 2', result)
        self.assertIn('  Files added: 1', result)
        self.assertIn('  1. New file: new_feature.py', result)
        self.assertIn('  1. Consider adding tests', result)
        
        # Check file details
        self.assertIn('File: new_feature.py', result)
        self.assertIn('File: existing.py', result)
        self.assertIn('Summary:', result)
    
    def test_format_case_insensitive(self):
        """Test that format types are case insensitive."""
        json_result1 = self.formatter.format_output(self.sample_summary, 'JSON')
        json_result2 = self.formatter.format_output(self.sample_summary, 'json')
        self.assertEqual(json_result1, json_result2)
        
        md_result1 = self.formatter.format_output(self.sample_summary, 'MARKDOWN')
        md_result2 = self.formatter.format_output(self.sample_summary, 'markdown')
        self.assertEqual(md_result1, md_result2)
    
    def test_format_aliases(self):
        """Test format type aliases."""
        # Test markdown aliases
        md_result = self.formatter.format_output(self.sample_summary, 'markdown')
        md_alias_result = self.formatter.format_output(self.sample_summary, 'md')
        self.assertEqual(md_result, md_alias_result)
        
        # Test plain text aliases
        plain_result = self.formatter.format_output(self.sample_summary, 'plain')
        text_result = self.formatter.format_output(self.sample_summary, 'text')
        self.assertEqual(plain_result, text_result)
    
    def test_unsupported_format(self):
        """Test error handling for unsupported format."""
        with self.assertRaises(ValueError) as context:
            self.formatter.format_output(self.sample_summary, 'xml')
        
        self.assertIn('Unsupported format type: xml', str(context.exception))
    
    def test_apply_template_basic(self):
        """Test basic template application."""
        template = """
Summary: {overview}
Total Files: {total_files}
Lines Added: {lines_added}
Lines Removed: {lines_removed}
"""
        
        result = self.formatter.apply_template(self.sample_summary, template)
        
        self.assertIn('Total Files: 2', result)
        self.assertIn('Lines Added: 15', result)
        self.assertIn('Lines Removed: 5', result)
        self.assertIn('Summary: 2 files changed', result)
    
    def test_apply_template_with_lists(self):
        """Test template application with list variables."""
        template = """
Key Changes:
{key_changes}

Recommendations:
{recommendations}

File Summaries:
{file_summaries}
"""
        
        result = self.formatter.apply_template(self.sample_summary, template)
        
        self.assertIn('- New file: new_feature.py', result)
        self.assertIn('- Consider adding tests', result)
        self.assertIn('- new_feature.py:', result)
        self.assertIn('- existing.py:', result)
    
    def test_apply_template_missing_variable(self):
        """Test template application with missing variable."""
        template = "Unknown variable: {unknown_var}"
        
        with self.assertRaises(ValueError) as context:
            self.formatter.apply_template(self.sample_summary, template)
        
        self.assertIn('Template variable not found', str(context.exception))
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.formatter.get_supported_formats()
        
        expected_formats = ['json', 'markdown', 'md', 'plain', 'text']
        self.assertEqual(set(formats), set(expected_formats))
    
    def test_validate_format(self):
        """Test format validation."""
        # Valid formats
        self.assertTrue(self.formatter.validate_format('json'))
        self.assertTrue(self.formatter.validate_format('markdown'))
        self.assertTrue(self.formatter.validate_format('md'))
        self.assertTrue(self.formatter.validate_format('plain'))
        self.assertTrue(self.formatter.validate_format('text'))
        
        # Case insensitive
        self.assertTrue(self.formatter.validate_format('JSON'))
        self.assertTrue(self.formatter.validate_format('MARKDOWN'))
        
        # Invalid formats
        self.assertFalse(self.formatter.validate_format('xml'))
        self.assertFalse(self.formatter.validate_format('html'))
        self.assertFalse(self.formatter.validate_format(''))
    
    def test_format_empty_summary(self):
        """Test formatting empty summary."""
        empty_summary = Summary(
            overview="No changes detected",
            file_summaries=[],
            statistics=ChangeStatistics(),
            key_changes=[],
            recommendations=[]
        )
        
        # Test JSON
        json_result = self.formatter.format_output(empty_summary, 'json')
        data = json.loads(json_result)
        self.assertEqual(data['overview'], "No changes detected")
        self.assertEqual(len(data['file_summaries']), 0)
        self.assertEqual(len(data['key_changes']), 0)
        
        # Test Markdown
        md_result = self.formatter.format_output(empty_summary, 'markdown')
        self.assertIn('# Code Change Summary', md_result)
        self.assertIn('No changes detected', md_result)
        
        # Test Plain Text
        plain_result = self.formatter.format_output(empty_summary, 'plain')
        self.assertIn('CODE CHANGE SUMMARY', plain_result)
        self.assertIn('No changes detected', plain_result)
    
    def test_format_summary_without_optional_sections(self):
        """Test formatting summary without key changes or recommendations."""
        minimal_summary = Summary(
            overview="1 file changed (1 modified). (+5, -2 lines).",
            file_summaries=[
                FileSummary(
                    filename="test.py",
                    summary="Modified 'test.py' - (+5, -2 lines)",
                    key_changes=[]
                )
            ],
            statistics=ChangeStatistics(
                total_files=1,
                files_modified=1,
                total_lines_added=5,
                total_lines_removed=2
            ),
            key_changes=[],
            recommendations=[]
        )
        
        # Test that sections are omitted when empty
        md_result = self.formatter.format_output(minimal_summary, 'markdown')
        
        # Should have required sections
        self.assertIn('## Overview', md_result)
        self.assertIn('## Statistics', md_result)
        self.assertIn('## File Details', md_result)
        
        # Should not have empty optional sections in a way that breaks formatting
        self.assertIn('test.py', md_result)
    
    def test_json_unicode_handling(self):
        """Test JSON formatting with unicode characters."""
        unicode_summary = Summary(
            overview="File with unicode: café.py changed",
            file_summaries=[
                FileSummary(
                    filename="café.py",
                    summary="Modified 'café.py' with unicode content",
                    key_changes=["Added function with unicode: 'naïve_function'"]
                )
            ],
            statistics=ChangeStatistics(total_files=1, files_modified=1),
            key_changes=["Unicode file: café.py"],
            recommendations=[]
        )
        
        json_result = self.formatter.format_output(unicode_summary, 'json')
        data = json.loads(json_result)
        
        self.assertIn('café.py', data['overview'])
        self.assertEqual(data['file_summaries'][0]['filename'], 'café.py')
        self.assertIn('naïve_function', data['file_summaries'][0]['key_changes'][0])


if __name__ == '__main__':
    unittest.main()