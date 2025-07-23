"""
Tests for configuration system.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch
from code_summarizer.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for configuration system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_default_config(self):
        """Test default configuration values."""
        self.assertEqual(self.config.get('output_format'), 'plain')
        self.assertEqual(self.config.get('quiet'), False)
        self.assertEqual(self.config.get('include_recommendations'), True)
        self.assertEqual(self.config.get('complexity_threshold'), 5)
        self.assertIsInstance(self.config.get('supported_extensions'), list)
    
    def test_get_set_config(self):
        """Test getting and setting configuration values."""
        # Test get with default
        self.assertEqual(self.config.get('nonexistent', 'default'), 'default')
        
        # Test set and get
        self.config.set('test_key', 'test_value')
        self.assertEqual(self.config.get('test_key'), 'test_value')
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        self.config.set('output_format', 'json')
        self.config.set('complexity_threshold', 7)
        self.config.set('max_file_size', 500000)
        
        self.assertTrue(self.config.validate_config())
    
    def test_validate_config_invalid_format(self):
        """Test configuration validation with invalid format."""
        self.config.set('output_format', 'invalid_format')
        
        with patch('builtins.print') as mock_print:
            result = self.config.validate_config()
            self.assertFalse(result)
            mock_print.assert_called()
    
    def test_validate_config_invalid_threshold(self):
        """Test configuration validation with invalid complexity threshold."""
        self.config.set('complexity_threshold', 15)  # Invalid: > 10
        
        with patch('builtins.print') as mock_print:
            result = self.config.validate_config()
            self.assertFalse(result)
            mock_print.assert_called()
    
    def test_validate_config_invalid_file_size(self):
        """Test configuration validation with invalid file size."""
        self.config.set('max_file_size', -100)  # Invalid: negative
        
        with patch('builtins.print') as mock_print:
            result = self.config.validate_config()
            self.assertFalse(result)
            mock_print.assert_called()
    
    def test_custom_templates(self):
        """Test custom template functionality."""
        # Test with no templates
        self.assertIsNone(self.config.get_template('nonexistent'))
        self.assertEqual(self.config.list_templates(), {})
        
        # Add custom templates
        templates = {
            'brief': 'Files: {total_files}',
            'detailed': 'Summary: {overview}\nFiles: {total_files}'
        }
        self.config.set('custom_templates', templates)
        
        # Test template retrieval
        self.assertEqual(self.config.get_template('brief'), 'Files: {total_files}')
        self.assertEqual(self.config.list_templates(), templates)
    
    def test_create_sample_config(self):
        """Test creating sample configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Remove the file so we can test creation
            os.unlink(temp_file)
            
            with patch('builtins.print') as mock_print:
                self.config.create_sample_config(temp_file)
                mock_print.assert_called_with(f"Sample configuration created at: {temp_file}")
            
            # Verify file was created and contains valid JSON
            self.assertTrue(os.path.exists(temp_file))
            
            with open(temp_file, 'r') as f:
                sample_config = json.load(f)
            
            self.assertIn('output_format', sample_config)
            self.assertIn('custom_templates', sample_config)
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables."""
        with patch.dict(os.environ, {
            'CODE_SUMMARIZER_FORMAT': 'json',
            'CODE_SUMMARIZER_QUIET': 'true',
            'CODE_SUMMARIZER_COMPLEXITY_THRESHOLD': '8'
        }):
            config = Config()
            
            self.assertEqual(config.get('output_format'), 'json')
            self.assertEqual(config.get('quiet'), True)
            self.assertEqual(config.get('complexity_threshold'), 8)
    
    def test_environment_variable_invalid_values(self):
        """Test handling of invalid environment variable values."""
        with patch.dict(os.environ, {
            'CODE_SUMMARIZER_COMPLEXITY_THRESHOLD': 'invalid'
        }):
            with patch('builtins.print') as mock_print:
                config = Config()
                mock_print.assert_called()
    
    def test_config_file_loading(self):
        """Test loading configuration from file."""
        config_data = {
            'output_format': 'markdown',
            'quiet': True,
            'complexity_threshold': 7,
            'custom_templates': {
                'test': 'Test template: {overview}'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            # Mock the project config path to point to our temp file
            from pathlib import Path
            with patch.object(Config, '_get_project_config_path', return_value=Path(temp_file)):
                config = Config()
                
                self.assertEqual(config.get('output_format'), 'markdown')
                self.assertEqual(config.get('quiet'), True)
                self.assertEqual(config.get('complexity_threshold'), 7)
                self.assertEqual(config.get_template('test'), 'Test template: {overview}')
        
        finally:
            os.unlink(temp_file)
    
    def test_config_file_invalid_json(self):
        """Test handling of invalid JSON in config file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{ invalid json }')
            temp_file = f.name
        
        try:
            from pathlib import Path
            with patch.object(Config, '_get_project_config_path', return_value=Path(temp_file)):
                with patch('builtins.print') as mock_print:
                    config = Config()
                    mock_print.assert_called()
        
        finally:
            os.unlink(temp_file)
    
    def test_save_user_config(self):
        """Test saving user configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            from pathlib import Path
            config_file = Path(temp_dir) / 'config.json'
            
            with patch.object(Config, '_get_user_config_path', return_value=config_file):
                self.config.set('test_setting', 'test_value')
                self.config.save_user_config()
                
                # Verify file was created
                self.assertTrue(config_file.exists())
                
                # Verify content
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                
                self.assertEqual(saved_config['test_setting'], 'test_value')


if __name__ == '__main__':
    unittest.main()