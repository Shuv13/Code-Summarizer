"""
Configuration management for Code Change Summarizer.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the code change summarizer."""
    
    DEFAULT_CONFIG = {
        "output_format": "plain",
        "quiet": False,
        "include_recommendations": True,
        "include_key_changes": True,
        "complexity_threshold": 5,
        "max_file_size": 1000000,  # 1MB
        "supported_extensions": [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
            ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".swift",
            ".kt", ".scala", ".html", ".css", ".scss", ".sass", ".json",
            ".xml", ".yaml", ".yml", ".md", ".sh", ".sql", ".r", ".m", ".pl"
        ],
        "template_variables": {
            "overview": "Overall summary",
            "total_files": "Number of files changed",
            "files_added": "Number of files added",
            "files_modified": "Number of files modified", 
            "files_deleted": "Number of files deleted",
            "lines_added": "Total lines added",
            "lines_removed": "Total lines removed",
            "key_changes": "List of key changes",
            "recommendations": "List of recommendations",
            "file_summaries": "Detailed file summaries"
        }
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from various sources."""
        # Load from user config file
        user_config_path = self._get_user_config_path()
        if user_config_path.exists():
            try:
                with open(user_config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self.config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load user config: {e}")
        
        # Load from project config file
        project_config_path = self._get_project_config_path()
        if project_config_path.exists():
            try:
                with open(project_config_path, 'r', encoding='utf-8') as f:
                    project_config = json.load(f)
                self.config.update(project_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load project config: {e}")
        
        # Load from environment variables
        self._load_from_env()
    
    def _get_user_config_path(self) -> Path:
        """Get the path to the user configuration file."""
        home = Path.home()
        return home / '.code-summarizer' / 'config.json'
    
    def _get_project_config_path(self) -> Path:
        """Get the path to the project configuration file."""
        return Path('.code-summarizer.json')
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'CODE_SUMMARIZER_FORMAT': 'output_format',
            'CODE_SUMMARIZER_QUIET': 'quiet',
            'CODE_SUMMARIZER_COMPLEXITY_THRESHOLD': 'complexity_threshold',
            'CODE_SUMMARIZER_MAX_FILE_SIZE': 'max_file_size'
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ['quiet']:
                    self.config[config_key] = value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['complexity_threshold', 'max_file_size']:
                    try:
                        self.config[config_key] = int(value)
                    except ValueError:
                        print(f"Warning: Invalid value for {env_var}: {value}")
                else:
                    self.config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self.config[key] = value
    
    def save_user_config(self):
        """Save current configuration to user config file."""
        user_config_path = self._get_user_config_path()
        user_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(user_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving user config: {e}")
    
    def create_sample_config(self, path: Optional[str] = None):
        """Create a sample configuration file."""
        if path is None:
            path = '.code-summarizer.json'
        
        sample_config = {
            "output_format": "markdown",
            "quiet": False,
            "include_recommendations": True,
            "include_key_changes": True,
            "complexity_threshold": 5,
            "max_file_size": 1000000,
            "custom_templates": {
                "brief": "Changed {total_files} files: +{lines_added}/-{lines_removed}",
                "detailed": "Summary: {overview}\n\nKey Changes:\n{key_changes}\n\nRecommendations:\n{recommendations}"
            }
        }
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
            print(f"Sample configuration created at: {path}")
        except IOError as e:
            print(f"Error creating sample config: {e}")
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        valid = True
        
        # Validate output format
        valid_formats = ['plain', 'text', 'markdown', 'md', 'json']
        if self.config.get('output_format') not in valid_formats:
            print(f"Warning: Invalid output_format. Must be one of: {valid_formats}")
            valid = False
        
        # Validate complexity threshold
        threshold = self.config.get('complexity_threshold', 0)
        if not isinstance(threshold, int) or threshold < 0 or threshold > 10:
            print("Warning: complexity_threshold must be an integer between 0 and 10")
            valid = False
        
        # Validate max file size
        max_size = self.config.get('max_file_size', 0)
        if not isinstance(max_size, int) or max_size <= 0:
            print("Warning: max_file_size must be a positive integer")
            valid = False
        
        return valid
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a custom template by name."""
        custom_templates = self.config.get('custom_templates', {})
        return custom_templates.get(name)
    
    def list_templates(self) -> Dict[str, str]:
        """List all available custom templates."""
        return self.config.get('custom_templates', {})


# Global configuration instance
config = Config()