"""
Git diff parser module.
"""

import re
import logging
from typing import List, Optional, Tuple
from .models import FileChange, Hunk, DiffLine

# Set up logging
logger = logging.getLogger(__name__)


class DiffParser:
    """Parses git diff format and extracts file changes."""
    
    def __init__(self):
        # Regex patterns for parsing git diff
        self.file_header_pattern = re.compile(r'^diff --git a/(.*?) b/(.*?)$')
        self.old_file_pattern = re.compile(r'^--- a/(.*)$|^--- /dev/null$')
        self.new_file_pattern = re.compile(r'^\+\+\+ b/(.*)$|^\+\+\+ /dev/null$')
        self.hunk_header_pattern = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$')
        self.rename_pattern = re.compile(r'^rename from (.*)$')
        self.rename_to_pattern = re.compile(r'^rename to (.*)$')
    
    def parse_diff(self, diff_text: str) -> List[FileChange]:
        """Parse git diff text and return list of file changes."""
        if not diff_text or not diff_text.strip():
            logger.debug("Empty diff text provided")
            return []
        
        try:
            lines = diff_text.split('\n')
            file_changes = []
            current_file = None
            i = 0
            
            logger.debug(f"Parsing diff with {len(lines)} lines")
            
            while i < len(lines):
                line = lines[i]
                
                # Check for file header
                if line.startswith('diff --git'):
                    if current_file:
                        file_changes.append(current_file)
                    
                    current_file = self._parse_file_header(line)
                    i += 1
                    
                    # Parse additional file metadata
                    while i < len(lines) and not lines[i].startswith('@@') and not lines[i].startswith('diff --git'):
                        if lines[i].startswith('rename from'):
                            match = self.rename_pattern.match(lines[i])
                            if match:
                                current_file.old_filename = match.group(1)
                                current_file.change_type = 'renamed'
                        elif lines[i].startswith('rename to'):
                            match = self.rename_to_pattern.match(lines[i])
                            if match:
                                current_file.filename = match.group(1)
                        elif lines[i].startswith('new file mode'):
                            current_file.change_type = 'added'
                        elif lines[i].startswith('deleted file mode'):
                            current_file.change_type = 'deleted'
                        elif lines[i].startswith('---') or lines[i].startswith('+++'):
                            pass  # Skip these for now
                        i += 1
                    continue
                
                # Check for hunk header
                elif line.startswith('@@') and current_file:
                    try:
                        hunk, lines_processed = self._parse_hunk(lines[i:])
                        if hunk:
                            current_file.hunks.append(hunk)
                            current_file.lines_added += sum(1 for l in hunk.lines if l.line_type == '+')
                            current_file.lines_removed += sum(1 for l in hunk.lines if l.line_type == '-')
                        i += lines_processed
                    except Exception as e:
                        logger.warning(f"Failed to parse hunk at line {i}: {e}")
                        i += 1
                    continue
                
                i += 1
            
            # Add the last file if exists
            if current_file:
                file_changes.append(current_file)
            
            logger.debug(f"Successfully parsed {len(file_changes)} file changes")
            return file_changes
            
        except Exception as e:
            logger.error(f"Error parsing diff: {e}")
            # Return empty list instead of raising exception for robustness
            return []
    
    def _parse_file_header(self, line: str) -> FileChange:
        """Parse file header line and create FileChange object."""
        try:
            match = self.file_header_pattern.match(line)
            if match:
                old_file = match.group(1)
                new_file = match.group(2)
                
                # Determine change type and filename
                if old_file == new_file:
                    return FileChange(filename=new_file, change_type='modified')
                else:
                    return FileChange(filename=new_file, change_type='renamed', old_filename=old_file)
            
            # Fallback for malformed headers
            logger.warning(f"Could not parse file header: {line}")
            return FileChange(filename='unknown', change_type='modified')
            
        except Exception as e:
            logger.error(f"Error parsing file header '{line}': {e}")
            return FileChange(filename='unknown', change_type='modified')
    
    def _parse_hunk(self, lines: List[str]) -> Tuple[Optional[Hunk], int]:
        """Parse a hunk from lines starting with hunk header."""
        if not lines or not lines[0].startswith('@@'):
            return None, 0
        
        try:
            # Parse hunk header
            match = self.hunk_header_pattern.match(lines[0])
            if not match:
                logger.warning(f"Invalid hunk header: {lines[0]}")
                return None, 1
            
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) else 1
            context = match.group(5).strip() if match.group(5) else ""
            
            # Parse hunk lines
            hunk_lines = []
            i = 1
            old_line_num = old_start
            new_line_num = new_start
            
            while i < len(lines):
                line = lines[i]
                
                # Stop if we hit another hunk or file
                if line.startswith('@@') or line.startswith('diff --git'):
                    break
                
                # Parse diff line
                try:
                    if line.startswith('+'):
                        diff_line = DiffLine(line_type='+', content=line[1:], line_number=new_line_num)
                        new_line_num += 1
                    elif line.startswith('-'):
                        diff_line = DiffLine(line_type='-', content=line[1:], line_number=old_line_num)
                        old_line_num += 1
                    elif line.startswith(' '):
                        diff_line = DiffLine(line_type=' ', content=line[1:], line_number=old_line_num)
                        old_line_num += 1
                        new_line_num += 1
                    else:
                        # Handle lines that don't start with +, -, or space (context lines)
                        diff_line = DiffLine(line_type=' ', content=line, line_number=old_line_num)
                        old_line_num += 1
                        new_line_num += 1
                    
                    hunk_lines.append(diff_line)
                except Exception as e:
                    logger.warning(f"Error parsing diff line '{line}': {e}")
                    # Continue processing other lines
                
                i += 1
            
            hunk = Hunk(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
                lines=hunk_lines,
                context=context
            )
            
            return hunk, i
            
        except Exception as e:
            logger.error(f"Error parsing hunk: {e}")
            return None, 1
    
    def extract_hunks(self, diff_section: str) -> List[Hunk]:
        """Extract hunks from a diff section."""
        if not diff_section or not diff_section.strip():
            return []
        
        try:
            lines = diff_section.split('\n')
            hunks = []
            i = 0
            
            while i < len(lines):
                if lines[i].startswith('@@'):
                    hunk, lines_processed = self._parse_hunk(lines[i:])
                    if hunk:
                        hunks.append(hunk)
                    i += lines_processed
                else:
                    i += 1
            
            return hunks
            
        except Exception as e:
            logger.error(f"Error extracting hunks: {e}")
            return []
    
    def validate_diff_format(self, diff_text: str) -> bool:
        """Validate if the input looks like a git diff."""
        if not diff_text or not diff_text.strip():
            return False
        
        # Check for basic git diff markers
        has_diff_header = 'diff --git' in diff_text
        has_file_markers = ('---' in diff_text and '+++' in diff_text)
        has_hunk_markers = '@@' in diff_text
        
        return has_diff_header or (has_file_markers and has_hunk_markers)