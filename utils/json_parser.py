"""Robust JSON parsing utilities for LLM responses."""

import json
import re
import logging

logger = logging.getLogger(__name__)


def clean_json_string(json_str: str) -> str:
    """Clean JSON string to remove control characters and fix common issues."""
    # Remove markdown code fences if present
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'^```\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'```\s*$', '', json_str, flags=re.MULTILINE)
    
    return json_str.strip()


def fix_json_strings(json_str: str) -> str:
    """Fix unescaped newlines and control characters in JSON string values."""
    result = []
    i = 0
    in_string = False
    escape_next = False
    
    while i < len(json_str):
        char = json_str[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
        elif char == '\\':
            result.append(char)
            escape_next = True
        elif char == '"' and (i == 0 or json_str[i-1] != '\\'):
            in_string = not in_string
            result.append(char)
        elif in_string:
            # Inside a string value
            if char == '\n':
                result.append('\\n')
            elif char == '\r':
                result.append('\\r')
            elif char == '\t':
                result.append('\\t')
            elif ord(char) < 32:  # Other control characters
                result.append(f'\\u{ord(char):04x}')
            else:
                result.append(char)
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)


def parse_json_with_retry(response: str, max_attempts: int = 3) -> dict:
    """
    Parse JSON from LLM response with multiple fallback strategies.
    
    Args:
        response: Raw response from LLM
        max_attempts: Maximum number of parsing attempts
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If all parsing attempts fail
    """
    # Strategy 1: Direct JSON extraction and parse
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            json_str = clean_json_string(json_str)
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.debug(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Fix control characters in string values
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            json_str = clean_json_string(json_str)
            json_str = fix_json_strings(json_str)
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.debug(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Try replacing newlines with spaces (less ideal but sometimes works)
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            json_str = clean_json_string(json_str)
            # Replace unescaped newlines/tabs with spaces in string values
            lines = json_str.split('\n')
            fixed_lines = []
            in_string = False
            
            for line in lines:
                # Count quotes (accounting for escaped quotes)
                line_quotes = line.count('"') - line.count('\\"')
                if line_quotes % 2 == 1:
                    in_string = not in_string
                
                if in_string:
                    # Replace newlines/tabs with spaces in string values
                    fixed_line = line.replace('\t', ' ')
                else:
                    fixed_line = line
                
                fixed_lines.append(fixed_line)
            
            fixed_json = ' '.join(fixed_lines)
            return json.loads(fixed_json)
    except json.JSONDecodeError as e:
        logger.debug(f"Strategy 3 failed: {e}")
    
    # All strategies failed
    raise ValueError(
        f"Failed to parse JSON after {max_attempts} attempts. "
        f"Response preview: {response[:500]}...\n"
        f"Full response: {response}"
    )

