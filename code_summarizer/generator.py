"""
Summary generation module.
"""

import logging
from typing import List
from .models import AnalyzedChange, Summary, FileSummary, ChangeStatistics

# Set up logging
logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generates human-readable summaries from analyzed changes."""
    
    def generate_summary(self, analyzed_changes: List[AnalyzedChange]) -> Summary:
        """Generate complete summary from analyzed changes."""
        if not analyzed_changes:
            logger.debug("No analyzed changes provided, returning empty summary")
            return Summary(
                overview="No changes detected",
                file_summaries=[],
                statistics=ChangeStatistics(),
                key_changes=[],
                recommendations=[]
            )
        
        try:
            logger.debug(f"Generating summary for {len(analyzed_changes)} analyzed changes")
            
            # Generate file summaries
            file_summaries = []
            for change in analyzed_changes:
                try:
                    file_summary = self._create_file_summary(change)
                    file_summaries.append(file_summary)
                except Exception as e:
                    logger.error(f"Error creating file summary for {change.file_change.filename}: {e}")
                    # Create a minimal file summary to avoid breaking the pipeline
                    file_summaries.append(FileSummary(
                        filename=change.file_change.filename,
                        summary=f"Error generating summary for {change.file_change.filename}",
                        key_changes=[]
                    ))
            
            # Calculate statistics
            statistics = self._calculate_statistics(analyzed_changes)
            
            # Generate overall overview
            overview = self._generate_overview(analyzed_changes, statistics)
            
            # Identify key changes
            key_changes = self._identify_key_changes(analyzed_changes)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analyzed_changes)
            
            logger.debug("Successfully generated summary")
            return Summary(
                overview=overview,
                file_summaries=file_summaries,
                statistics=statistics,
                key_changes=key_changes,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Return a minimal summary to avoid breaking the pipeline
            return Summary(
                overview="Error generating summary",
                file_summaries=[],
                statistics=ChangeStatistics(),
                key_changes=[],
                recommendations=["Review failed - manual analysis recommended"]
            )
    
    def create_change_description(self, change: AnalyzedChange) -> str:
        """Create human-readable description of a change."""
        file_change = change.file_change
        descriptions = []
        
        # File-level description
        if file_change.change_type == 'added':
            descriptions.append(f"Added new file '{file_change.filename}'")
        elif file_change.change_type == 'deleted':
            descriptions.append(f"Deleted file '{file_change.filename}'")
        elif file_change.change_type == 'renamed':
            descriptions.append(f"Renamed '{file_change.old_filename}' to '{file_change.filename}'")
        else:
            descriptions.append(f"Modified '{file_change.filename}'")
        
        # Add line change information
        if file_change.lines_added > 0 or file_change.lines_removed > 0:
            line_info = []
            if file_change.lines_added > 0:
                line_info.append(f"+{file_change.lines_added} lines")
            if file_change.lines_removed > 0:
                line_info.append(f"-{file_change.lines_removed} lines")
            descriptions.append(f"({', '.join(line_info)})")
        
        # Add structural changes
        if change.structural_changes:
            structural_desc = self._describe_structural_changes(change.structural_changes)
            if structural_desc:
                descriptions.append(structural_desc)
        
        # Add purpose if available
        if change.purpose_inference and change.purpose_inference != "Code modification":
            descriptions.append(f"Purpose: {change.purpose_inference}")
        
        return " - ".join(descriptions)
    
    def _create_file_summary(self, change: AnalyzedChange) -> FileSummary:
        """Create a summary for a single file change."""
        file_change = change.file_change
        
        # Generate main summary
        summary = self.create_change_description(change)
        
        # Identify key changes for this file
        key_changes = []
        
        # Add structural changes as key changes
        for sc in change.structural_changes:
            if sc.change_type.endswith('_added'):
                key_changes.append(f"Added {sc.change_type.replace('_added', '')} '{sc.element_name}'")
            elif sc.change_type.endswith('_removed'):
                key_changes.append(f"Removed {sc.change_type.replace('_removed', '')} '{sc.element_name}'")
            elif sc.change_type.endswith('_modified'):
                key_changes.append(f"Modified {sc.change_type.replace('_modified', '')} '{sc.element_name}'")
        
        # Add complexity indicator if high
        if change.complexity_score >= 7:
            key_changes.append(f"High complexity change (score: {change.complexity_score}/10)")
        elif change.complexity_score >= 4:
            key_changes.append(f"Medium complexity change (score: {change.complexity_score}/10)")
        
        # Add impact assessment if significant
        if "high impact" in change.impact_assessment.lower():
            key_changes.append("High impact change - review carefully")
        
        return FileSummary(
            filename=file_change.filename,
            summary=summary,
            key_changes=key_changes
        )
    
    def _calculate_statistics(self, analyzed_changes: List[AnalyzedChange]) -> ChangeStatistics:
        """Calculate overall statistics for the changes."""
        stats = ChangeStatistics()
        
        for change in analyzed_changes:
            file_change = change.file_change
            stats.total_files += 1
            
            if file_change.change_type == 'added':
                stats.files_added += 1
            elif file_change.change_type == 'modified':
                stats.files_modified += 1
            elif file_change.change_type == 'deleted':
                stats.files_deleted += 1
            
            stats.total_lines_added += file_change.lines_added
            stats.total_lines_removed += file_change.lines_removed
        
        return stats
    
    def _generate_overview(self, analyzed_changes: List[AnalyzedChange], statistics: ChangeStatistics) -> str:
        """Generate an overall overview of the changes."""
        overview_parts = []
        
        # Basic statistics
        if statistics.total_files == 1:
            overview_parts.append("1 file changed")
        else:
            overview_parts.append(f"{statistics.total_files} files changed")
        
        # File type breakdown
        if statistics.files_added > 0:
            overview_parts.append(f"{statistics.files_added} added")
        if statistics.files_modified > 0:
            overview_parts.append(f"{statistics.files_modified} modified")
        if statistics.files_deleted > 0:
            overview_parts.append(f"{statistics.files_deleted} deleted")
        
        # Line changes
        line_changes = []
        if statistics.total_lines_added > 0:
            line_changes.append(f"+{statistics.total_lines_added}")
        if statistics.total_lines_removed > 0:
            line_changes.append(f"-{statistics.total_lines_removed}")
        
        if line_changes:
            overview_parts.append(f"({', '.join(line_changes)} lines)")
        
        # Dominant purposes
        purposes = []
        for change in analyzed_changes:
            if change.purpose_inference:
                purposes.extend(change.purpose_inference.split('; '))
        
        # Count purpose frequency
        purpose_counts = {}
        for purpose in purposes:
            purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
        
        # Get most common purposes
        if purpose_counts:
            sorted_purposes = sorted(purpose_counts.items(), key=lambda x: x[1], reverse=True)
            top_purposes = [p[0] for p in sorted_purposes[:3]]
            if top_purposes:
                overview_parts.append(f"Primary focus: {', '.join(top_purposes)}")
        
        return ". ".join(overview_parts) + "."
    
    def _identify_key_changes(self, analyzed_changes: List[AnalyzedChange]) -> List[str]:
        """Identify the most important changes across all files."""
        key_changes = []
        
        # High complexity changes
        high_complexity_changes = [c for c in analyzed_changes if c.complexity_score >= 7]
        for change in high_complexity_changes:
            key_changes.append(f"High complexity change in {change.file_change.filename}")
        
        # New files
        new_files = [c for c in analyzed_changes if c.file_change.change_type == 'added']
        if len(new_files) > 3:
            key_changes.append(f"Multiple new files added ({len(new_files)} files)")
        else:
            for change in new_files:
                key_changes.append(f"New file: {change.file_change.filename}")
        
        # Deleted files
        deleted_files = [c for c in analyzed_changes if c.file_change.change_type == 'deleted']
        for change in deleted_files:
            key_changes.append(f"Deleted file: {change.file_change.filename}")
        
        # Large changes
        large_changes = [c for c in analyzed_changes 
                        if (c.file_change.lines_added + c.file_change.lines_removed) > 100]
        for change in large_changes:
            total_lines = change.file_change.lines_added + change.file_change.lines_removed
            key_changes.append(f"Large change in {change.file_change.filename} ({total_lines} lines)")
        
        # Significant structural changes
        for change in analyzed_changes:
            class_changes = [sc for sc in change.structural_changes if 'class' in sc.change_type]
            if len(class_changes) > 2:
                key_changes.append(f"Multiple class changes in {change.file_change.filename}")
        
        return key_changes[:10]  # Limit to top 10 key changes
    
    def _generate_recommendations(self, analyzed_changes: List[AnalyzedChange]) -> List[str]:
        """Generate recommendations based on the changes."""
        recommendations = []
        
        # High complexity warnings
        high_complexity_count = len([c for c in analyzed_changes if c.complexity_score >= 7])
        if high_complexity_count > 0:
            recommendations.append(f"Review {high_complexity_count} high-complexity changes carefully")
        
        # Test coverage recommendations
        test_files = [c for c in analyzed_changes 
                     if 'test' in c.file_change.filename.lower() or 'spec' in c.file_change.filename.lower()]
        non_test_files = [c for c in analyzed_changes if c not in test_files]
        
        if len(non_test_files) > len(test_files) * 2:
            recommendations.append("Consider adding tests for the new functionality")
        
        # Documentation recommendations
        has_doc_changes = any('documentation' in c.purpose_inference.lower() for c in analyzed_changes)
        has_new_features = any('feature addition' in c.purpose_inference.lower() for c in analyzed_changes)
        
        if has_new_features and not has_doc_changes:
            recommendations.append("Consider updating documentation for new features")
        
        # API change warnings
        api_changes = [c for c in analyzed_changes if 'public api' in c.impact_assessment.lower()]
        if api_changes:
            recommendations.append("API changes detected - ensure backward compatibility")
        
        # Large scale change recommendations
        total_lines_changed = sum(c.file_change.lines_added + c.file_change.lines_removed 
                                for c in analyzed_changes)
        if total_lines_changed > 500:
            recommendations.append("Large-scale changes - consider breaking into smaller commits")
        
        # Dependency change recommendations
        dependency_changes = [c for c in analyzed_changes 
                            if any('import' in sc.change_type for sc in c.structural_changes)]
        if dependency_changes:
            recommendations.append("Dependency changes detected - verify build and deployment")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _describe_structural_changes(self, structural_changes) -> str:
        """Create a description of structural changes."""
        if not structural_changes:
            return ""
        
        # Group changes by type
        change_groups = {}
        for sc in structural_changes:
            change_type = sc.change_type.split('_')[0]  # Get base type (function, class, etc.)
            if change_type not in change_groups:
                change_groups[change_type] = {'added': [], 'removed': [], 'modified': []}
            
            if sc.change_type.endswith('_added'):
                change_groups[change_type]['added'].append(sc.element_name)
            elif sc.change_type.endswith('_removed'):
                change_groups[change_type]['removed'].append(sc.element_name)
            elif sc.change_type.endswith('_modified'):
                change_groups[change_type]['modified'].append(sc.element_name)
        
        descriptions = []
        for change_type, changes in change_groups.items():
            type_descriptions = []
            
            if changes['added']:
                if len(changes['added']) == 1:
                    type_descriptions.append(f"added {change_type} {changes['added'][0]}")
                else:
                    type_descriptions.append(f"added {len(changes['added'])} {change_type}s")
            
            if changes['removed']:
                if len(changes['removed']) == 1:
                    type_descriptions.append(f"removed {change_type} {changes['removed'][0]}")
                else:
                    type_descriptions.append(f"removed {len(changes['removed'])} {change_type}s")
            
            if changes['modified']:
                if len(changes['modified']) == 1:
                    type_descriptions.append(f"modified {change_type} {changes['modified'][0]}")
                else:
                    type_descriptions.append(f"modified {len(changes['modified'])} {change_type}s")
            
            if type_descriptions:
                descriptions.append(', '.join(type_descriptions))
        
        return '; '.join(descriptions) if descriptions else ""