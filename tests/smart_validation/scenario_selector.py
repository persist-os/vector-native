"""
Scenario Selector for Smart Validation Framework

Implements stratified sampling to select 15 representative scenarios covering:
- Short/medium/long prompts (5 each)
- Different domains (analysis, creation, configuration, workflows)
- Edge cases (ambiguous, nested, domain-specific)
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from vector_native import count_tokens


def classify_prompt_length(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Classify prompt length based on token count.
    
    Args:
        prompt: The prompt text
        model: Model name for token counting
    
    Returns:
        "short", "medium", or "long"
    """
    token_count = count_tokens(prompt, model)
    
    if token_count < 50:
        return "short"
    elif token_count < 200:
        return "medium"
    else:
        return "long"


def infer_domain(scenario: Dict[str, Any]) -> str:
    """
    Infer domain from scenario name or prompt content.
    
    Args:
        scenario: Scenario dict with "name" and "prompt" fields
    
    Returns:
        Domain: "analysis", "creation", "config", "workflow", or "unknown"
    """
    name_lower = scenario.get("name", "").lower()
    prompt_lower = scenario.get("prompt", "").lower()
    combined = f"{name_lower} {prompt_lower}"
    
    # Domain keywords
    if any(kw in combined for kw in ["analyze", "analysis", "data", "report", "metrics"]):
        return "analysis"
    elif any(kw in combined for kw in ["create", "generate", "build", "make", "widget"]):
        return "creation"
    elif any(kw in combined for kw in ["config", "configure", "setup", "settings", "policy"]):
        return "config"
    elif any(kw in combined for kw in ["workflow", "process", "task", "schedule", "automate"]):
        return "workflow"
    else:
        return "unknown"


def is_edge_case(scenario: Dict[str, Any]) -> bool:
    """
    Determine if scenario is an edge case.
    
    Args:
        scenario: Scenario dict
    
    Returns:
        True if edge case, False otherwise
    """
    # Check metadata if available
    if "edge_case" in scenario:
        return scenario["edge_case"]
    
    # Infer from characteristics
    prompt = scenario.get("prompt", "")
    name = scenario.get("name", "").lower()
    
    # Edge case indicators
    edge_indicators = [
        "extremely long",
        "comprehensive",
        "multi-task",
        "ambiguous",
        "nested",
        "complex",
    ]
    
    return any(indicator in name or indicator in prompt.lower() for indicator in edge_indicators)


def select_stratified_scenarios(
    scenarios: List[Dict[str, Any]],
    target_count: int = 15,
    model: str = "gpt-4o-mini"
) -> List[Dict[str, Any]]:
    """
    Select representative scenarios using stratified sampling.
    
    Args:
        scenarios: List of scenario dicts
        target_count: Number of scenarios to select (default: 15)
        model: Model name for token counting
    
    Returns:
        List of selected scenario dicts
    """
    # Classify all scenarios
    classified = []
    for scenario in scenarios:
        # Add metadata if not present
        if "length" not in scenario:
            scenario["length"] = classify_prompt_length(scenario.get("prompt", ""), model)
        if "domain" not in scenario:
            scenario["domain"] = infer_domain(scenario)
        if "edge_case" not in scenario:
            scenario["edge_case"] = is_edge_case(scenario)
        
        classified.append(scenario)
    
    # Stratify by length (target: 5 short, 5 medium, 5 long)
    short_scenarios = [s for s in classified if s["length"] == "short"]
    medium_scenarios = [s for s in classified if s["length"] == "medium"]
    long_scenarios = [s for s in classified if s["length"] == "long"]
    
    # Target distribution: 5 each
    per_length = target_count // 3
    remainder = target_count % 3
    
    selected = []
    
    # Select from each length category, ensuring domain diversity
    for length_group, count in [
        (short_scenarios, per_length + (1 if remainder > 0 else 0)),
        (medium_scenarios, per_length + (1 if remainder > 1 else 0)),
        (long_scenarios, per_length),
    ]:
        # Group by domain
        by_domain = {}
        for scenario in length_group:
            domain = scenario["domain"]
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(scenario)
        
        # Select from each domain, prioritizing edge cases
        selected_from_length = []
        domains = list(by_domain.keys())
        
        # Round-robin selection across domains
        domain_idx = 0
        while len(selected_from_length) < count and length_group:
            if not domains:
                # Fallback: select remaining from any domain
                remaining = [s for s in length_group if s not in selected_from_length]
                if remaining:
                    selected_from_length.append(remaining[0])
                break
            
            domain = domains[domain_idx % len(domains)]
            if domain in by_domain and by_domain[domain]:
                # Prioritize edge cases
                edge_cases = [s for s in by_domain[domain] if s["edge_case"]]
                regular = [s for s in by_domain[domain] if not s["edge_case"]]
                
                if edge_cases:
                    selected_from_length.append(edge_cases.pop(0))
                elif regular:
                    selected_from_length.append(regular.pop(0))
                else:
                    domains.remove(domain)
                    continue
                
                # Remove from domain group
                by_domain[domain] = [s for s in by_domain[domain] if s not in selected_from_length]
                if not by_domain[domain]:
                    domains.remove(domain)
            
            domain_idx += 1
        
        selected.extend(selected_from_length)
    
    # Ensure we have exactly target_count
    if len(selected) > target_count:
        selected = selected[:target_count]
    elif len(selected) < target_count:
        # Fill remaining from any category
        remaining = [s for s in classified if s not in selected]
        selected.extend(remaining[:target_count - len(selected)])
    
    return selected


def load_and_select_scenarios(
    scenarios_file: Optional[Path] = None,
    target_count: int = 15,
    model: str = "gpt-4o-mini"
) -> List[Dict[str, Any]]:
    """
    Load scenarios from JSON file and select representative subset.
    
    Args:
        scenarios_file: Path to scenarios.json (default: auto-detect)
        target_count: Number of scenarios to select
        model: Model name for token counting
    
    Returns:
        List of selected scenario dicts with metadata
    """
    if scenarios_file is None:
        # Auto-detect scenarios file
        script_dir = Path(__file__).parent.parent
        scenarios_file = script_dir / "test_cases" / "scenarios.json"
    
    # Load scenarios
    with open(scenarios_file, "r") as f:
        all_scenarios = json.load(f)
    
    # Select stratified subset
    selected = select_stratified_scenarios(all_scenarios, target_count, model)
    
    return selected


if __name__ == "__main__":
    # Test scenario selector
    selected = load_and_select_scenarios(target_count=15)
    
    print(f"Selected {len(selected)} scenarios:")
    print("\nBy length:")
    length_counts = {}
    domain_counts = {}
    edge_case_count = 0
    
    for scenario in selected:
        length = scenario.get("length", "unknown")
        domain = scenario.get("domain", "unknown")
        is_edge = scenario.get("edge_case", False)
        
        length_counts[length] = length_counts.get(length, 0) + 1
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if is_edge:
            edge_case_count += 1
    
    print(f"  Short: {length_counts.get('short', 0)}")
    print(f"  Medium: {length_counts.get('medium', 0)}")
    print(f"  Long: {length_counts.get('long', 0)}")
    
    print("\nBy domain:")
    for domain, count in domain_counts.items():
        print(f"  {domain}: {count}")
    
    print(f"\nEdge cases: {edge_case_count}")
    
    print("\nSelected scenarios:")
    for i, scenario in enumerate(selected, 1):
        print(f"{i}. {scenario['name']} ({scenario.get('length', 'unknown')}, {scenario.get('domain', 'unknown')})")

