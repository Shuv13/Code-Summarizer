"""
Data models for the code change summarizer.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DiffLine:
    """Represents a single line in a diff."""
    line_type: str  # '+', '-', ' '
    content: str
    line_number: Optional[int] = None


@dataclass
class Hunk:
    """Represents a hunk (section of changes) in a diff."""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[DiffLine]
    context: str = ""


@dataclass
class FileChange:
    """Represents changes to a single file."""
    filename: str
    change_type: str  # 'modified', 'added', 'deleted', 'renamed'
    old_filename: Optional[str] = None
    hunks: List[Hunk] = None
    language: str = "unknown"
    lines_added: int = 0
    lines_removed: int = 0
    
    def __post_init__(self):
        if self.hunks is None:
            self.hunks = []


@dataclass
class StructuralChange:
    """Represents a structural change in code (function, class, etc.)."""
    change_type: str  # 'function_added', 'class_modified', 'import_changed'
    element_name: str
    description: str
    before: Optional[str] = None
    after: Optional[str] = None


@dataclass
class AnalyzedChange:
    """Represents an analyzed file change with inferred context."""
    file_change: FileChange
    structural_changes: List[StructuralChange]
    purpose_inference: str = ""
    impact_assessment: str = ""
    complexity_score: int = 0
    
    def __post_init__(self):
        if self.structural_changes is None:
            self.structural_changes = []


@dataclass
class ChangeStatistics:
    """Statistics about the changes."""
    total_files: int = 0
    files_added: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    total_lines_added: int = 0
    total_lines_removed: int = 0


@dataclass
class FileSummary:
    """Summary of changes for a single file."""
    filename: str
    summary: str
    key_changes: List[str]
    
    def __post_init__(self):
        if self.key_changes is None:
            self.key_changes = []


@dataclass
class Summary:
    """Complete summary of all changes."""
    overview: str
    file_summaries: List[FileSummary] = None
    statistics: ChangeStatistics = None
    key_changes: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.file_summaries is None:
            self.file_summaries = []
        if self.key_changes is None:
            self.key_changes = []
        if self.recommendations is None:
            self.recommendations = []
        if self.statistics is None:
            self.statistics = ChangeStatistics()