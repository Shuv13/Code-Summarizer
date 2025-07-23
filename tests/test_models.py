"""
Tests for data models.
"""

import unittest
from code_summarizer.models import (
    DiffLine, Hunk, FileChange, StructuralChange, 
    AnalyzedChange, Summary, ChangeStatistics, FileSummary
)


class TestModels(unittest.TestCase):
    """Test cases for data models."""
    
    def test_diff_line_creation(self):
        """Test DiffLine creation."""
        line = DiffLine(line_type='+', content='print("hello")', line_number=10)
        self.assertEqual(line.line_type, '+')
        self.assertEqual(line.content, 'print("hello")')
        self.assertEqual(line.line_number, 10)
    
    def test_file_change_creation(self):
        """Test FileChange creation with defaults."""
        file_change = FileChange(filename='test.py', change_type='modified')
        self.assertEqual(file_change.filename, 'test.py')
        self.assertEqual(file_change.change_type, 'modified')
        self.assertEqual(file_change.language, 'unknown')
        self.assertEqual(len(file_change.hunks), 0)
    
    def test_summary_creation(self):
        """Test Summary creation with defaults."""
        summary = Summary(overview='Test changes')
        self.assertEqual(summary.overview, 'Test changes')
        self.assertEqual(len(summary.file_summaries), 0)
        self.assertEqual(len(summary.key_changes), 0)
        self.assertIsInstance(summary.statistics, ChangeStatistics)


if __name__ == '__main__':
    unittest.main()