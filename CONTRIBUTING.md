# Contributing to QuantContext

Thanks for your interest in contributing to QuantContext!

## Development Setup

```bash
git clone https://github.com/jihjihk/quantcontext-mcp-server.git
cd quantcontext-mcp-server
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running Tests

```bash
python tests/test_tools.py
```

## Adding a New Screen Type

1. Add the skill to `engine/skills/pipeline_skills/registry.py`
2. Add config documentation to `SCREEN_CONFIG_HELP` in `server.py`
3. Update `docs/tools.md` with parameter reference
4. Add a test case to `tests/test_tools.py`

## Code Style

- Python 3.10+ type hints everywhere
- Docstrings on all public functions
- JSON output must have no NaN values (use `None`)
- Error responses must include an `"error"` key with a helpful message

## Pull Requests

- One feature per PR
- Include test coverage
- Update docs if adding or changing tool parameters
