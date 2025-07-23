"""
Tests for code analyzer.
"""

import unittest
from code_summarizer.analyzer import CodeAnalyzer
from code_summarizer.models import FileChange, Hunk, DiffLine


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for CodeAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()
    
    def test_detect_language_python(self):
        """Test Python language detection."""
        self.assertEqual(self.analyzer.detect_language('test.py'), 'python')
        self.assertEqual(self.analyzer.detect_language('module/__init__.py'), 'python')
    
    def test_detect_language_javascript(self):
        """Test JavaScript language detection."""
        self.assertEqual(self.analyzer.detect_language('script.js'), 'javascript')
        self.assertEqual(self.analyzer.detect_language('component.jsx'), 'javascript')
    
    def test_detect_language_typescript(self):
        """Test TypeScript language detection."""
        self.assertEqual(self.analyzer.detect_language('app.ts'), 'typescript')
        self.assertEqual(self.analyzer.detect_language('component.tsx'), 'typescript')
    
    def test_detect_language_java(self):
        """Test Java language detection."""
        self.assertEqual(self.analyzer.detect_language('Main.java'), 'java')
    
    def test_detect_language_special_cases(self):
        """Test special file name cases."""
        self.assertEqual(self.analyzer.detect_language('Makefile'), 'makefile')
        self.assertEqual(self.analyzer.detect_language('Dockerfile'), 'dockerfile')
        self.assertEqual(self.analyzer.detect_language('README.md'), 'markdown')
        self.assertEqual(self.analyzer.detect_language('package.json'), 'json')
        self.assertEqual(self.analyzer.detect_language('.gitignore'), 'config')
    
    def test_detect_language_unknown(self):
        """Test unknown language detection."""
        self.assertEqual(self.analyzer.detect_language('unknown.xyz'), 'unknown')
        self.assertEqual(self.analyzer.detect_language('noextension'), 'unknown')
    
    def test_parse_python_structure(self):
        """Test parsing Python code structure."""
        python_code = """
def hello_world():
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
    
    def method(self, param):
        return param * 2

import os
from sys import argv

@decorator
def decorated_func():
    pass

variable = "test"
"""
        structure = self.analyzer.parse_code_structure(python_code, 'python')
        
        # Check functions
        self.assertIn('function', structure)
        function_names = [f['name'] for f in structure['function']]
        self.assertIn('hello_world', function_names)
        self.assertIn('__init__', function_names)
        self.assertIn('method', function_names)
        self.assertIn('decorated_func', function_names)
        
        # Check classes
        self.assertIn('class', structure)
        self.assertEqual(structure['class'][0]['name'], 'TestClass')
        
        # Check imports
        self.assertIn('import', structure)
        self.assertEqual(len(structure['import']), 2)
        
        # Check decorators
        self.assertIn('decorator', structure)
        self.assertEqual(structure['decorator'][0]['name'], 'decorator')
        
        # Check variables
        self.assertIn('variable', structure)
        self.assertEqual(structure['variable'][0]['name'], 'variable')
    
    def test_parse_javascript_structure(self):
        """Test parsing JavaScript code structure."""
        js_code = """
function regularFunction() {
    return "hello";
}

const arrowFunc = () => {
    return "arrow";
};

class MyClass {
    constructor() {
        this.value = 1;
    }
    
    method() {
        return this.value;
    }
}

import { something } from 'module';
const variable = 42;
"""
        structure = self.analyzer.parse_code_structure(js_code, 'javascript')
        
        # Check functions
        self.assertIn('function', structure)
        function_names = [f['name'] for f in structure['function']]
        self.assertIn('regularFunction', function_names)
        self.assertIn('arrowFunc', function_names)
        
        # Check classes
        self.assertIn('class', structure)
        self.assertEqual(structure['class'][0]['name'], 'MyClass')
        
        # Check imports
        self.assertIn('import', structure)
        
        # Check variables (note: arrow functions are also captured as variables)
        self.assertIn('variable', structure)
        variable_names = [v['name'] for v in structure['variable']]
        self.assertIn('variable', variable_names)
    
    def test_analyze_changes_python_function_added(self):
        """Test analyzing Python function addition."""
        # Create a file change with added function
        diff_lines = [
            DiffLine(line_type='+', content='def new_function():'),
            DiffLine(line_type='+', content='    return "new"'),
            DiffLine(line_type=' ', content=''),
            DiffLine(line_type=' ', content='def existing_function():'),
            DiffLine(line_type=' ', content='    return "existing"')
        ]
        
        hunk = Hunk(old_start=1, old_count=3, new_start=1, new_count=5, lines=diff_lines)
        file_change = FileChange(filename='test.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        
        self.assertEqual(len(analyzed_changes), 1)
        analyzed_change = analyzed_changes[0]
        
        # Check language detection
        self.assertEqual(analyzed_change.file_change.language, 'python')
        
        # Check structural changes
        self.assertEqual(len(analyzed_change.structural_changes), 1)
        structural_change = analyzed_change.structural_changes[0]
        
        self.assertEqual(structural_change.change_type, 'function_added')
        self.assertEqual(structural_change.element_name, 'new_function')
        self.assertIn('Added function', structural_change.description)
    
    def test_analyze_changes_function_removed(self):
        """Test analyzing function removal."""
        diff_lines = [
            DiffLine(line_type='-', content='def old_function():'),
            DiffLine(line_type='-', content='    return "old"'),
            DiffLine(line_type=' ', content=''),
            DiffLine(line_type=' ', content='def remaining_function():'),
            DiffLine(line_type=' ', content='    return "remaining"')
        ]
        
        hunk = Hunk(old_start=1, old_count=5, new_start=1, new_count=3, lines=diff_lines)
        file_change = FileChange(filename='test.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        
        self.assertEqual(len(analyzed_changes), 1)
        analyzed_change = analyzed_changes[0]
        
        # Check structural changes
        self.assertEqual(len(analyzed_change.structural_changes), 1)
        structural_change = analyzed_change.structural_changes[0]
        
        self.assertEqual(structural_change.change_type, 'function_removed')
        self.assertEqual(structural_change.element_name, 'old_function')
        self.assertIn('Removed function', structural_change.description)
    
    def test_analyze_changes_function_modified(self):
        """Test analyzing function modification."""
        diff_lines = [
            DiffLine(line_type='-', content='def test_function():'),
            DiffLine(line_type='-', content='    return "old"'),
            DiffLine(line_type='+', content='def test_function():'),
            DiffLine(line_type='+', content='    return "new"'),
            DiffLine(line_type=' ', content='')
        ]
        
        hunk = Hunk(old_start=1, old_count=3, new_start=1, new_count=3, lines=diff_lines)
        file_change = FileChange(filename='test.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        
        self.assertEqual(len(analyzed_changes), 1)
        analyzed_change = analyzed_changes[0]
        
        # Check structural changes - should detect modification
        self.assertEqual(len(analyzed_change.structural_changes), 1)
        structural_change = analyzed_change.structural_changes[0]
        
        self.assertEqual(structural_change.change_type, 'function_modified')
        self.assertEqual(structural_change.element_name, 'test_function')
        self.assertIn('Modified function', structural_change.description)
    
    def test_analyze_changes_unknown_language(self):
        """Test analyzing changes for unknown language."""
        diff_lines = [
            DiffLine(line_type='+', content='some random content'),
            DiffLine(line_type='-', content='other content')
        ]
        
        hunk = Hunk(old_start=1, old_count=1, new_start=1, new_count=1, lines=diff_lines)
        file_change = FileChange(filename='unknown.xyz', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        
        self.assertEqual(len(analyzed_changes), 1)
        analyzed_change = analyzed_changes[0]
        
        # Should have unknown language and no structural changes
        self.assertEqual(analyzed_change.file_change.language, 'unknown')
        self.assertEqual(len(analyzed_change.structural_changes), 0)
    
    def test_analyze_changes_multiple_files(self):
        """Test analyzing changes for multiple files."""
        # Python file
        py_lines = [DiffLine(line_type='+', content='def new_func():')]
        py_hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=1, lines=py_lines)
        py_file = FileChange(filename='test.py', change_type='modified', hunks=[py_hunk])
        
        # JavaScript file
        js_lines = [DiffLine(line_type='+', content='class NewClass {')]
        js_hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=1, lines=js_lines)
        js_file = FileChange(filename='test.js', change_type='modified', hunks=[js_hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([py_file, js_file])
        
        self.assertEqual(len(analyzed_changes), 2)
        
        # Check Python file analysis
        py_analysis = analyzed_changes[0]
        self.assertEqual(py_analysis.file_change.language, 'python')
        self.assertEqual(len(py_analysis.structural_changes), 1)
        self.assertEqual(py_analysis.structural_changes[0].change_type, 'function_added')
        
        # Check JavaScript file analysis
        js_analysis = analyzed_changes[1]
        self.assertEqual(js_analysis.file_change.language, 'javascript')
        self.assertEqual(len(js_analysis.structural_changes), 1)
        self.assertEqual(js_analysis.structural_changes[0].change_type, 'class_added')


    def test_infer_change_purpose_feature_addition(self):
        """Test purpose inference for feature addition."""
        diff_lines = [
            DiffLine(line_type='+', content='def new_feature():'),
            DiffLine(line_type='+', content='    return "new functionality"'),
        ]
        
        hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=2, lines=diff_lines)
        file_change = FileChange(filename='features.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('Feature addition', analyzed_change.purpose_inference)
        self.assertGreater(analyzed_change.complexity_score, 0)
    
    def test_infer_change_purpose_bug_fix(self):
        """Test purpose inference for bug fix."""
        diff_lines = [
            DiffLine(line_type='-', content='def buggy_function():'),
            DiffLine(line_type='-', content='    return wrong_value'),
            DiffLine(line_type='+', content='def buggy_function():'),
            DiffLine(line_type='+', content='    return correct_value'),
        ]
        
        hunk = Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=diff_lines)
        file_change = FileChange(filename='utils.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('Bug fix or enhancement', analyzed_change.purpose_inference)
    
    def test_infer_change_purpose_test_addition(self):
        """Test purpose inference for test addition."""
        diff_lines = [
            DiffLine(line_type='+', content='def test_new_feature():'),
            DiffLine(line_type='+', content='    assert new_feature() == expected'),
        ]
        
        hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=2, lines=diff_lines)
        file_change = FileChange(filename='test_features.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('Test coverage improvement', analyzed_change.purpose_inference)
    
    def test_assess_change_impact_large_scale(self):
        """Test impact assessment for large-scale changes."""
        # Create a large change (simulate 150 lines changed)
        diff_lines = []
        for i in range(75):
            diff_lines.append(DiffLine(line_type='+', content=f'    line_{i} = "added"'))
            diff_lines.append(DiffLine(line_type='-', content=f'    old_line_{i} = "removed"'))
        
        hunk = Hunk(old_start=1, old_count=75, new_start=1, new_count=75, lines=diff_lines)
        file_change = FileChange(filename='large_module.py', change_type='modified', hunks=[hunk])
        file_change.lines_added = 75
        file_change.lines_removed = 75
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('Large-scale changes - high impact', analyzed_change.impact_assessment)
        self.assertGreater(analyzed_change.complexity_score, 5)
    
    def test_assess_change_impact_public_api(self):
        """Test impact assessment for public API changes."""
        diff_lines = [
            DiffLine(line_type='+', content='def public_function():'),
            DiffLine(line_type='+', content='    return "public"'),
            DiffLine(line_type='+', content='def _private_function():'),
            DiffLine(line_type='+', content='    return "private"'),
        ]
        
        hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=4, lines=diff_lines)
        file_change = FileChange(filename='api.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('Public API changes', analyzed_change.impact_assessment)
        self.assertIn('Internal implementation changes', analyzed_change.impact_assessment)
    
    def test_calculate_complexity_score_simple(self):
        """Test complexity score calculation for simple changes."""
        diff_lines = [
            DiffLine(line_type='+', content='print("hello")'),
        ]
        
        hunk = Hunk(old_start=1, old_count=0, new_start=1, new_count=1, lines=diff_lines)
        file_change = FileChange(filename='simple.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        # Should have low complexity score
        self.assertLessEqual(analyzed_change.complexity_score, 3)
    
    def test_calculate_complexity_score_complex(self):
        """Test complexity score calculation for complex changes."""
        diff_lines = [
            DiffLine(line_type='+', content='class ComplexClass:'),
            DiffLine(line_type='+', content='    def __init__(self):'),
            DiffLine(line_type='+', content='        self.data = {}'),
            DiffLine(line_type='-', content='class OldClass:'),
            DiffLine(line_type='-', content='    pass'),
        ]
        
        hunk = Hunk(old_start=1, old_count=2, new_start=1, new_count=3, lines=diff_lines)
        file_change = FileChange(filename='complex.py', change_type='modified', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        # Should have higher complexity score due to class changes
        self.assertGreater(analyzed_change.complexity_score, 2)
    
    def test_analyze_new_file_creation(self):
        """Test analyzing new file creation."""
        diff_lines = [
            DiffLine(line_type='+', content='def new_module_function():'),
            DiffLine(line_type='+', content='    return "new module"'),
        ]
        
        hunk = Hunk(old_start=0, old_count=0, new_start=1, new_count=2, lines=diff_lines)
        file_change = FileChange(filename='new_module.py', change_type='added', hunks=[hunk])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('New file creation', analyzed_change.purpose_inference)
        self.assertIn('New functionality introduced', analyzed_change.impact_assessment)
    
    def test_analyze_file_deletion(self):
        """Test analyzing file deletion."""
        file_change = FileChange(filename='deprecated.py', change_type='deleted', hunks=[])
        
        analyzed_changes = self.analyzer.analyze_changes([file_change])
        analyzed_change = analyzed_changes[0]
        
        self.assertIn('File removal', analyzed_change.purpose_inference)
        self.assertIn('Functionality removed', analyzed_change.impact_assessment)
        # Deletions should have higher complexity score
        self.assertGreaterEqual(analyzed_change.complexity_score, 2)

if __name__ == '__main__':
    unittest.main()