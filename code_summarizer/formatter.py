"""
Output formatting module.
"""

import json
import logging
from typing import Dict, Any
from .models import Summary

# Set up logging
logger = logging.getLogger(__name__)


class OutputFormatter:
    """Formats summaries according to specified output format."""
    
    def format_output(self, summary: Summary, format_type: str) -> str:
        """Format summary according to the specified format type."""
        if not summary:
            raise ValueError("Summary cannot be None")
        
        if not format_type:
            raise ValueError("Format type cannot be empty")
        
        format_type = format_type.lower()
        logger.debug(f"Formatting output as {format_type}")
        
        try:
            if format_type == 'json':
                return self._format_json(summary)
            elif format_type == 'markdown' or format_type == 'md':
                return self._format_markdown(summary)
            elif format_type == 'plain' or format_type == 'text':
                return self._format_plain_text(summary)
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
        except Exception as e:
            logger.error(f"Error formatting output as {format_type}: {e}")
            raise
    
    def apply_template(self, summary: Summary, template: str) -> str:
        """Apply custom template to format the summary."""
        if not summary:
            raise ValueError("Summary cannot be None")
        
        if not template:
            raise ValueError("Template cannot be empty")
        
        logger.debug("Applying custom template")
        
        try:
            # Simple template substitution using string formatting
            template_vars = {
                'overview': summary.overview or "",
                'total_files': summary.statistics.total_files,
                'files_added': summary.statistics.files_added,
                'files_modified': summary.statistics.files_modified,
                'files_deleted': summary.statistics.files_deleted,
                'lines_added': summary.statistics.total_lines_added,
                'lines_removed': summary.statistics.total_lines_removed,
                'key_changes': '\n'.join(f"- {change}" for change in summary.key_changes),
                'recommendations': '\n'.join(f"- {rec}" for rec in summary.recommendations),
                'file_summaries': self._format_file_summaries_for_template(summary.file_summaries)
            }
            
            return template.format(**template_vars)
            
        except KeyError as e:
            logger.error(f"Template variable not found: {e}")
            raise ValueError(f"Template variable not found: {e}")
        except Exception as e:
            logger.error(f"Error applying template: {e}")
            raise ValueError(f"Error applying template: {e}")
    
    def _format_json(self, summary: Summary) -> str:
        """Format summary as JSON."""
        data = {
            'overview': summary.overview,
            'statistics': {
                'total_files': summary.statistics.total_files,
                'files_added': summary.statistics.files_added,
                'files_modified': summary.statistics.files_modified,
                'files_deleted': summary.statistics.files_deleted,
                'total_lines_added': summary.statistics.total_lines_added,
                'total_lines_removed': summary.statistics.total_lines_removed
            },
            'file_summaries': [
                {
                    'filename': fs.filename,
                    'summary': fs.summary,
                    'key_changes': fs.key_changes
                }
                for fs in summary.file_summaries
            ],
            'key_changes': summary.key_changes,
            'recommendations': summary.recommendations
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _format_markdown(self, summary: Summary) -> str:
        """Format summary as Markdown."""
        lines = []
        
        # Title
        lines.append("# Code Change Summary")
        lines.append("")
        
        # Overview
        lines.append("## Overview")
        lines.append(summary.overview)
        lines.append("")
        
        # Statistics
        lines.append("## Statistics")
        stats = summary.statistics
        lines.append(f"- **Total files changed:** {stats.total_files}")
        if stats.files_added > 0:
            lines.append(f"- **Files added:** {stats.files_added}")
        if stats.files_modified > 0:
            lines.append(f"- **Files modified:** {stats.files_modified}")
        if stats.files_deleted > 0:
            lines.append(f"- **Files deleted:** {stats.files_deleted}")
        lines.append(f"- **Lines added:** +{stats.total_lines_added}")
        lines.append(f"- **Lines removed:** -{stats.total_lines_removed}")
        lines.append("")
        
        # Key Changes
        if summary.key_changes:
            lines.append("## Key Changes")
            for change in summary.key_changes:
                lines.append(f"- {change}")
            lines.append("")
        
        # File Details
        if summary.file_summaries:
            lines.append("## File Details")
            for file_summary in summary.file_summaries:
                lines.append(f"### {file_summary.filename}")
                lines.append(file_summary.summary)
                
                if file_summary.key_changes:
                    lines.append("")
                    lines.append("**Key changes:**")
                    for key_change in file_summary.key_changes:
                        lines.append(f"- {key_change}")
                
                lines.append("")
        
        # Recommendations
        if summary.recommendations:
            lines.append("## Recommendations")
            for recommendation in summary.recommendations:
                lines.append(f"- {recommendation}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_plain_text(self, summary: Summary) -> str:
        """Format summary as plain text."""
        lines = []
        
        # Title
        lines.append("CODE CHANGE SUMMARY")
        lines.append("=" * 50)
        lines.append("")
        
        # Overview
        lines.append("OVERVIEW:")
        lines.append(summary.overview)
        lines.append("")
        
        # Statistics
        lines.append("STATISTICS:")
        stats = summary.statistics
        lines.append(f"  Total files changed: {stats.total_files}")
        if stats.files_added > 0:
            lines.append(f"  Files added: {stats.files_added}")
        if stats.files_modified > 0:
            lines.append(f"  Files modified: {stats.files_modified}")
        if stats.files_deleted > 0:
            lines.append(f"  Files deleted: {stats.files_deleted}")
        lines.append(f"  Lines added: +{stats.total_lines_added}")
        lines.append(f"  Lines removed: -{stats.total_lines_removed}")
        lines.append("")
        
        # Key Changes
        if summary.key_changes:
            lines.append("KEY CHANGES:")
            for i, change in enumerate(summary.key_changes, 1):
                lines.append(f"  {i}. {change}")
            lines.append("")
        
        # File Details
        if summary.file_summaries:
            lines.append("FILE DETAILS:")
            lines.append("-" * 30)
            for file_summary in summary.file_summaries:
                lines.append(f"File: {file_summary.filename}")
                lines.append(f"Summary: {file_summary.summary}")
                
                if file_summary.key_changes:
                    lines.append("Key changes:")
                    for key_change in file_summary.key_changes:
                        lines.append(f"  - {key_change}")
                
                lines.append("")
        
        # Recommendations
        if summary.recommendations:
            lines.append("RECOMMENDATIONS:")
            for i, recommendation in enumerate(summary.recommendations, 1):
                lines.append(f"  {i}. {recommendation}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_file_summaries_for_template(self, file_summaries) -> str:
        """Format file summaries for template substitution."""
        if not file_summaries:
            return "No file changes"
        
        lines = []
        for fs in file_summaries:
            lines.append(f"- {fs.filename}: {fs.summary}")
            if fs.key_changes:
                for key_change in fs.key_changes:
                    lines.append(f"  - {key_change}")
        
        return '\n'.join(lines)
    
    def get_supported_formats(self) -> list:
        """Get list of supported output formats."""
        return ['json', 'markdown', 'md', 'plain', 'text']
    
    def validate_format(self, format_type: str) -> bool:
        """Validate if the format type is supported."""
        return format_type.lower() in self.get_supported_formats()