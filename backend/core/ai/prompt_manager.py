"""
Prompt management system for AI services.

This module provides version-controlled prompt templates with variable substitution,
ensuring maintainable and testable AI prompts across all features.
"""

import string
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger('ai.prompts')


@dataclass
class PromptTemplate:
    """
    Represents a versioned prompt template with metadata.
    """
    name: str
    version: int
    template_str: str
    description: str = ""
    expected_schema: str = ""
    
    def __post_init__(self):
        """Initialize the string template after dataclass creation."""
        self.template = string.Template(self.template_str)
    
    def substitute(self, **variables) -> str:
        """
        Substitute variables in the template.
        
        Args:
            **variables: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
            
        Raises:
            KeyError: If required template variables are missing
        """
        try:
            return self.template.substitute(**variables)
        except KeyError as e:
            missing_var = str(e).strip("'")
            logger.error(f"Missing template variable '{missing_var}' for prompt {self.name}_v{self.version}")
            raise ValueError(f"Missing required variable '{missing_var}' for prompt template")
    
    def safe_substitute(self, **variables) -> str:
        """
        Substitute variables with safe fallback for missing variables.
        
        Args:
            **variables: Variables to substitute in the template
            
        Returns:
            Formatted prompt string with missing variables left as-is
        """
        return self.template.safe_substitute(**variables)
    
    @property
    def full_name(self) -> str:
        """Get the full name with version."""
        return f"{self.name}_v{self.version}"


class PromptManager:
    """
    Manages AI prompt templates with version control and caching.
    
    Loads prompts from the filesystem and provides a simple interface
    for retrieving and formatting prompt templates.
    """
    
    def __init__(self, prompt_dir: Optional[str] = None):
        """
        Initialize the prompt manager.
        
        Args:
            prompt_dir: Directory containing prompt files (defaults to 'prompts')
        """
        self.prompt_dir = Path(prompt_dir or 'prompts')
        self._prompts: Dict[str, PromptTemplate] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompt templates from the prompt directory."""
        if not self.prompt_dir.exists():
            logger.warning(f"Prompt directory {self.prompt_dir} does not exist")
            return
        
        # Load all .txt files in the prompt directory
        for prompt_file in self.prompt_dir.glob('*.txt'):
            try:
                self._load_prompt_file(prompt_file)
            except Exception as e:
                logger.error(f"Failed to load prompt file {prompt_file}: {e}")
    
    def _load_prompt_file(self, prompt_file: Path):
        """
        Load a single prompt file and parse its metadata.
        
        Expected filename format: {name}_v{version}.txt
        Example: company_research_v1.txt
        """
        filename = prompt_file.stem
        
        # Parse name and version from filename
        if '_v' not in filename:
            logger.warning(f"Prompt file {prompt_file} doesn't follow naming convention (name_vN)")
            return
        
        name, version_str = filename.rsplit('_v', 1)
        
        try:
            version = int(version_str)
        except ValueError:
            logger.error(f"Invalid version number in prompt file {prompt_file}")
            return
        
        # Read the prompt content
        try:
            content = prompt_file.read_text(encoding='utf-8').strip()
        except Exception as e:
            logger.error(f"Failed to read prompt file {prompt_file}: {e}")
            return
        
        # Parse metadata from comments at the top of the file
        description = ""
        expected_schema = ""
        
        lines = content.split('\n')
        template_start = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('# Description:'):
                description = line.replace('# Description:', '').strip()
            elif line.startswith('# Schema:'):
                expected_schema = line.replace('# Schema:', '').strip()
            elif not line.startswith('#') and line:
                template_start = i
                break
        
        # Extract the actual template (without metadata comments)
        template_str = '\n'.join(lines[template_start:]).strip()
        
        # Create and store the prompt template
        prompt_template = PromptTemplate(
            name=name,
            version=version,
            template_str=template_str,
            description=description,
            expected_schema=expected_schema
        )
        
        full_name = prompt_template.full_name
        self._prompts[full_name] = prompt_template
        
        logger.info(f"Loaded prompt template: {full_name}")
    
    def get_prompt(self, name: str, version: int = 1) -> PromptTemplate:
        """
        Get a prompt template by name and version.
        
        Args:
            name: Prompt name
            version: Prompt version (defaults to 1)
            
        Returns:
            PromptTemplate instance
            
        Raises:
            ValueError: If prompt is not found
        """
        full_name = f"{name}_v{version}"
        
        if full_name not in self._prompts:
            available = list(self._prompts.keys())
            raise ValueError(f"Prompt '{full_name}' not found. Available prompts: {available}")
        
        return self._prompts[full_name]
    
    def get_latest_version(self, name: str) -> Optional[PromptTemplate]:
        """
        Get the latest version of a prompt template.
        
        Args:
            name: Prompt name
            
        Returns:
            Latest PromptTemplate or None if not found
        """
        matching_prompts = [
            (version, prompt) for prompt_name, prompt in self._prompts.items()
            if prompt_name.startswith(f"{name}_v")
            for version in [int(prompt_name.split('_v')[1])]
        ]
        
        if not matching_prompts:
            return None
        
        # Sort by version and return the latest
        latest_version, latest_prompt = max(matching_prompts, key=lambda x: x[0])
        return latest_prompt
    
    def list_prompts(self) -> Dict[str, PromptTemplate]:
        """Get all available prompt templates."""
        return self._prompts.copy()
    
    def reload(self):
        """Reload all prompt templates from disk."""
        self._prompts.clear()
        self._load_prompts()
        logger.info(f"Reloaded {len(self._prompts)} prompt templates")


# Global instance
prompt_manager = PromptManager()