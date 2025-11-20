"""
Test script demonstrating hybrid parser functionality.

The hybrid parser preserves prose while parsing compliant vector-native operations,
enabling token reduction from structured operations without losing necessary context.
"""

from vector_native import (
    parse_vector_native_hybrid,
    parse_with_fallback,
    extract_operations,
    extract_prose,
    ParsedOperation,
)


def test_hybrid_parsing():
    """Test hybrid parser with mixed content."""
    
    # Example 1: Mixed vector-native operations and prose
    mixed_output = """
    Here's the analysis you requested:
    
    ●analyze|dataset:Q4_sales|metrics:revenue,profit|status:complete
    ●create_report|format:pdf|sections:summary,trends|status:complete
    
    Note: The profit margin calculation uses the standard formula.
    
    ●schedule_update|frequency:15min|priority:high
    
    Additional context: This report will be sent to stakeholders.
    """
    
    print("=" * 80)
    print("TEST 1: Mixed Vector-Native + Prose")
    print("=" * 80)
    print(f"\nInput:\n{mixed_output}\n")
    
    result = parse_vector_native_hybrid(mixed_output)
    
    print(f"Parsed {len(result)} items:")
    for i, item in enumerate(result, 1):
        if isinstance(item, ParsedOperation):
            print(f"  [{i}] OPERATION: {item.operation}")
            print(f"      Params: {item.params}")
            print(f"      Attention: {item.attention}")
        else:
            print(f"  [{i}] PROSE: {item[:60]}...")
    
    operations = extract_operations(result)
    prose = extract_prose(result)
    
    print(f"\nSummary:")
    print(f"  Operations parsed: {len(operations)}")
    print(f"  Prose lines preserved: {len(prose)}")
    
    # Example 2: Using parse_with_fallback with hybrid=True
    print("\n" + "=" * 80)
    print("TEST 2: parse_with_fallback(hybrid=True)")
    print("=" * 80)
    
    fallback_result = parse_with_fallback(mixed_output, hybrid=True)
    print(f"\nFormat: {fallback_result['format']}")
    print(f"Has operations: {any(isinstance(item, ParsedOperation) for item in fallback_result['parsed'])}")
    print(f"Has prose: {any(isinstance(item, str) for item in fallback_result['parsed'])}")
    
    # Example 3: Pure prose (should be preserved)
    print("\n" + "=" * 80)
    print("TEST 3: Pure Prose (No Operations)")
    print("=" * 80)
    
    pure_prose = """
    This is a natural language explanation.
    It doesn't follow vector-native syntax.
    But it should still be preserved.
    """
    
    try:
        result = parse_vector_native_hybrid(pure_prose)
        print(f"\nParsed {len(result)} prose lines")
        for i, line in enumerate(result, 1):
            print(f"  [{i}] {line[:60]}...")
    except Exception as e:
        print(f"\nError: {e}")
    
    # Example 4: Pure vector-native (should parse normally)
    print("\n" + "=" * 80)
    print("TEST 4: Pure Vector-Native (No Prose)")
    print("=" * 80)
    
    pure_vn = """
    ●analyze|dataset:Q4|status:complete
    ●create_report|format:pdf|status:complete
    """
    
    result = parse_vector_native_hybrid(pure_vn)
    print(f"\nParsed {len(result)} operations")
    for i, op in enumerate(result, 1):
        if isinstance(op, ParsedOperation):
            print(f"  [{i}] {op.operation}: {op.params}")
    
    # Example 5: Prose with distribution symbols (should be preserved)
    print("\n" + "=" * 80)
    print("TEST 5: Prose with Distribution Symbols")
    print("=" * 80)
    
    prose_with_symbols = """
    The probability distribution ⟨⟩ shows high confidence.
    ●analyze|dataset:test|confidence:high
    The angle ∠ between vectors is 45 degrees.
    """
    
    result = parse_vector_native_hybrid(prose_with_symbols)
    print(f"\nParsed {len(result)} items")
    for i, item in enumerate(result, 1):
        if isinstance(item, ParsedOperation):
            print(f"  [{i}] OPERATION: {item.operation}")
        else:
            print(f"  [{i}] PROSE: {item.strip()}")


if __name__ == "__main__":
    test_hybrid_parsing()
    print("\n✅ Hybrid parser tests complete!")

