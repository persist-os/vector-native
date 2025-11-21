"""
Prompt Templates for HLE Benchmark
Generates NL and VN prompts for reasoning tasks
"""
from pathlib import Path
from typing import Optional
from vector_native import get_vector_native_system_prompt


def get_nl_system_prompt() -> str:
    """
    Get natural language system prompt for reasoning tasks.
    
    Returns:
        System prompt encouraging detailed English reasoning
    """
    return """You are a helpful assistant that solves reasoning problems. 
Think step by step, show your reasoning process in natural English, and provide a clear answer.
When answering multiple choice questions, provide your reasoning first, then clearly state your answer."""


def get_vn_system_prompt(
    variant: str = "ultra_strict",
    global_mdc_path: Optional[str] = None
) -> str:
    """
    Get vector-native system prompt for reasoning tasks.
    
    CRITICAL: VN prompts must emphasize NO english reasoning, ONLY vn symbols.
    
    Args:
        variant: Prompt variant to use (default: "ultra_strict")
        global_mdc_path: Optional path to global.mdc for injection
    
    Returns:
        System prompt in vector-native format
    """
    # Load base VN prompt
    base_prompt = get_vector_native_system_prompt(variant)
    
    # Add HLE-specific instructions emphasizing NO english reasoning
    hle_instructions = """
●hle_reasoning_rules|mode:reasoning|format:vector_native_only|forbidden:english_reasoning|required:vn_symbols_only|critical:no_english_words|critical:no_natural_language|critical:only_symbols|reasoning:use_L1_L2_L3|answer:●answer|value:ANSWER_LETTER

●reasoning_process|step1:●analyze|question:Q|options:O1,O2,O3,O4|step2:●compare∠|option1:O1|option2:O2|similarity:high|step3:●evaluate[?→!]|condition:if_correct|action:select|step4:●answer|value:A|format:vector_native_only

●forbidden_reasoning|○english_words|○natural_language|○sentences|○explanations|○step_by_step_english|○thinking_process_english|○reasoning_in_english|required:only_symbols|required:vector_native_format|required:●answer|value:ANSWER
"""
    
    # Inject global.mdc if provided
    injected_content = ""
    if global_mdc_path:
        try:
            global_mdc = Path(global_mdc_path).read_text(encoding="utf-8")
            injected_content = f"\n\n{global_mdc}\n\n"
        except Exception as e:
            print(f"Warning: Could not load global.mdc from {global_mdc_path}: {e}")
    
    # Combine: base prompt + injected content + HLE instructions
    full_prompt = f"{base_prompt}{injected_content}{hle_instructions}"
    
    return full_prompt


def format_question_prompt(question: str, options: list[str]) -> str:
    """
    Format question as user prompt for LLM.
    
    Args:
        question: Question text
        options: List of multiple choice options
    
    Returns:
        Formatted prompt string
    """
    prompt = f"{question}\n\n"
    
    if options:
        prompt += "Options:\n"
        for i, option in enumerate(options):
            letter = chr(ord("A") + i)
            prompt += f"{letter}) {option}\n"
    
    prompt += "\nProvide your answer."
    
    return prompt


def format_question_prompt_vn(question: str, options: list[str]) -> str:
    """
    Format question as user prompt for VN LLM.
    Uses vector-native format to encourage VN response.
    
    Args:
        question: Question text
        options: List of multiple choice options
    
    Returns:
        Formatted prompt in vector-native style
    """
    # Format options as VN parameters
    options_param = ",".join([f"O{i+1}:{opt}" for i, opt in enumerate(options)])
    letters = ",".join([chr(ord("A") + i) for i in range(len(options))])
    
    prompt = f"""●solve_reasoning|question:{question}|options:{options_param}|letters:{letters}|required:●answer|value:ANSWER_LETTER|format:vector_native_only|forbidden:english_reasoning"""
    
    return prompt

