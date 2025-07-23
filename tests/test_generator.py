"""
Tests for summary generator.
"""

import unittest
from code_summarizer.generator import SummaryGenerator
from code_summarizer.models import (
    AnalyzedChange, FileChange, StructuralChange, Hunk, DiffLine
)


class TestSummaryGenerator(unittest.TestCase):
    """Test cases for SummaryGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = SummaryGenerator()
    
    def test_generate_summary_empty(self):
        """Test generating summary for empty changes."""
        summary = self.generator.generate_summary([])
        
        self.assertEqual(summary.overview, "No changes detected")
        self.assertEqual(len(summary.file_summaries), 0)
        self.assertEqual(summary.statistics.total_files, 0)
        self.assertEqual(len(summary.key_changes), 0)
        self.assertEqual(len(summary.recommendations), 0)
    
    def test_generate_summary_single_file(self):
        """Test generating summary for single file change."""
        # Create a simple file change
        diff_lines = [
            DiffLine(line_type='+', content='def new_function():'),
            DiffLine(line_type='+', content='    return "hello"'),
        ]
        hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=2, lines=diff_lines)
        file_change = FileChange(filename='test.py', change_type='modified', hunks=[hunk])
        file_change.lines_added = 2
        file_change.lines_removed = 0
        file_change.language = 'python'
        
        structural_change = StructuralChange(
            change_type='function_added',
            element_name='new_function',
            description='Added function new_function'
        )
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[structural_change],
            purpose_inference='Feature addition',
            impact_assessment='Small-scale changes - low impact',
            complexity_score=2
        )
        
        summary = self.generator.generate_summary([analyzed_change])
        
        # Check overview
        self.assertIn('1 file changed', summary.overview)
        self.assertIn('1 modified', summary.overview)
        self.assertIn('+2 lines', summary.overview)
        
        # Check statistics
        self.assertEqual(summary.statistics.total_files, 1)
        self.assertEqual(summary.statistics.files_modified, 1)
        self.assertEqual(summary.statistics.total_lines_added, 2)
        self.assertEqual(summary.statistics.total_lines_removed, 0)
        
        # Check file summaries
        self.assertEqual(len(summary.file_summaries), 1)
        file_summary = summary.file_summaries[0]
        self.assertEqual(file_summary.filename, 'test.py')
        self.assertIn('Modified', file_summary.summary)
        self.assertIn('Feature addition', file_summary.summary)
    
    def test_generate_summary_multiple_files(self):
        """Test generating summary for multiple file changes."""
        # Create multiple file changes
        changes = []
        
        # New file
        new_file = FileChange(filename='new.py', change_type='added')
        new_file.lines_added = 10
        new_file.language = 'python'
        changes.append(AnalyzedChange(
            file_change=new_file,
            structural_changes=[],
            purpose_inference='New file creation',
            impact_assessment='New functionality introduced',
            complexity_score=3
        ))
        
        # Modified file
        mod_file = FileChange(filename='existing.py', change_type='modified')
        mod_file.lines_added = 5
        mod_file.lines_removed = 3
        mod_file.language = 'python'
        changes.append(AnalyzedChange(
            file_change=mod_file,
            structural_changes=[],
            purpose_inference='Bug fix or enhancement',
            impact_assessment='Small-scale changes - low impact',
            complexity_score=2
        ))
        
        # Deleted file
        del_file = FileChange(filename='old.py', change_type='deleted')
        del_file.lines_removed = 20
        del_file.language = 'python'
        changes.append(AnalyzedChange(
            file_change=del_file,
            structural_changes=[],
            purpose_inference='File removal',
            impact_assessment='Functionality removed - may break dependencies',
            complexity_score=4
        ))
        
        summary = self.generator.generate_summary(changes)
        
        # Check overview
        self.assertIn('3 files changed', summary.overview)
        self.assertIn('1 added', summary.overview)
        self.assertIn('1 modified', summary.overview)
        self.assertIn('1 deleted', summary.overview)
        
        # Check statistics
        self.assertEqual(summary.statistics.total_files, 3)
        self.assertEqual(summary.statistics.files_added, 1)
        self.assertEqual(summary.statistics.files_modified, 1)
        self.assertEqual(summary.statistics.files_deleted, 1)
        self.assertEqual(summary.statistics.total_lines_added, 15)
        self.assertEqual(summary.statistics.total_lines_removed, 23)
        
        # Check file summaries
        self.assertEqual(len(summary.file_summaries), 3)
        
        # Check key changes
        self.assertGreater(len(summary.key_changes), 0)
        key_changes_text = ' '.join(summary.key_changes)
        self.assertIn('new.py', key_changes_text)
        self.assertIn('old.py', key_changes_text)
    
    def test_create_change_description_added_file(self):
        """Test creating description for added file."""
        file_change = FileChange(filename='new_module.py', change_type='added')
        file_change.lines_added = 50
        file_change.language = 'python'
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='New file creation',
            impact_assessment='New functionality introduced',
            complexity_score=3
        )
        
        description = self.generator.create_change_description(analyzed_change)
        
        self.assertIn("Added new file 'new_module.py'", description)
        self.assertIn('+50 lines', description)
        self.assertIn('New file creation', description)
    
    def test_create_change_description_with_structural_changes(self):
        """Test creating description with structural changes."""
        file_change = FileChange(filename='api.py', change_type='modified')
        file_change.lines_added = 10
        file_change.lines_removed = 5
        file_change.language = 'python'
        
        structural_changes = [
            StructuralChange(
                change_type='function_added',
                element_name='new_endpoint',
                description='Added function new_endpoint'
            ),
            StructuralChange(
                change_type='class_modified',
                element_name='APIHandler',
                description='Modified class APIHandler'
            )
        ]
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=structural_changes,
            purpose_inference='Feature addition; Bug fix or enhancement',
            impact_assessment='Medium-scale changes - moderate impact',
            complexity_score=5
        )
        
        description = self.generator.create_change_description(analyzed_change)
        
        self.assertIn("Modified 'api.py'", description)
        self.assertIn('+10 lines', description)
        self.assertIn('-5 lines', description)
        self.assertIn('added function new_endpoint', description)
        self.assertIn('modified class APIHandler', description)
    
    def test_identify_key_changes_high_complexity(self):
        """Test identifying high complexity changes as key changes."""
        file_change = FileChange(filename='complex.py', change_type='modified')
        file_change.lines_added = 200
        file_change.lines_removed = 150
        file_change.language = 'python'
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='Architecture refactoring',
            impact_assessment='Large-scale changes - high impact',
            complexity_score=9
        )
        
        summary = self.generator.generate_summary([analyzed_change])
        
        key_changes_text = ' '.join(summary.key_changes)
        self.assertIn('High complexity change', key_changes_text)
        self.assertIn('Large change', key_changes_text)
    
    def test_generate_recommendations_high_complexity(self):
        """Test generating recommendations for high complexity changes."""
        file_change = FileChange(filename='complex.py', change_type='modified')
        file_change.language = 'python'
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='Feature addition',
            impact_assessment='Large-scale changes - high impact',
            complexity_score=8
        )
        
        summary = self.generator.generate_summary([analyzed_change])
        
        recommendations_text = ' '.join(summary.recommendations)
        self.assertIn('high-complexity', recommendations_text)
    
    def test_generate_recommendations_test_coverage(self):
        """Test generating test coverage recommendations."""
        # Create multiple non-test files
        changes = []
        for i in range(3):
            file_change = FileChange(filename=f'module_{i}.py', change_type='modified')
            file_change.language = 'python'
            changes.append(AnalyzedChange(
                file_change=file_change,
                structural_changes=[],
                purpose_inference='Feature addition',
                impact_assessment='Small-scale changes - low impact',
                complexity_score=2
            ))
        
        summary = self.generator.generate_summary(changes)
        
        recommendations_text = ' '.join(summary.recommendations)
        self.assertIn('adding tests', recommendations_text)
    
    def test_generate_recommendations_documentation(self):
        """Test generating documentation recommendations."""
        file_change = FileChange(filename='new_feature.py', change_type='added')
        file_change.language = 'python'
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='Feature addition',
            impact_assessment='New functionality introduced',
            complexity_score=3
        )
        
        summary = self.generator.generate_summary([analyzed_change])
        
        recommendations_text = ' '.join(summary.recommendations)
        self.assertIn('documentation', recommendations_text)
    
    def test_generate_recommendations_api_changes(self):
        """Test generating API change recommendations."""
        file_change = FileChange(filename='api.py', change_type='modified')
        file_change.language = 'python'
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='Feature addition',
            impact_assessment='Public API changes (2 elements) - may affect external code',
            complexity_score=4
        )
        
        summary = self.generator.generate_summary([analyzed_change])
        
        recommendations_text = ' '.join(summary.recommendations)
        self.assertIn('API changes', recommendations_text)
        self.assertIn('backward compatibility', recommendations_text)
    
    def test_generate_recommendations_large_scale(self):
        """Test generating large scale change recommendations."""
        file_change = FileChange(filename='large_refactor.py', change_type='modified')
        file_change.lines_added = 300
        file_change.lines_removed = 250
        file_change.language = 'python'
        
        analyzed_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='Architecture refactoring',
            impact_assessment='Large-scale changes - high impact',
            complexity_score=7
        )
        
        summary = self.generator.generate_summary([analyzed_change])
        
        recommendations_text = ' '.join(summary.recommendations)
        self.assertIn('Large-scale changes', recommendations_text)
        self.assertIn('smaller commits', recommendations_text)
    
    def test_describe_structural_changes_mixed(self):
        """Test describing mixed structural changes."""
        structural_changes = [
            StructuralChange(
                change_type='function_added',
                element_name='new_func1',
                description='Added function new_func1'
            ),
            StructuralChange(
                change_type='function_added',
                element_name='new_func2',
                description='Added function new_func2'
            ),
            StructuralChange(
                change_type='class_modified',
                element_name='MyClass',
                description='Modified class MyClass'
            ),
            StructuralChange(
                change_type='function_removed',
                element_name='old_func',
                description='Removed function old_func'
            )
        ]
        
        description = self.generator._describe_structural_changes(structural_changes)
        
        self.assertIn('added 2 functions', description)
        self.assertIn('modified class MyClass', description)
        self.assertIn('removed function old_func', description)
    
    def test_file_summary_complexity_indicators(self):
        """Test file summary includes complexity indicators."""
        file_change = FileChange(filename='complex.py', change_type='modified')
        file_change.language = 'python'
        
        # High complexity change
        high_complexity_change = AnalyzedChange(
            file_change=file_change,
            structural_changes=[],
            purpose_inference='Feature addition',
            impact_assessment='Large-scale changes - high impact',
            complexity_score=8
        )
        
        file_summary = self.generator._create_file_summary(high_complexity_change)
        
        key_changes_text = ' '.join(file_summary.key_changes)
        self.assertIn('High complexity change', key_changes_text)
        self.assertIn('score: 8/10', key_changes_text)
        self.assertIn('High impact change', key_changes_text)
    
    def test_overview_primary_focus(self):
        """Test overview includes primary focus from purposes."""
        changes = []
        
        # Multiple changes with same purpose
        for i in range(3):
            file_change = FileChange(filename=f'test_{i}.py', change_type='modified')
            file_change.language = 'python'
            changes.append(AnalyzedChange(
                file_change=file_change,
                structural_changes=[],
                purpose_inference='Bug fix or enhancement',
                impact_assessment='Small-scale changes - low impact',
                complexity_score=2
            ))
        
        summary = self.generator.generate_summary(changes)
        
        self.assertIn('Primary focus: Bug fix or enhancement', summary.overview)


if __name__ == '__main__':
    unittest.main()