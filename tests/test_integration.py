"""
End-to-end integration tests for the code change summarizer.
"""

import unittest
import json
import tempfile
import os
import time
from code_summarizer.parser import DiffParser
from code_summarizer.analyzer import CodeAnalyzer
from code_summarizer.generator import SummaryGenerator
from code_summarizer.formatter import OutputFormatter
from code_summarizer.cli import main, process_diff, format_output
from unittest.mock import patch, MagicMock


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration test cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DiffParser()
        self.analyzer = CodeAnalyzer()
        self.generator = SummaryGenerator()
        self.formatter = OutputFormatter()
    
    def test_python_file_integration(self):
        """Test complete pipeline with Python file changes."""
        python_diff = """diff --git a/calculator.py b/calculator.py
index 1234567..abcdefg 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,8 +1,12 @@
+import math
+
 class Calculator:
     def __init__(self):
-        self.result = 0
+        self.result = 0.0
+        self.history = []
     
     def add(self, x, y):
-        return x + y
+        result = x + y
+        self.history.append(f"add({x}, {y}) = {result}")
+        return result
     
     def subtract(self, x, y):
         return x - y
@@ -10,3 +14,9 @@ class Calculator:
     def multiply(self, x, y):
         return x * y
     
+    def power(self, base, exponent):
+        result = math.pow(base, exponent)
+        self.history.append(f"power({base}, {exponent}) = {result}")
+        return result
+    
+    def get_history(self):
+        return self.history.copy()
"""
        
        # Test complete pipeline
        file_changes = self.parser.parse_diff(python_diff)
        self.assertEqual(len(file_changes), 1)
        self.assertEqual(file_changes[0].filename, 'calculator.py')
        self.assertEqual(file_changes[0].change_type, 'modified')
        
        analyzed_changes = self.analyzer.analyze_changes(file_changes)
        self.assertEqual(len(analyzed_changes), 1)
        self.assertEqual(analyzed_changes[0].file_change.language, 'python')
        self.assertGreater(len(analyzed_changes[0].structural_changes), 0)
        
        summary = self.generator.generate_summary(analyzed_changes)
        self.assertIsNotNone(summary)
        self.assertIn('1 file changed', summary.overview)
        self.assertEqual(len(summary.file_summaries), 1)
        self.assertEqual(summary.file_summaries[0].filename, 'calculator.py')
        
        # Test all output formats
        plain_output = self.formatter.format_output(summary, 'plain')
        self.assertIn('CODE CHANGE SUMMARY', plain_output)
        self.assertIn('calculator.py', plain_output)
        
        json_output = self.formatter.format_output(summary, 'json')
        json_data = json.loads(json_output)
        self.assertIn('overview', json_data)
        self.assertEqual(len(json_data['file_summaries']), 1)
        
        md_output = self.formatter.format_output(summary, 'markdown')
        self.assertIn('# Code Change Summary', md_output)
        self.assertIn('calculator.py', md_output)
    
    def test_javascript_file_integration(self):
        """Test complete pipeline with JavaScript file changes."""
        js_diff = """diff --git a/app.js b/app.js
index 1234567..abcdefg 100644
--- a/app.js
+++ b/app.js
@@ -1,10 +1,15 @@
+const express = require('express');
+const app = express();
+
 class UserManager {
     constructor() {
         this.users = [];
+        this.nextId = 1;
     }
     
     addUser(name, email) {
-        this.users.push({ name, email });
+        const user = { id: this.nextId++, name, email, createdAt: new Date() };
+        this.users.push(user);
+        return user;
     }
     
     getUsers() {
@@ -12,4 +17,12 @@ class UserManager {
     }
 }
 
+const userManager = new UserManager();
+
+app.get('/users', (req, res) => {
+    res.json(userManager.getUsers());
+});
+
+app.listen(3000, () => {
+    console.log('Server running on port 3000');
+});
 module.exports = UserManager;
"""
        
        # Test complete pipeline
        file_changes = self.parser.parse_diff(js_diff)
        self.assertEqual(len(file_changes), 1)
        self.assertEqual(file_changes[0].filename, 'app.js')
        
        analyzed_changes = self.analyzer.analyze_changes(file_changes)
        self.assertEqual(analyzed_changes[0].file_change.language, 'javascript')
        
        summary = self.generator.generate_summary(analyzed_changes)
        self.assertIn('1 file changed', summary.overview)
        self.assertEqual(summary.file_summaries[0].filename, 'app.js')
        
        # Test template formatting
        template = "File: {total_files}, Added: +{lines_added}, Removed: -{lines_removed}"
        template_output = self.formatter.apply_template(summary, template)
        self.assertIn('File: 1', template_output)
    
    def test_multiple_files_integration(self):
        """Test complete pipeline with multiple file changes."""
        multi_file_diff = """diff --git a/src/main.py b/src/main.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/main.py
@@ -0,0 +1,10 @@
+#!/usr/bin/env python3
+# Main application entry point.
+
+from .calculator import Calculator
+
+def main():
+    calc = Calculator()
+    print("Calculator started")
+
+if __name__ == "__main__":
+    main()
diff --git a/tests/test_calculator.py b/tests/test_calculator.py
new file mode 100644
index 0000000..abcdefg
--- /dev/null
+++ b/tests/test_calculator.py
@@ -0,0 +1,15 @@
+import unittest
+from src.calculator import Calculator
+
+class TestCalculator(unittest.TestCase):
+    def setUp(self):
+        self.calc = Calculator()
+    
+    def test_add(self):
+        result = self.calc.add(2, 3)
+        self.assertEqual(result, 5)
+    
+    def test_subtract(self):
+        result = self.calc.subtract(5, 3)
+        self.assertEqual(result, 2)
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,8 @@
 # Calculator Project
 
-A simple calculator implementation.
+A simple calculator implementation with the following features:
+
+- Basic arithmetic operations
+- History tracking
+- Command-line interface
+- Comprehensive test suite
"""
        
        # Test complete pipeline
        file_changes = self.parser.parse_diff(multi_file_diff)
        self.assertEqual(len(file_changes), 3)
        
        # Check file types
        filenames = [fc.filename for fc in file_changes]
        self.assertIn('src/main.py', filenames)
        self.assertIn('tests/test_calculator.py', filenames)
        self.assertIn('README.md', filenames)
        
        analyzed_changes = self.analyzer.analyze_changes(file_changes)
        self.assertEqual(len(analyzed_changes), 3)
        
        # Check language detection
        languages = [ac.file_change.language for ac in analyzed_changes]
        self.assertIn('python', languages)
        self.assertIn('markdown', languages)
        
        summary = self.generator.generate_summary(analyzed_changes)
        self.assertEqual(summary.statistics.total_files, 3)
        self.assertEqual(summary.statistics.files_added, 2)  # main.py and test_calculator.py are new
        self.assertEqual(summary.statistics.files_modified, 1)  # README.md is modified
        
        # Check recommendations
        recommendations_text = ' '.join(summary.recommendations)
        self.assertTrue(len(summary.recommendations) > 0)
    
    def test_large_diff_performance(self):
        """Test pipeline performance with large diff."""
        # Create a large diff with many files
        large_diff_parts = []
        
        for i in range(20):  # 20 files
            file_diff = f"""diff --git a/file_{i}.py b/file_{i}.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/file_{i}.py
@@ -0,0 +1,50 @@
+# File {i}
+class Class{i}:
+    def __init__(self):
+        self.value = {i}
+    
+    def method_{i}(self):
+        return self.value * {i}
+"""
            # Add 45 more lines to make it substantial
            for j in range(45):
                file_diff += f"+    # Line {j} in file {i}\n"
            
            large_diff_parts.append(file_diff)
        
        large_diff = '\n'.join(large_diff_parts)
        
        # Test that pipeline handles large input efficiently
        import time
        start_time = time.time()
        
        file_changes = self.parser.parse_diff(large_diff)
        analyzed_changes = self.analyzer.analyze_changes(file_changes)
        summary = self.generator.generate_summary(analyzed_changes)
        output = self.formatter.format_output(summary, 'json')
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(processing_time, 10.0, "Processing took too long")
        
        # Verify results
        self.assertEqual(len(file_changes), 20)
        self.assertEqual(summary.statistics.total_files, 20)
        self.assertIsInstance(output, str)
        
        # Verify JSON is valid
        json_data = json.loads(output)
        self.assertEqual(len(json_data['file_summaries']), 20)
    
    def test_edge_case_diffs(self):
        """Test pipeline with various edge case diffs."""
        edge_cases = [
            # Binary file diff
            """diff --git a/image.png b/image.png
index 1234567..abcdefg 100644
Binary files a/image.png and b/image.png differ
""",
            # File with unicode content
            """diff --git a/unicode.py b/unicode.py
index 1234567..abcdefg 100644
--- a/unicode.py
+++ b/unicode.py
@@ -1,3 +1,4 @@
 # -*- coding: utf-8 -*-
 def greet():
-    return "Hello"
+    return "Hello 世界"
+    # Added unicode support
""",
            # Very long line diff
            """diff --git a/long_line.py b/long_line.py
index 1234567..abcdefg 100644
--- a/long_line.py
+++ b/long_line.py
@@ -1,1 +1,2 @@
 short_line = "normal"
+""" + f"very_long_line = \"{'a' * 1000}\"\n",
            
            # Renamed file
            """diff --git a/old_name.py b/new_name.py
similarity index 100%
rename from old_name.py
rename to new_name.py
""",
            
            # Deleted file
            """diff --git a/deleted.py b/deleted.py
deleted file mode 100644
index 1234567..0000000
--- a/deleted.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def old_function():
-    return "deprecated"
-
-# This file is no longer needed
-print("Goodbye")
"""
        ]
        
        for i, diff in enumerate(edge_cases):
            with self.subTest(edge_case=i):
                # Should not raise exceptions
                file_changes = self.parser.parse_diff(diff)
                analyzed_changes = self.analyzer.analyze_changes(file_changes)
                summary = self.generator.generate_summary(analyzed_changes)
                
                # Should produce valid output in all formats
                plain_output = self.formatter.format_output(summary, 'plain')
                json_output = self.formatter.format_output(summary, 'json')
                md_output = self.formatter.format_output(summary, 'markdown')
                
                self.assertIsInstance(plain_output, str)
                self.assertIsInstance(json_output, str)
                self.assertIsInstance(md_output, str)
                
                # JSON should be valid
                json.loads(json_output)
    
    def test_cli_integration_with_file_input(self):
        """Test CLI integration with file input."""
        test_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Hello, World!")
     return "hello"
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.diff') as f:
            f.write(test_diff)
            temp_file = f.name
        
        try:
            # Test CLI with file input
            with patch('sys.argv', ['cli.py', '--input', temp_file, '--format', 'json', '--quiet']):
                with patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')):
                    result = main()
                    self.assertEqual(result, 0)
        finally:
            os.unlink(temp_file)
    
    def test_cli_integration_with_template(self):
        """Test CLI integration with custom template."""
        test_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Hello, World!")
     return "hello"
"""
        
        template = "Changed {total_files} files with +{lines_added}/-{lines_removed} lines"
        
        with patch('sys.argv', ['cli.py', '--diff', test_diff, '--template', template, '--quiet']):
            with patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')):
                result = main()
                self.assertEqual(result, 0)
    
    def test_error_recovery_integration(self):
        """Test that pipeline recovers gracefully from errors."""
        # Create a diff that might cause issues in some components
        problematic_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Hello, World!")
     return "hello"
"""
        
        # Mock one component to raise an exception
        with patch.object(self.analyzer, 'detect_language', side_effect=Exception("Mock error")):
            # Pipeline should still complete
            file_changes = self.parser.parse_diff(problematic_diff)
            analyzed_changes = self.analyzer.analyze_changes(file_changes)
            summary = self.generator.generate_summary(analyzed_changes)
            output = self.formatter.format_output(summary, 'plain')
            
            self.assertIsInstance(output, str)
            self.assertIn('CODE CHANGE SUMMARY', output)
    
    def test_comprehensive_language_support(self):
        """Test pipeline with various programming languages."""
        language_diffs = {
            'python': """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,1 +1,3 @@
+import os
 def test():
+    return os.getcwd()
-    pass
""",
            'javascript': """diff --git a/test.js b/test.js
--- a/test.js
+++ b/test.js
@@ -1,3 +1,5 @@
+const fs = require('fs');
 function test() {
-    return null;
+    return fs.readFileSync('test.txt');
 }
+module.exports = test;
""",
            'java': """diff --git a/Test.java b/Test.java
--- a/Test.java
+++ b/Test.java
@@ -1,5 +1,7 @@
+import java.util.List;
 public class Test {
     public void test() {
-        System.out.println("test");
+        List<String> items = new ArrayList<>();
+        System.out.println("test: " + items.size());
     }
 }
""",
            'typescript': """diff --git a/test.ts b/test.ts
--- a/test.ts
+++ b/test.ts
@@ -1,3 +1,5 @@
+interface User { name: string; }
 function test() {
-    return "test";
+    const user: User = { name: "test" };
+    return user.name;
 }
""",
            'go': """diff --git a/test.go b/test.go
--- a/test.go
+++ b/test.go
@@ -1,5 +1,7 @@
 package main
+import "fmt"
 func test() {
-    return
+    fmt.Println("test")
+    return
 }
""",
        }
        
        for language, diff in language_diffs.items():
            with self.subTest(language=language):
                file_changes = self.parser.parse_diff(diff)
                self.assertGreater(len(file_changes), 0)
                
                analyzed_changes = self.analyzer.analyze_changes(file_changes)
                self.assertEqual(analyzed_changes[0].file_change.language, language)
                
                summary = self.generator.generate_summary(analyzed_changes)
                self.assertIsNotNone(summary)
                
                # Should generate meaningful output
                output = self.formatter.format_output(summary, 'plain')
                self.assertIn(file_changes[0].filename, output)
    
    def test_full_pipeline_stress_test(self):
        """Stress test the full pipeline with complex scenarios."""
        # Create a complex diff with multiple file types and changes
        complex_diff = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,10 +1,15 @@
+#!/usr/bin/env python3
+import sys
+import logging
+
 class Application:
     def __init__(self):
-        self.name = "app"
+        self.name = "MyApp"
+        self.logger = logging.getLogger(__name__)
     
     def run(self):
-        print("Running")
+        self.logger.info("Application starting")
+        print(f"Running {self.name}")
     
     def stop(self):
         print("Stopping")
@@ -12,3 +17,8 @@ class Application:
 if __name__ == "__main__":
     app = Application()
     app.run()
+    
+    try:
+        app.stop()
+    except KeyboardInterrupt:
+        sys.exit(1)
diff --git a/config.json b/config.json
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/config.json
@@ -0,0 +1,8 @@
+{
+    "app_name": "MyApp",
+    "version": "1.0.0",
+    "debug": true,
+    "logging": {
+        "level": "INFO"
+    }
+}
diff --git a/old_config.ini b/old_config.ini
deleted file mode 100644
index 1234567..0000000
--- a/old_config.ini
+++ /dev/null
@@ -1,5 +0,0 @@
-[DEFAULT]
-app_name = app
-version = 0.1.0
-debug = false
-
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,5 +1,12 @@
 # My Application
 
-A simple application.
+A simple Python application with the following features:
+
+## Features
+- Configurable logging
+- JSON configuration
+- Error handling
+- Command-line interface
 
 ## Usage
-Run the application.
+```bash
+python src/main.py
+```
"""
        
        # Test complete pipeline
        start_time = time.time()
        
        file_changes = self.parser.parse_diff(complex_diff)
        analyzed_changes = self.analyzer.analyze_changes(file_changes)
        summary = self.generator.generate_summary(analyzed_changes)
        
        # Test all output formats
        plain_output = self.formatter.format_output(summary, 'plain')
        json_output = self.formatter.format_output(summary, 'json')
        md_output = self.formatter.format_output(summary, 'markdown')
        
        end_time = time.time()
        
        # Verify results
        self.assertEqual(len(file_changes), 4)
        self.assertEqual(summary.statistics.total_files, 4)
        self.assertEqual(summary.statistics.files_added, 1)  # config.json
        self.assertEqual(summary.statistics.files_modified, 2)  # main.py, README.md
        self.assertEqual(summary.statistics.files_deleted, 1)  # old_config.ini
        
        # Verify output quality
        self.assertIn('src/main.py', plain_output)
        self.assertIn('config.json', plain_output)
        
        json_data = json.loads(json_output)
        self.assertEqual(len(json_data['file_summaries']), 4)
        
        self.assertIn('# Code Change Summary', md_output)
        self.assertIn('## Statistics', md_output)
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 5.0)
        
        # Should have meaningful recommendations
        self.assertGreater(len(summary.recommendations), 0)


    def test_configuration_integration(self):
        """Test integration with configuration system."""
        from code_summarizer.config import Config
        
        # Create a test configuration
        test_config = Config()
        test_config.set('output_format', 'json')
        test_config.set('quiet', True)
        test_config.set('custom_templates', {
            'test_template': 'Files changed: {total_files}, Lines: +{lines_added}/-{lines_removed}'
        })
        
        # Test that configuration is accessible
        self.assertEqual(test_config.get('output_format'), 'json')
        self.assertEqual(test_config.get('quiet'), True)
        self.assertEqual(test_config.get_template('test_template'), 'Files changed: {total_files}, Lines: +{lines_added}/-{lines_removed}')
        
        # Test configuration validation
        self.assertTrue(test_config.validate_config())
        
        # Test invalid configuration
        test_config.set('output_format', 'invalid')
        with patch('builtins.print'):
            self.assertFalse(test_config.validate_config())
    
    def test_cli_with_configuration_options(self):
        """Test CLI with configuration-related options."""
        # Test create config option
        with patch('sys.argv', ['cli.py', '--create-config']):
            with patch('code_summarizer.config.config.create_sample_config') as mock_create:
                result = main()
                self.assertEqual(result, 0)
                mock_create.assert_called_once()
        
        # Test list templates option
        with patch('sys.argv', ['cli.py', '--list-templates']):
            with patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')):
                result = main()
                self.assertEqual(result, 0)
    
    def test_complete_workflow_with_all_features(self):
        """Test the complete workflow using all features."""
        # Create a comprehensive diff that exercises all features
        comprehensive_diff = """diff --git a/src/api.py b/src/api.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/api.py
@@ -0,0 +1,25 @@
+#!/usr/bin/env python3
+# API module for the application.
+
+import json
+import logging
+from typing import Dict, Any, Optional
+
+logger = logging.getLogger(__name__)
+
+class APIHandler:
+    def __init__(self, config: Dict[str, Any]):
+        self.config = config
+        self.logger = logger
+    
+    def process_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
+        \"\"\"Process an API request.\"\"\"
+        try:
+            self.logger.info(f"Processing request: {data}")
+            result = self._validate_and_process(data)
+            return {"status": "success", "data": result}
+        except Exception as e:
+            self.logger.error(f"Request processing failed: {e}")
+            return {"status": "error", "message": str(e)}
+    
+    def _validate_and_process(self, data: Dict[str, Any]) -> Any:
+        # Implementation would go here
+        return data
diff --git a/tests/test_api.py b/tests/test_api.py
new file mode 100644
index 0000000..abcdefg
--- /dev/null
+++ b/tests/test_api.py
@@ -0,0 +1,20 @@
+import unittest
+from unittest.mock import Mock, patch
+from src.api import APIHandler
+
+class TestAPIHandler(unittest.TestCase):
+    def setUp(self):
+        self.config = {"debug": True}
+        self.handler = APIHandler(self.config)
+    
+    def test_process_request_success(self):
+        data = {"key": "value"}
+        result = self.handler.process_request(data)
+        
+        self.assertEqual(result["status"], "success")
+        self.assertIn("data", result)
+    
+    @patch('src.api.logger')
+    def test_process_request_error(self, mock_logger):
+        # Test error handling
+        pass
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,8 +1,15 @@
 # My Application
 
-A simple application.
+A comprehensive Python application with API functionality.
+
+## New Features
+- RESTful API endpoints
+- Comprehensive error handling
+- Logging and monitoring
+- Full test coverage
 
 ## Installation
-pip install myapp
+```bash
+pip install myapp
+python -m pytest tests/
+```
"""
        
        # Test the complete pipeline with all components
        start_time = time.time()
        file_changes = self.parser.parse_diff(comprehensive_diff)
        self.assertEqual(len(file_changes), 3)
        
        # Verify language detection for all files
        analyzed_changes = self.analyzer.analyze_changes(file_changes)
        languages = [ac.file_change.language for ac in analyzed_changes]
        self.assertIn('python', languages)
        self.assertIn('markdown', languages)
        
        # Verify structural analysis
        total_structural_changes = sum(len(ac.structural_changes) for ac in analyzed_changes)
        self.assertGreater(total_structural_changes, 0)
        
        # Generate comprehensive summary
        summary = self.generator.generate_summary(analyzed_changes)
        
        # Verify summary quality
        self.assertEqual(summary.statistics.total_files, 3)
        self.assertEqual(summary.statistics.files_added, 2)
        self.assertEqual(summary.statistics.files_modified, 1)
        self.assertGreater(len(summary.recommendations), 0)
        
        # Test all output formats
        formats = ['plain', 'markdown', 'json']
        for format_type in formats:
            with self.subTest(format=format_type):
                output = self.formatter.format_output(summary, format_type)
                self.assertIsInstance(output, str)
                self.assertGreater(len(output), 0)
                
                if format_type == 'json':
                    # Verify valid JSON
                    json_data = json.loads(output)
                    self.assertIn('overview', json_data)
                    self.assertIn('statistics', json_data)
        
        # Test custom template
        template = "Summary: {overview}\nFiles: {total_files}\nComplexity: High" 
        template_output = self.formatter.apply_template(summary, template)
        self.assertIn('Summary:', template_output)
        self.assertIn('Files: 3', template_output)
        self.assertIn('Complexity: High', template_output)
        
        # Verify performance (should complete quickly)
        self.assertLess(time.time() - start_time, 2.0)
    
    def test_package_installation_simulation(self):
        """Simulate package installation and usage."""
        # Test that all modules can be imported
        try:
            from code_summarizer import parser, analyzer, generator, formatter, cli, config
            from code_summarizer.models import FileChange, Summary, AnalyzedChange
            
            # Test that main classes can be instantiated
            diff_parser = parser.DiffParser()
            code_analyzer = analyzer.CodeAnalyzer()
            summary_generator = generator.SummaryGenerator()
            output_formatter = formatter.OutputFormatter()
            
            # Test that they have expected methods
            self.assertTrue(hasattr(diff_parser, 'parse_diff'))
            self.assertTrue(hasattr(code_analyzer, 'analyze_changes'))
            self.assertTrue(hasattr(summary_generator, 'generate_summary'))
            self.assertTrue(hasattr(output_formatter, 'format_output'))
            
            # Test configuration
            self.assertTrue(hasattr(config.config, 'get'))
            self.assertTrue(hasattr(config.config, 'validate_config'))
            
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_entry_point_functionality(self):
        """Test that entry points work correctly."""
        # Test CLI main function
        from code_summarizer.cli import main
        
        # Test with help option (should exit cleanly)
        with patch('sys.argv', ['code-summarizer', '--help']):
            with self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 0)
        
        # Test with version option
        with patch('sys.argv', ['code-summarizer', '--version']):
            with self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 0)


if __name__ == '__main__':
    unittest.main()