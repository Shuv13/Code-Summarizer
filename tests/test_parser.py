"""
Tests for git diff parser.
"""

import unittest
from code_summarizer.parser import DiffParser
from code_summarizer.models import FileChange, Hunk, DiffLine


class TestDiffParser(unittest.TestCase):
    """Test cases for DiffParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DiffParser()
    
    def test_parse_simple_diff(self):
        """Test parsing a simple git diff."""
        diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Hello, World!")
     return "hello"
 
"""
        file_changes = self.parser.parse_diff(diff_text)
        
        self.assertEqual(len(file_changes), 1)
        file_change = file_changes[0]
        
        self.assertEqual(file_change.filename, 'test.py')
        self.assertEqual(file_change.change_type, 'modified')
        self.assertEqual(file_change.lines_added, 1)
        self.assertEqual(file_change.lines_removed, 0)
        self.assertEqual(len(file_change.hunks), 1)
    
    def test_parse_new_file(self):
        """Test parsing a new file diff."""
        diff_text = """diff --git a/new_file.py b/new_file.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,3 @@
+def new_function():
+    return "new"
+
"""
        file_changes = self.parser.parse_diff(diff_text)
        
        self.assertEqual(len(file_changes), 1)
        file_change = file_changes[0]
        
        self.assertEqual(file_change.filename, 'new_file.py')
        self.assertEqual(file_change.change_type, 'added')
        self.assertEqual(file_change.lines_added, 3)
        self.assertEqual(file_change.lines_removed, 0)
    
    def test_parse_deleted_file(self):
        """Test parsing a deleted file diff."""
        diff_text = """diff --git a/old_file.py b/old_file.py
deleted file mode 100644
index 1234567..0000000
--- a/old_file.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def old_function():
-    return "old"
-
"""
        file_changes = self.parser.parse_diff(diff_text)
        
        self.assertEqual(len(file_changes), 1)
        file_change = file_changes[0]
        
        self.assertEqual(file_change.filename, 'old_file.py')
        self.assertEqual(file_change.change_type, 'deleted')
        self.assertEqual(file_change.lines_added, 0)
        self.assertEqual(file_change.lines_removed, 3)
    
    def test_parse_renamed_file(self):
        """Test parsing a renamed file diff."""
        diff_text = """diff --git a/old_name.py b/new_name.py
similarity index 100%
rename from old_name.py
rename to new_name.py
"""
        file_changes = self.parser.parse_diff(diff_text)
        
        self.assertEqual(len(file_changes), 1)
        file_change = file_changes[0]
        
        self.assertEqual(file_change.filename, 'new_name.py')
        self.assertEqual(file_change.old_filename, 'old_name.py')
        self.assertEqual(file_change.change_type, 'renamed')
    
    def test_parse_multiple_files(self):
        """Test parsing diff with multiple files."""
        diff_text = """diff --git a/file1.py b/file1.py
index 1234567..abcdefg 100644
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,3 @@
 def func1():
+    print("added line")
     return 1
diff --git a/file2.py b/file2.py
index 2345678..bcdefgh 100644
--- a/file2.py
+++ b/file2.py
@@ -1,3 +1,2 @@
 def func2():
-    print("removed line")
     return 2
"""
        file_changes = self.parser.parse_diff(diff_text)
        
        self.assertEqual(len(file_changes), 2)
        
        # Check first file
        file1 = file_changes[0]
        self.assertEqual(file1.filename, 'file1.py')
        self.assertEqual(file1.lines_added, 1)
        self.assertEqual(file1.lines_removed, 0)
        
        # Check second file
        file2 = file_changes[1]
        self.assertEqual(file2.filename, 'file2.py')
        self.assertEqual(file2.lines_added, 0)
        self.assertEqual(file2.lines_removed, 1)
    
    def test_parse_hunk_header(self):
        """Test parsing hunk headers."""
        diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -10,5 +10,6 @@ class TestClass:
 def method():
     pass
+    # Added comment
 
 def another():
     return True
"""
        file_changes = self.parser.parse_diff(diff_text)
        
        self.assertEqual(len(file_changes), 1)
        hunk = file_changes[0].hunks[0]
        
        self.assertEqual(hunk.old_start, 10)
        self.assertEqual(hunk.old_count, 5)
        self.assertEqual(hunk.new_start, 10)
        self.assertEqual(hunk.new_count, 6)
        self.assertEqual(hunk.context, "class TestClass:")
    
    def test_extract_hunks(self):
        """Test extracting hunks from diff section."""
        diff_section = """@@ -1,3 +1,4 @@
 def hello():
+    print("Hello, World!")
     return "hello"
 
@@ -10,2 +11,3 @@
 def goodbye():
+    print("Goodbye!")
     return "bye"
"""
        hunks = self.parser.extract_hunks(diff_section)
        
        self.assertEqual(len(hunks), 2)
        
        # Check first hunk
        hunk1 = hunks[0]
        self.assertEqual(hunk1.old_start, 1)
        self.assertEqual(hunk1.new_start, 1)
        self.assertEqual(len(hunk1.lines), 4)
        
        # Check second hunk
        hunk2 = hunks[1]
        self.assertEqual(hunk2.old_start, 10)
        self.assertEqual(hunk2.new_start, 11)
        self.assertEqual(len(hunk2.lines), 4)  # includes empty line
    
    def test_empty_diff(self):
        """Test parsing empty diff."""
        file_changes = self.parser.parse_diff("")
        self.assertEqual(len(file_changes), 0)
        
        file_changes = self.parser.parse_diff("   \n  \n  ")
        self.assertEqual(len(file_changes), 0)


if __name__ == '__main__':
    unittest.main()