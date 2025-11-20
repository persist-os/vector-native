# Test Cases

This directory contains test scenarios for token reduction testing.

## Adding New Scenarios

To add a new test scenario, edit `scenarios.json` and add a new object to the array:

```json
{
  "name": "Your Scenario Name",
  "prompt": "The user prompt to test",
  "expected_operations": ["operation1", "operation2", "operation3"]
}
```

### Fields

- **name**: Descriptive name for the scenario (e.g., "Short Analysis", "Long Data Processing")
- **prompt**: The user prompt text to test. Can be multi-line using `\n` for line breaks
- **expected_operations**: List of operations/keywords expected in the response (used for validation)

### Example

```json
{
  "name": "Customer Support Query",
  "prompt": "Help me resolve an issue with my account. User ID is 12345. They're reporting login problems.",
  "expected_operations": ["help", "resolve", "account", "login"]
}
```

The scenarios are automatically loaded by `test_token_reduction.py` when tests run.

