"""
Code analysis module for detecting language and structure.
"""

import re
import logging
from typing import List, Dict, Set, Optional
from .models import FileChange, AnalyzedChange, StructuralChange

# Set up logging
logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes code structure and infers change meanings."""
    
    def __init__(self):
        # Language detection mappings
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sh': 'bash',
            '.sql': 'sql',
            '.r': 'r',
            '.m': 'matlab',
            '.pl': 'perl'
        }
        
        # Language-specific patterns for structural elements
        self.language_patterns = {
            'python': {
                'function': re.compile(r'^\s*def\s+(\w+)\s*\(([^)]*)\):'),
                'class': re.compile(r'^\s*class\s+(\w+)(?:\([^)]*\))?:'),
                'import': re.compile(r'^\s*(?:from\s+[\w.]+\s+)?import\s+([\w.,\s*]+)'),
                'variable': re.compile(r'^\s*(\w+)\s*='),
                'decorator': re.compile(r'^\s*@(\w+)')
            },
            'javascript': {
                'function': re.compile(r'^\s*(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>))'),
                'class': re.compile(r'^\s*class\s+(\w+)'),
                'import': re.compile(r'^\s*import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"][^\'"]+[\'"]'),
                'variable': re.compile(r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?!function|\([^)]*\)\s*=>)[^;]+;?'),
                'method': re.compile(r'^\s*(\w+)\s*\([^)]*\)\s*{')
            },
            'typescript': {
                'function': re.compile(r'^\s*(?:function\s+(\w+)|(?:const|let)\s+(\w+)\s*:\s*\([^)]*\)\s*=>)'),
                'class': re.compile(r'^\s*(?:export\s+)?class\s+(\w+)'),
                'interface': re.compile(r'^\s*(?:export\s+)?interface\s+(\w+)'),
                'import': re.compile(r'^\s*import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"][^\'"]+[\'"]'),
                'type': re.compile(r'^\s*(?:export\s+)?type\s+(\w+)')
            },
            'java': {
                'class': re.compile(r'^\s*(?:public\s+)?class\s+(\w+)'),
                'method': re.compile(r'^\s*(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\('),
                'import': re.compile(r'^\s*import\s+([\w.]+);'),
                'variable': re.compile(r'^\s*(?:private|public|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*[=;]')
            },
            'go': {
                'function': re.compile(r'^\s*func\s+(?:\([^)]*\)\s+)?(\w+)\s*\('),
                'struct': re.compile(r'^\s*type\s+(\w+)\s+struct'),
                'interface': re.compile(r'^\s*type\s+(\w+)\s+interface'),
                'import': re.compile(r'^\s*import\s+(?:"[^"]+"|`[^`]+`)'),
                'variable': re.compile(r'^\s*(?:var\s+)?(\w+)\s*:?=')
            },
            'rust': {
                'function': re.compile(r'^\s*(?:pub\s+)?fn\s+(\w+)\s*\('),
                'struct': re.compile(r'^\s*(?:pub\s+)?struct\s+(\w+)'),
                'enum': re.compile(r'^\s*(?:pub\s+)?enum\s+(\w+)'),
                'trait': re.compile(r'^\s*(?:pub\s+)?trait\s+(\w+)'),
                'impl': re.compile(r'^\s*impl(?:\s*<[^>]*>)?\s+(?:(\w+)|(\w+)\s+for\s+(\w+))'),
                'use': re.compile(r'^\s*use\s+([\w::{},\s*]+);')
            }
        }
    
    def analyze_changes(self, file_changes: List[FileChange]) -> List[AnalyzedChange]:
        """Analyze file changes and return analyzed changes with context."""
        if not file_changes:
            logger.debug("No file changes provided for analysis")
            return []
        
        analyzed_changes = []
        
        for file_change in file_changes:
            try:
                # Validate file change
                if not file_change.filename:
                    logger.warning("File change has no filename, skipping")
                    continue
                
                # Detect language for the file
                language = self.detect_language(file_change.filename)
                file_change.language = language
                logger.debug(f"Detected language '{language}' for file '{file_change.filename}'")
                
                # Analyze structural changes
                structural_changes = self._analyze_structural_changes(file_change, language)
                
                # Infer purpose and assess impact
                purpose_inference = self._infer_change_purpose(file_change, structural_changes)
                impact_assessment = self._assess_change_impact(file_change, structural_changes)
                complexity_score = self._calculate_complexity_score(file_change, structural_changes)
                
                # Create analyzed change
                analyzed_change = AnalyzedChange(
                    file_change=file_change,
                    structural_changes=structural_changes,
                    purpose_inference=purpose_inference,
                    impact_assessment=impact_assessment,
                    complexity_score=complexity_score
                )
                
                analyzed_changes.append(analyzed_change)
                
            except Exception as e:
                logger.error(f"Error analyzing file change '{file_change.filename}': {e}")
                # Create a minimal analyzed change to avoid breaking the pipeline
                analyzed_change = AnalyzedChange(
                    file_change=file_change,
                    structural_changes=[],
                    purpose_inference="Analysis failed",
                    impact_assessment="Unable to assess impact",
                    complexity_score=0
                )
                analyzed_changes.append(analyzed_change)
        
        logger.debug(f"Successfully analyzed {len(analyzed_changes)} file changes")
        return analyzed_changes
    
    def detect_language(self, filename: str) -> str:
        """Detect programming language based on filename."""
        # Special cases for common files without extensions
        filename_lower = filename.lower()
        if filename_lower in ['makefile', 'dockerfile']:
            return filename_lower
        elif filename_lower.startswith('readme'):
            return 'markdown'
        elif filename_lower in ['package.json', 'tsconfig.json']:
            return 'json'
        elif filename_lower in ['.gitignore', '.env']:
            return 'config'
        
        # Get file extension
        if '.' not in filename:
            return 'unknown'
        
        extension = '.' + filename.split('.')[-1].lower()
        
        # Check direct extension mapping
        if extension in self.language_extensions:
            return self.language_extensions[extension]
        
        return 'unknown'
    
    def parse_code_structure(self, code: str, language: str) -> Dict[str, List[Dict]]:
        """Parse code structure for the given language."""
        if language not in self.language_patterns:
            return {}
        
        patterns = self.language_patterns[language]
        structure = {}
        
        lines = code.split('\n')
        
        for pattern_type, pattern in patterns.items():
            matches = []
            for line_num, line in enumerate(lines, 1):
                match = pattern.match(line)
                if match:
                    # Handle multiple capture groups (e.g., JavaScript functions)
                    name = 'anonymous'
                    for i in range(1, len(match.groups()) + 1):
                        if match.group(i):
                            name = match.group(i)
                            break
                    
                    match_info = {
                        'name': name,
                        'line': line_num,
                        'content': line.strip()
                    }
                    
                    # Add additional info for functions
                    if pattern_type == 'function' and len(match.groups()) > 1:
                        match_info['parameters'] = match.group(2) if match.group(2) else ''
                    
                    matches.append(match_info)
            
            if matches:
                structure[pattern_type] = matches
        
        return structure
    
    def _analyze_structural_changes(self, file_change: FileChange, language: str) -> List[StructuralChange]:
        """Analyze structural changes in a file."""
        structural_changes = []
        
        if language == 'unknown' or not file_change.hunks:
            return structural_changes
        
        # Collect added and removed lines
        added_lines = []
        removed_lines = []
        
        for hunk in file_change.hunks:
            for line in hunk.lines:
                if line.line_type == '+':
                    added_lines.append(line.content)
                elif line.line_type == '-':
                    removed_lines.append(line.content)
        
        # Analyze added code
        if added_lines:
            added_code = '\n'.join(added_lines)
            added_structure = self.parse_code_structure(added_code, language)
            
            for element_type, elements in added_structure.items():
                for element in elements:
                    structural_change = StructuralChange(
                        change_type=f'{element_type}_added',
                        element_name=element['name'],
                        description=f"Added {element_type} '{element['name']}'",
                        after=element['content']
                    )
                    structural_changes.append(structural_change)
        
        # Analyze removed code
        if removed_lines:
            removed_code = '\n'.join(removed_lines)
            removed_structure = self.parse_code_structure(removed_code, language)
            
            for element_type, elements in removed_structure.items():
                for element in elements:
                    structural_change = StructuralChange(
                        change_type=f'{element_type}_removed',
                        element_name=element['name'],
                        description=f"Removed {element_type} '{element['name']}'",
                        before=element['content']
                    )
                    structural_changes.append(structural_change)
        
        # Detect modifications (simplified - could be enhanced)
        self._detect_modifications(structural_changes, added_lines, removed_lines, language)
        
        return structural_changes
    
    def _detect_modifications(self, structural_changes: List[StructuralChange], 
                            added_lines: List[str], removed_lines: List[str], language: str):
        """Detect modifications by comparing added and removed lines."""
        if language not in self.language_patterns:
            return
        
        patterns = self.language_patterns[language]
        
        # Simple heuristic: if we have similar function/class names in both added and removed,
        # it might be a modification
        for pattern_type, pattern in patterns.items():
            added_names = set()
            removed_names = set()
            
            for line in added_lines:
                match = pattern.match(line)
                if match and match.group(1):
                    added_names.add(match.group(1))
            
            for line in removed_lines:
                match = pattern.match(line)
                if match and match.group(1):
                    removed_names.add(match.group(1))
            
            # Find common names (potential modifications)
            common_names = added_names.intersection(removed_names)
            
            for name in common_names:
                # Remove the individual add/remove entries for this name
                structural_changes[:] = [sc for sc in structural_changes 
                                       if not (sc.element_name == name and 
                                             sc.change_type in [f'{pattern_type}_added', f'{pattern_type}_removed'])]
                
                # Add modification entry
                structural_change = StructuralChange(
                    change_type=f'{pattern_type}_modified',
                    element_name=name,
                    description=f"Modified {pattern_type} '{name}'"
                )
                structural_changes.append(structural_change)    

    def _infer_change_purpose(self, file_change: FileChange, structural_changes: List[StructuralChange]) -> str:
        """Infer the purpose of changes based on patterns and context."""
        purposes = []
        
        # Analyze file-level changes
        if file_change.change_type == 'added':
            purposes.append("New file creation")
        elif file_change.change_type == 'deleted':
            purposes.append("File removal")
        elif file_change.change_type == 'renamed':
            purposes.append("File reorganization")
        
        # Analyze structural changes
        if structural_changes:
            change_types = [sc.change_type for sc in structural_changes]
            
            # Function-related changes
            function_added = any('function_added' in ct for ct in change_types)
            function_removed = any('function_removed' in ct for ct in change_types)
            function_modified = any('function_modified' in ct for ct in change_types)
            
            if function_added and not function_removed:
                purposes.append("Feature addition")
            elif function_removed and not function_added:
                purposes.append("Code cleanup or deprecation")
            elif function_modified:
                purposes.append("Bug fix or enhancement")
            
            # Class-related changes
            class_added = any('class_added' in ct for ct in change_types)
            class_removed = any('class_removed' in ct for ct in change_types)
            class_modified = any('class_modified' in ct for ct in change_types)
            
            if class_added:
                purposes.append("New component or module")
            elif class_removed:
                purposes.append("Architecture refactoring")
            elif class_modified:
                purposes.append("Class enhancement")
            
            # Import changes
            import_added = any('import_added' in ct for ct in change_types)
            import_removed = any('import_removed' in ct for ct in change_types)
            
            if import_added:
                purposes.append("Dependency addition")
            elif import_removed:
                purposes.append("Dependency cleanup")
        
        # Analyze content patterns for additional context
        all_added_content = []
        all_removed_content = []
        
        for hunk in file_change.hunks:
            for line in hunk.lines:
                if line.line_type == '+':
                    all_added_content.append(line.content.lower())
                elif line.line_type == '-':
                    all_removed_content.append(line.content.lower())
        
        added_text = ' '.join(all_added_content)
        removed_text = ' '.join(all_removed_content)
        
        # Look for common patterns
        if any(keyword in added_text for keyword in ['test', 'spec', 'assert', 'expect']):
            purposes.append("Test coverage improvement")
        
        if any(keyword in added_text for keyword in ['log', 'debug', 'print', 'console']):
            purposes.append("Debugging or logging enhancement")
        
        if any(keyword in added_text for keyword in ['error', 'exception', 'try', 'catch']):
            purposes.append("Error handling improvement")
        
        if any(keyword in added_text for keyword in ['todo', 'fixme', 'hack']):
            purposes.append("Technical debt or temporary fix")
        
        if any(keyword in removed_text for keyword in ['todo', 'fixme', 'hack']):
            purposes.append("Technical debt resolution")
        
        # Documentation changes
        if file_change.language in ['markdown', 'unknown'] and 'readme' in file_change.filename.lower():
            purposes.append("Documentation update")
        
        if any(keyword in added_text for keyword in ['"""', "'''", '//', '/*', '#']):
            purposes.append("Documentation improvement")
        
        return "; ".join(purposes) if purposes else "Code modification"
    
    def _assess_change_impact(self, file_change: FileChange, structural_changes: List[StructuralChange]) -> str:
        """Assess the potential impact of changes."""
        impact_factors = []
        
        # File-level impact
        if file_change.change_type == 'added':
            impact_factors.append("New functionality introduced")
        elif file_change.change_type == 'deleted':
            impact_factors.append("Functionality removed - may break dependencies")
        elif file_change.change_type == 'renamed':
            impact_factors.append("Import paths may need updating")
        
        # Scale of changes
        total_lines_changed = file_change.lines_added + file_change.lines_removed
        if total_lines_changed > 100:
            impact_factors.append("Large-scale changes - high impact")
        elif total_lines_changed > 20:
            impact_factors.append("Medium-scale changes - moderate impact")
        else:
            impact_factors.append("Small-scale changes - low impact")
        
        # Structural impact
        if structural_changes:
            public_changes = []
            private_changes = []
            
            for sc in structural_changes:
                # Heuristic: assume functions/classes starting with _ are private
                if sc.element_name.startswith('_'):
                    private_changes.append(sc)
                else:
                    public_changes.append(sc)
            
            if public_changes:
                impact_factors.append(f"Public API changes ({len(public_changes)} elements) - may affect external code")
            
            if private_changes:
                impact_factors.append(f"Internal implementation changes ({len(private_changes)} elements)")
            
            # Specific structural impacts
            if any('class' in sc.change_type for sc in structural_changes):
                impact_factors.append("Class structure changes - may affect inheritance")
            
            if any('import' in sc.change_type for sc in structural_changes):
                impact_factors.append("Dependency changes - may affect build process")
        
        # File type specific impacts
        if file_change.filename.endswith(('.py', '.js', '.ts', '.java')):
            impact_factors.append("Core application code - runtime impact")
        elif file_change.filename.endswith(('.test.py', '.spec.js', '.test.ts')):
            impact_factors.append("Test code - affects test coverage")
        elif file_change.filename.endswith(('.json', '.yaml', '.yml', '.xml')):
            impact_factors.append("Configuration changes - may affect deployment")
        elif file_change.filename.endswith(('.md', '.txt', '.rst')):
            impact_factors.append("Documentation changes - no runtime impact")
        
        return "; ".join(impact_factors) if impact_factors else "Minimal impact expected"
    
    def _calculate_complexity_score(self, file_change: FileChange, structural_changes: List[StructuralChange]) -> int:
        """Calculate a complexity score for the changes (0-10 scale)."""
        score = 0
        
        # Base score from lines changed
        total_lines = file_change.lines_added + file_change.lines_removed
        if total_lines > 200:
            score += 4
        elif total_lines > 100:
            score += 3
        elif total_lines > 50:
            score += 2
        elif total_lines > 10:
            score += 1
        
        # Structural complexity
        if structural_changes:
            # More points for more structural changes
            score += min(len(structural_changes), 3)
            
            # Extra points for complex change types
            complex_changes = ['class_added', 'class_modified', 'interface_added', 'interface_modified']
            if any(sc.change_type in complex_changes for sc in structural_changes):
                score += 2
            
            # Points for modifications (more complex than additions/removals)
            modifications = [sc for sc in structural_changes if 'modified' in sc.change_type]
            score += min(len(modifications), 2)
        
        # File type complexity
        if file_change.language in ['cpp', 'rust', 'java']:
            score += 1  # More complex languages
        elif file_change.language in ['python', 'javascript', 'typescript']:
            pass  # Neutral
        elif file_change.language in ['json', 'yaml', 'markdown']:
            score = max(0, score - 1)  # Less complex
        
        # File change type complexity
        if file_change.change_type == 'renamed':
            score += 1  # Renames can be tricky
        elif file_change.change_type == 'deleted':
            score += 2  # Deletions can break things
        
        # Cap the score at 10
        return min(score, 10)