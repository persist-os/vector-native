"""
Answer Extraction and Validation for HLE Benchmark
"""
import re
from typing import Dict, Any, Optional, List


def extract_nl_answer(response: str, pattern: str = r"ANSWER:\s*([A-Z])") -> Optional[str]:
    """
    Extract answer from natural language response.
    
    Args:
        response: LLM response text
        pattern: Regex pattern to match answer (default: "ANSWER: A")
    
    Returns:
        Extracted answer letter (A/B/C/D) or None if not found
    """
    # Try regex pattern first
    match = re.search(pattern, response, re.IGNORECASE)
    if match:
        answer = match.group(1).upper()
        if answer in ["A", "B", "C", "D", "E"]:
            return answer
    
    # Try to find answer at end of response
    # Look for patterns like "The answer is A" or "Answer: B"
    patterns = [
        r"(?:answer|correct|choice)\s+is\s+([A-E])",
        r"(?:answer|correct|choice)[:\s]+([A-E])",
        r"\b([A-E])\s*(?:is|is the)?\s*(?:correct|answer|choice)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        if matches:
            answer = matches[-1].upper()  # Take last match
            if answer in ["A", "B", "C", "D", "E"]:
                return answer
    
    # Try to find standalone letter at end
    lines = response.strip().split("\n")
    if lines:
        last_line = lines[-1].strip()
        # Check if last line is just a letter
        if len(last_line) == 1 and last_line.upper() in ["A", "B", "C", "D", "E"]:
            return last_line.upper()
    
    return None


def extract_vn_answer(response: str, pattern: str = r"●answer\|value:([A-Z])") -> Optional[str]:
    """
    Extract answer from vector-native response.
    
    Args:
        response: LLM response in vector-native format
        pattern: Pattern to match VN answer (default: "●answer|value:A")
    
    Returns:
        Extracted answer letter (A/B/C/D) or None if not found
    """
    # Try exact pattern match
    match = re.search(pattern, response)
    if match:
        answer = match.group(1).upper()
        if answer in ["A", "B", "C", "D", "E"]:
            return answer
    
    # Try variations of VN answer format
    patterns = [
        r"●answer\|value:([A-E])",
        r"●answer\|answer:([A-E])",
        r"●answer\|result:([A-E])",
        r"●answer\|choice:([A-E])",
        r"answer\|value:([A-E])",  # Without ●
        r"answer\|([A-E])",  # Minimal format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            answer = match.group(1).upper()
            if answer in ["A", "B", "C", "D", "E"]:
                return answer
    
    # Try to find answer in delimited blocks
    # Look for ⟦...●answer|value:A...⟧
    block_pattern = r"⟦[^⟧]*●answer\|value:([A-E])[^⟧]*⟧"
    match = re.search(block_pattern, response)
    if match:
        answer = match.group(1).upper()
        if answer in ["A", "B", "C", "D", "E"]:
            return answer
    
    # Fallback: Look for any letter after "answer" in VN format
    answer_pattern = r"(?:●answer|answer)\|.*?([A-E])"
    match = re.search(answer_pattern, response)
    if match:
        answer = match.group(1).upper()
        if answer in ["A", "B", "C", "D", "E"]:
            return answer
    
    return None


def validate_answer(
    predicted: Optional[str],
    correct: str,
    mode: str = "exact_match"
) -> bool:
    """
    Validate predicted answer against correct answer.
    
    Args:
        predicted: Predicted answer (A/B/C/D/E or None)
        correct: Correct answer (A/B/C/D/E)
        mode: Validation mode ("exact_match", "flexible", "multiple_choice")
    
    Returns:
        True if prediction is correct, False otherwise
    """
    if predicted is None:
        return False
    
    predicted = predicted.upper().strip()
    correct = correct.upper().strip()
    
    if mode == "exact_match":
        return predicted == correct
    
    elif mode == "flexible":
        # Allow case-insensitive, whitespace-tolerant matching
        return predicted.strip().upper() == correct.strip().upper()
    
    elif mode == "multiple_choice":
        # For multiple choice, exact match is required
        # But normalize both to single letter
        pred_letter = predicted[0] if predicted else None
        correct_letter = correct[0] if correct else None
        return pred_letter == correct_letter
    
    else:
        # Default to exact match
        return predicted == correct


def evaluate_response(
    response: str,
    correct_answer: str,
    response_type: str,  # "nl" or "vn"
    extraction_pattern: Optional[str] = None,
    validation_modes: List[str] = None
) -> Dict[str, Any]:
    """
    Evaluate a single response against correct answer.
    
    Args:
        response: LLM response text
        correct_answer: Correct answer (A/B/C/D/E)
        response_type: "nl" or "vn"
        extraction_pattern: Optional custom extraction pattern
        validation_modes: List of validation modes to use
    
    Returns:
        {
            "extracted_answer": str or None,
            "correct_answer": str,
            "is_correct": dict[str, bool],  # Per validation mode
            "extraction_success": bool,
        }
    """
    if validation_modes is None:
        validation_modes = ["exact_match"]
    
    # Extract answer
    if response_type == "nl":
        extracted = extract_nl_answer(response, extraction_pattern or r"ANSWER:\s*([A-Z])")
    elif response_type == "vn":
        extracted = extract_vn_answer(response, extraction_pattern or r"●answer\|value:([A-Z])")
    else:
        raise ValueError(f"Unknown response_type: {response_type}")
    
    # Validate against each mode
    validation_results = {}
    for mode in validation_modes:
        validation_results[mode] = validate_answer(extracted, correct_answer, mode)
    
    return {
        "extracted_answer": extracted,
        "correct_answer": correct_answer,
        "is_correct": validation_results,
        "extraction_success": extracted is not None,
        "response_preview": response[:200] if response else "",
    }

