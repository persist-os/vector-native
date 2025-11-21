"""
Dataset Loader for HLE Benchmark
Loads cais/hle dataset from HuggingFace
"""
from typing import List, Dict, Any, Optional

try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    load_dataset = None


def load_hle_dataset(
    dataset_name: str = "cais/hle",
    split: str = "test",
    sample_size: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Load HLE dataset from HuggingFace.
    
    Args:
        dataset_name: HuggingFace dataset identifier
        split: Dataset split to load ("test", "train", "validation")
        sample_size: Optional limit on number of examples (for testing)
    
    Returns:
        List of examples, each containing:
        - question: str
        - options: List[str] (multiple choice options)
        - answer: str (correct answer, typically A/B/C/D)
        - Other fields as present in dataset
    
    Raises:
        Exception: If dataset loading fails
    """
    if not DATASETS_AVAILABLE:
        raise ImportError("datasets package not installed. Install with: pip install datasets")
    
    try:
        print(f"Loading dataset: {dataset_name} (split: {split})...")
        dataset = load_dataset(dataset_name, split=split)
        
        # Convert to list of dicts
        examples = []
        for i, example in enumerate(dataset):
            if sample_size and i >= sample_size:
                break
            
            # Normalize example structure
            normalized = {
                "id": example.get("id", f"example_{i}"),
                "question": example.get("question", example.get("prompt", "")),
                "options": _extract_options(example),
                "answer": _extract_answer(example),
                "raw": example,  # Keep raw data for reference
            }
            examples.append(normalized)
        
        print(f"Loaded {len(examples)} examples")
        return examples
    
    except Exception as e:
        raise Exception(f"Failed to load dataset {dataset_name}: {e}")


def _extract_options(example: Dict[str, Any]) -> List[str]:
    """Extract multiple choice options from example"""
    # Try common field names
    if "options" in example:
        options = example["options"]
        if isinstance(options, list):
            return options
        if isinstance(options, dict):
            return [options[k] for k in sorted(options.keys())]
    
    if "choices" in example:
        choices = example["choices"]
        if isinstance(choices, list):
            return choices
    
    # Try to extract from question text
    question = example.get("question", example.get("prompt", ""))
    if "A)" in question and "B)" in question:
        # Parse options from question text
        parts = question.split("A)")
        if len(parts) > 1:
            options_text = "A)" + parts[1]
            options = []
            for letter in ["A", "B", "C", "D", "E"]:
                pattern = f"{letter}\\)"
                import re
                match = re.search(f"{pattern}([^A-Z)]+)", options_text)
                if match:
                    options.append(match.group(1).strip())
            if options:
                return options
    
    return []


def _extract_answer(example: Dict[str, Any]) -> str:
    """Extract correct answer from example"""
    # Try common field names
    if "answer" in example:
        answer = example["answer"]
        if isinstance(answer, str):
            return answer.strip().upper()
    
    if "correct_answer" in example:
        answer = example["correct_answer"]
        if isinstance(answer, str):
            return answer.strip().upper()
    
    if "label" in example:
        label = example["label"]
        if isinstance(label, (int, str)):
            # Convert to letter if numeric
            if isinstance(label, int):
                return chr(ord("A") + label)
            return str(label).strip().upper()
    
    return ""


def get_example_prompt(example: Dict[str, Any]) -> str:
    """
    Format example as prompt for LLM.
    
    Args:
        example: Example dict with question, options, etc.
    
    Returns:
        Formatted prompt string
    """
    question = example["question"]
    options = example.get("options", [])
    
    prompt = f"{question}\n\n"
    
    if options:
        prompt += "Options:\n"
        for i, option in enumerate(options):
            letter = chr(ord("A") + i)
            prompt += f"{letter}) {option}\n"
        prompt += "\n"
    
    prompt += "Provide your answer."
    
    return prompt

