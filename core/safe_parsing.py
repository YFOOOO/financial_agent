"""
Safe Parsing Utilities

This module provides robust functions for parsing and cleaning LLM outputs.
It handles common issues like Markdown code fences, missing tags, and JSON formatting.
"""

import re
from typing import Optional

def ensure_execute_python_tags(text: str) -> str:
    """
    Normalizes LLM generated code by ensuring it is wrapped in <execute_python> tags.
    
    Steps:
    1. Removes Markdown code fences (```python ... ```)
    2. Adds <execute_python> tags if missing
    
    Args:
        text: Raw text from LLM
    
    Returns:
        Normalized text with <execute_python> tags
    """
    text = text.strip()
    
    # Remove Markdown code fences
    text = re.sub(r"^```(?:python)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    
    # Add tags if missing
    if "<execute_python>" not in text:
        text = f"<execute_python>\n{text}\n</execute_python>"
    
    return text


def extract_code_from_tags(text: str) -> Optional[str]:
    """
    Extracts code from <execute_python> tags.
    
    Args:
        text: Text containing tags
    
    Returns:
        Extracted code string, or None if not found
    """
    match = re.search(r"<execute_python>(.*?)</execute_python>", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_json_from_markdown(text: str) -> Optional[str]:
    """
    Extracts JSON from Markdown code blocks.
    
    Looks for JSON within ```json or ``` code fences.
    
    Args:
        text: Text containing markdown code blocks
    
    Returns:
        Extracted JSON string, or the original text if no code block found
    """
    # Try to find ```json code block
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try to find generic ``` code block
    match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If text looks like JSON (starts with { or [), return it
    text = text.strip()
    if text.startswith('{') or text.startswith('['):
        return text
    
    return None


def safe_json_parse(text: str) -> Optional[dict]:
    """
    Safely parse JSON string with error handling.
    
    Args:
        text: JSON string to parse
    
    Returns:
        Parsed dictionary, or None if parsing fails
    """
    import json
    
    if not text:
        return None
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to fix common issues
        text = text.strip()
        
        # Remove trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
