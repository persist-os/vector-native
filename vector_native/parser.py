"""
Vector-Native Parser: Parse vector-native strings into structured data.

This is the core value-add beyond the system prompt - developers need to parse output.
"""

import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ParsedOperation:
    """Parsed vector-native operation."""
    operation: str
    params: Dict[str, str]
    attention: str  # "full", "partial", "none"
    raw: str  # Original string


class ParseError(Exception):
    """Error parsing vector-native string."""
    pass


# Type alias for hybrid parsing results
HybridContent = Union[ParsedOperation, str]


def parse_vector_native(text: str) -> Union[ParsedOperation, List[ParsedOperation]]:
    """
    Parse vector-native string into structured data.
    
    Args:
        text: Vector-native string (e.g., "●create_widget|userId:123|type:chart")
    
    Returns:
        ParsedOperation or list of ParsedOperation if multiple operations
    
    Raises:
        ParseError: If syntax is invalid or text is empty
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Empty string raises error (not valid operation)
    if not text:
        raise ParseError("Empty string is not a valid vector-native operation")
    
    # Handle multiple operations (one per line)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        raise ParseError("No valid operations found in text")
    
    if len(lines) == 1:
        return _parse_single_operation(lines[0])
    else:
        return [_parse_single_operation(line) for line in lines]


def _parse_single_operation(line: str) -> ParsedOperation:
    """Parse a single vector-native operation."""
    # Extract attention symbol (●, ◐, ○)
    attention_match = re.match(r'^([●◐○])', line)
    if not attention_match:
        raise ParseError(f"Operation must start with attention symbol (●, ◐, ○): {line}")
    
    attention_symbol = attention_match.group(1)
    attention_map = {
        "●": "full",
        "◐": "partial",
        "○": "none"
    }
    attention = attention_map.get(attention_symbol, "full")
    
    # Remove attention symbol
    remaining = line[1:].strip()
    
    # Split by pipe separator
    parts = remaining.split('|')
    
    if not parts:
        raise ParseError(f"Operation must have at least operation name: {line}")
    
    # First part is operation name
    operation = parts[0].strip()
    if not operation:
        raise ParseError(f"Operation name cannot be empty: {line}")
    
    # Remaining parts are params (key:value)
    params = {}
    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        
        # Split by colon (first colon is separator)
        if ':' not in part:
            raise ParseError(f"Parameter must be in format 'key:value': {part}")
        
        colon_index = part.index(':')
        key = part[:colon_index].strip()
        value = part[colon_index + 1:].strip()
        
        if not key:
            raise ParseError(f"Parameter key cannot be empty: {part}")
        
        params[key] = value
    
    return ParsedOperation(
        operation=operation,
        params=params,
        attention=attention,
        raw=line
    )


def validate_syntax(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate vector-native syntax.
    
    Args:
        text: Vector-native string to validate
    
    Returns:
        (is_valid, error_message)
    """
    try:
        parse_vector_native(text)
        return True, None
    except ParseError as e:
        return False, str(e)


def parse_vector_native_hybrid(text: str) -> List[HybridContent]:
    """
    Parse vector-native strings, allowing non-compliant lines as prose.
    
    This hybrid variant honors token reduction achieved by compliant lines while
    preserving necessary prose that doesn't follow vector-native syntax.
    
    Args:
        text: LLM output (may contain mixed vector-native operations and prose)
    
    Returns:
        List of ParsedOperation (for compliant lines) and str (for prose lines)
    
    Raises:
        ParseError: If no valid content found (all lines are empty after stripping)
    """
    text = text.strip()
    
    # Handle delimiters (strip ⟦ and ⟧ if present)
    if text.startswith('⟦'):
        text = text[1:]
    if text.endswith('⟧'):
        text = text[:-1]
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        raise ParseError("No valid content found in text")
    
    results: List[HybridContent] = []
    
    for line in lines:
        try:
            # If a line is compliant, parse it normally
            parsed_op = _parse_single_operation(line)
            results.append(parsed_op)
        except ParseError:
            # If a line is NOT compliant (it's prose or malformed VN),
            # treat it as English and continue to the next line.
            results.append(line)
    
    return results


def parse_with_fallback(text: str, hybrid: bool = False) -> Dict:
    """
    Parse vector-native with fallback to English.
    
    Args:
        text: LLM output (may be vector-native or English)
        hybrid: If True, use hybrid parsing (preserve prose, parse operations)
    
    Returns:
        {
            "format": "vector_native" | "hybrid" | "english",
            "parsed": ParsedOperation, List[HybridContent], or None,
            "raw": str,
            "error": str or None
        }
    """
    if hybrid:
        # Hybrid mode: parse line-by-line, preserve prose
        try:
            parsed = parse_vector_native_hybrid(text)
            # Check if we have any ParsedOperation objects
            has_operations = any(isinstance(item, ParsedOperation) for item in parsed)
            has_prose = any(isinstance(item, str) for item in parsed)
            
            if has_operations and has_prose:
                format_type = "hybrid"
            elif has_operations:
                format_type = "vector_native"
            else:
                format_type = "english"
            
            return {
                "format": format_type,
                "parsed": parsed,
                "raw": text,
                "error": None
            }
        except ParseError as e:
            # Fallback: treat as English
            return {
                "format": "english",
                "parsed": None,
                "raw": text,
                "error": str(e)
            }
    else:
        # Strict mode: all-or-nothing parsing (original behavior)
        try:
            parsed = parse_vector_native(text)
            return {
                "format": "vector_native",
                "parsed": parsed,
                "raw": text,
                "error": None
            }
        except ParseError:
            # Fallback: treat as English
            return {
                "format": "english",
                "parsed": None,
                "raw": text,
                "error": "Not valid vector-native syntax"
            }


def to_dict(parsed: ParsedOperation) -> Dict:
    """Convert ParsedOperation to dictionary."""
    return {
        "operation": parsed.operation,
        "params": parsed.params,
        "attention": parsed.attention
    }


def extract_operations(hybrid_result: List[HybridContent]) -> List[ParsedOperation]:
    """Extract only ParsedOperation objects from hybrid parsing result."""
    return [item for item in hybrid_result if isinstance(item, ParsedOperation)]


def extract_prose(hybrid_result: List[HybridContent]) -> List[str]:
    """Extract only prose strings from hybrid parsing result."""
    return [item for item in hybrid_result if isinstance(item, str)]

