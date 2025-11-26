"""
Format Comparator for Smart Validation Framework

Compares Vector-Native vs JSON vs Natural Language formats.
Reuses functions from test_token_reduction.py per PT:1.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from vector_native import (
    get_vector_native_system_prompt,
    count_tokens,
    parse_with_fallback,
)

# Import reusable functions from existing test infrastructure
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from test_token_reduction import get_english_response, get_vector_native_response


def prompt_to_json_structure(prompt: str) -> Dict[str, Any]:
    """
    Convert natural language prompt to JSON structure.
    
    This is a simple heuristic conversion - in practice, you might use
    an LLM to convert prompts to JSON, but for validation we want
    a consistent structure.
    
    Args:
        prompt: Natural language prompt
    
    Returns:
        JSON structure dict
    """
    # Simple heuristic: extract key operations and parameters
    # This is a placeholder - actual implementation would be more sophisticated
    lines = prompt.split('\n')
    
    structure = {
        "action": "process",
        "parameters": {}
    }
    
    # Extract common patterns
    prompt_lower = prompt.lower()
    if "analyze" in prompt_lower:
        structure["action"] = "analyze"
    elif "create" in prompt_lower:
        structure["action"] = "create"
    elif "process" in prompt_lower:
        structure["action"] = "process"
    elif "generate" in prompt_lower:
        structure["action"] = "generate"
    
    # Extract data mentions
    if "revenue" in prompt_lower:
        structure["parameters"]["metrics"] = structure["parameters"].get("metrics", [])
        if "revenue" not in structure["parameters"]["metrics"]:
            structure["parameters"]["metrics"].append("revenue")
    
    if "profit" in prompt_lower:
        structure["parameters"]["metrics"] = structure["parameters"].get("metrics", [])
        if "profit" not in structure["parameters"]["metrics"]:
            structure["parameters"]["metrics"].append("profit")
    
    # Extract time periods
    if "q4" in prompt_lower or "q1" in prompt_lower or "q2" in prompt_lower or "q3" in prompt_lower:
        structure["parameters"]["period"] = "quarterly"
    
    return structure


def get_json_response(
    client: OpenAI,
    prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    call_tracker: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get JSON-formatted response from OpenAI.
    
    Args:
        client: OpenAI client
        prompt: User prompt
        model: Model to use
        temperature: Temperature setting
    
    Returns:
        {
            "response": str (JSON string),
            "parsed": dict or None,
            "format": "json" or "unknown",
            "tokens_used": int,
        }
    """
    json_structure = prompt_to_json_structure(prompt)
    json_prompt = json.dumps(json_structure, indent=2)
    
    system_prompt = (
        "You are a helpful assistant. Respond ONLY with valid JSON. "
        "Do not include any explanatory text, markdown formatting, or code blocks. "
        "Return pure JSON that can be parsed directly."
    )
    
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Convert this to JSON format: {prompt}"},
        ],
    )
    
    # Track API call if tracker provided
    if call_tracker is not None:
        call_tracker.total_calls += 1
    
    content = response.choices[0].message.content.strip()
    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
    
    # Try to parse JSON
    parsed = None
    format_type = "unknown"
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        lines = content.split('\n')
        content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
    
    try:
        parsed = json.loads(content)
        format_type = "json"
    except json.JSONDecodeError:
        # Not valid JSON
        pass
    
    return {
        "response": content,
        "parsed": parsed,
        "format": format_type,
        "tokens_used": tokens_used,
    }


def compare_formats(
    client: OpenAI,
    prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    vn_prompt_variant: str = "strict",
    cached_english: Optional[Dict[str, Any]] = None,
    call_tracker: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Compare all three formats for a single prompt.
    
    Args:
        client: OpenAI client
        prompt: User prompt to test
        model: Model to use
        temperature: Temperature setting
        vn_prompt_variant: Vector-native prompt variant ("strict", "balanced", "minimal")
        cached_english: Optional cached English response (reuse across formats)
    
    Returns:
        {
            "prompt": str,
            "natural_language": {...},
            "json": {...},
            "vector_native": {...},
            "comparison": {
                "nl_tokens": int,
                "json_tokens": int,
                "vn_tokens": int,
                "nl_compliance": float (1.0 if valid, 0.0 if invalid),
                "json_compliance": float (1.0 if valid JSON, 0.0 if invalid),
                "vn_compliance": float (1.0 if valid VN, 0.0 if invalid),
            }
        }
    """
    # Get Natural Language response (use cache if available)
    if cached_english:
        nl_result = cached_english
    else:
        nl_result = get_english_response(client, prompt, model)
    
    # Get JSON response
    json_result = get_json_response(client, prompt, model, temperature, call_tracker)
    
    # Get Vector-Native response
    vn_system_prompt = get_vector_native_system_prompt(vn_prompt_variant)
    # Note: get_vector_native_response is from test_token_reduction.py and doesn't have call_tracker
    # We'll track it manually after the call
    vn_result = get_vector_native_response(client, prompt, vn_system_prompt, model)
    if call_tracker is not None:
        call_tracker.total_calls += 1
    
    # Calculate compliance
    nl_compliance = 1.0  # Natural language is always "compliant" (it's the baseline)
    json_compliance = 1.0 if json_result["format"] == "json" else 0.0
    vn_compliance = 1.0 if vn_result["format"] == "vector_native" else 0.0
    
    # Calculate token counts
    nl_tokens = nl_result.get("tokens_used", 0)
    json_tokens = json_result.get("tokens_used", 0)
    vn_tokens = vn_result.get("tokens_used", 0)
    
    return {
        "prompt": prompt,
        "natural_language": {
            "response": nl_result.get("response", ""),
            "tokens_used": nl_tokens,
            "compliance": nl_compliance,
        },
        "json": {
            "response": json_result.get("response", ""),
            "tokens_used": json_tokens,
            "compliance": json_compliance,
            "parsed": json_result.get("parsed"),
        },
        "vector_native": {
            "response": vn_result.get("response", ""),
            "tokens_used": vn_tokens,
            "compliance": vn_compliance,
            "parsed": str(vn_result.get("parsed")) if vn_result.get("parsed") else None,
        },
        "comparison": {
            "nl_tokens": nl_tokens,
            "json_tokens": json_tokens,
            "vn_tokens": vn_tokens,
            "nl_compliance": nl_compliance,
            "json_compliance": json_compliance,
            "vn_compliance": vn_compliance,
            "vn_reduction_vs_nl": (
                (nl_tokens - vn_tokens) / nl_tokens * 100
                if nl_tokens > 0
                else 0
            ),
            "vn_reduction_vs_json": (
                (json_tokens - vn_tokens) / json_tokens * 100
                if json_tokens > 0
                else 0
            ),
        },
    }

