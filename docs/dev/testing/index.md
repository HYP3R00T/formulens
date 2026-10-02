# Testing

This section documents how tests are structured, written, and run in this repository.
Formulens has no committed test suite yet. These pages describe conventions for
adding tests. The current CI runs repository checks through prek.

## Test Types

| Type | Purpose | Runs in CI |
|---|---|---|
| [Unit](unit-tests.md) | Test a single function or class in isolation | Yes |
| [Integration](integration-tests.md) | Test multiple components together | Optional |
| [Property-based](property-tests.md) | Verify invariants across many generated inputs | Optional |
| [Optional markers](optional-markers.md) | Tests that are slow or depend on optional local setup | Optional |

## Running Tests

Run tests from the repository root.

| Command | What it runs |
|---|---|
| `uv run pytest --cov --cov-report=term-missing --cov-fail-under=80` | Test command once pytest, pytest-cov, and tests have been added |

## File Layout

When tests are added, use a standard `tests/` layout:

```text
tests/
  conftest.py
  unit/
    test_example.py
  integration/
    test_example_flow.py
  property/
    test_example_properties.py
```

Keep tests small, deterministic, and independent of network access by default.

## Related

- [Unit Tests](unit-tests.md)
- [Integration Tests](integration-tests.md)
- [Property-Based Tests](property-tests.md)
- [Optional Test Markers](optional-markers.md)
- [Developer Setup](../setup/index.md)
