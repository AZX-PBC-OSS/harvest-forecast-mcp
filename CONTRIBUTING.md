# Contributing to harvest-forecast-mcp

Thank you for your interest in contributing to harvest-forecast-mcp! We appreciate your time and effort in making this MCP server better for everyone.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

### Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AZX-PBC-OSS/harvest-forecast-mcp.git
   cd harvest-forecast-mcp
   ```

2. **Install dependencies:**

   This project uses `uv` for dependency management. Install development dependencies with:
   ```bash
   uv sync --group dev
   ```

   This will create a virtual environment and install all necessary dependencies including pytest, pyright, ruff, and other development tools.

## Running Tests

**IMPORTANT: Always use `uv run` to execute pytest and other development commands.**

Using `uv run` ensures that:
- Commands run in the correct virtual environment
- All dependencies are properly resolved
- You're using the exact versions specified in the project
- No conflicts with globally installed packages

### Test Commands

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_server.py

# Run specific test function
uv run pytest tests/test_server.py::test_list_people

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=harvest_forecast_mcp --cov-report=html

# Run tests matching a pattern
uv run pytest -k "test_assignment"

# Run tests with output from print statements
uv run pytest -s
```

### Understanding Test Output

The project is configured with the following pytest settings (in `pyproject.toml`):
- `asyncio_mode = "auto"` — async tests run without explicit markers
- `--strict-markers` and `--strict-config` — fail on unknown markers/config
- `--timeout=5` — individual test timeout of 5 seconds
- Coverage is collected for the `harvest_forecast_mcp` package
- HTML coverage reports are generated in `htmlcov/`
- Coverage reports exclude test files and implementation details

## Code Quality

### Type Checking

The project uses `pyright` for type checking:

```bash
# Run type checking
uv run pyright src/harvest_forecast_mcp

# Type check specific file
uv run pyright src/harvest_forecast_mcp/server.py
```

### Linting and Formatting

The project uses `ruff` for both linting and formatting:

```bash
# Check for linting issues
uv run ruff check src/harvest_forecast_mcp

# Auto-fix linting issues
uv run ruff check --fix src/harvest_forecast_mcp

# Format code
uv run ruff format src/harvest_forecast_mcp

# Check formatting without making changes
uv run ruff format --check src/harvest_forecast_mcp
```

### Running All Quality Checks

Before submitting a PR, run all quality checks:

```bash
# Run tests with coverage
uv run pytest

# Run type checking
uv run pyright src/harvest_forecast_mcp

# Run linting
uv run ruff check .

# Check formatting
uv run ruff format --check .
```

Or use the Makefile:

```bash
make test type-check lint format
```

## Making Changes

### Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

   Or for bug fixes:
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Make your changes:**
   - Write clear, readable code
   - Follow existing code patterns and conventions
   - Add type hints to all functions and methods
   - Keep functions focused and modular
   - Use the FastMCP framework decorators (`@mcp.tool()`) to expose new tools

3. **Write tests:**
   - Add tests in `tests/` for all new functionality
   - Use `respx` for HTTP mocking — no real network calls in tests
   - Test edge cases and error conditions
   - Run tests with `uv run pytest`

4. **Update documentation:**
   - Update README.md if adding new tools
   - Add the new tool to the tool list table in the README
   - Add docstrings to new functions and classes
   - Update type hints and examples

5. **Verify your changes:**
   ```bash
   # Run all tests
   uv run pytest

   # Check types
   uv run pyright src/harvest_forecast_mcp

   # Check linting
   uv run ruff check .

   # Check formatting
   uv run ruff format --check .
   ```

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass:**
   ```bash
   uv run pytest
   ```

2. **Ensure type checking passes:**
   ```bash
   uv run pyright src/harvest_forecast_mcp
   ```

3. **Ensure code is properly formatted:**
   ```bash
   uv run ruff format .
   uv run ruff check --fix .
   ```

4. **Verify coverage hasn't decreased:**
   ```bash
   uv run pytest --cov=harvest_forecast_mcp --cov-report=term-missing
   ```

### Submitting Your PR

1. **Push your branch:**
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Create a pull request on GitHub**

3. **In your PR description:**
   - Clearly describe what changes you made
   - Explain why the changes are needed
   - Reference any related issues
   - Include examples of new functionality (if applicable)
   - List any breaking changes

## Code Review

### What to Expect

- All changes must pass automated tests and type checking
- Code reviewers will check for:
  - Implementation correctness
  - Code clarity and maintainability
  - Adequate test coverage
  - Documentation completeness
  - Adherence to project conventions

- You may be asked to make revisions
- Reviews are constructive — they help improve code quality

### Addressing Feedback

When reviewers request changes:

1. Make the requested changes in your branch
2. Run tests again: `uv run pytest`
3. Push the updates: `git push origin feat/your-feature-name`
4. Respond to reviewer comments

## Development Tips

### Virtual Environment

The `uv run` command automatically manages the virtual environment. You don't need to manually activate it.

If you prefer to activate the environment manually:
```bash
# uv creates a .venv directory
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

However, we recommend using `uv run` for consistency.

### Interactive Testing

You can use `uv run python` to start a Python interpreter with the correct environment:

```bash
uv run python
```

Then test your changes interactively:

```python
from harvest_forecast_mcp.server import mcp

# Inspect registered tools
print(mcp.list_tools())
```

### Debugging Tests

To debug a specific test with pdb:

```bash
# Add breakpoint() in your test or code
# Then run with -s to see output
uv run pytest -s tests/test_server.py::test_specific_function
```

### Coverage Reports

After running tests with coverage, view the HTML report:

```bash
uv run pytest --cov=harvest_forecast_mcp --cov-report=html
# Open htmlcov/index.html in your browser
```

## Code Style Guidelines

### General Principles

- Write clear, self-documenting code
- Use meaningful variable and function names
- Keep functions short and focused (ideally under 50 lines)
- Avoid deep nesting (max 3–4 levels)
- Comments should explain "why", not "what"
- Use modern Python conventions (`X | None`, built-in generics, `pathlib`)

### Type Hints

Always use type hints on all public boundaries:

```python
# Good
def list_time_entries(self, from_date: str | None = None) -> list[dict[str, object]]:
    ...

# Bad
def list_time_entries(self, from_date=None):
    ...
```

### Docstrings

Use Google-style docstrings for public APIs:

```python
def list_time_entries() -> list[dict[str, object]]:
    """List time entries in the Harvest account.

    Returns:
        A list of time entries, fully paginated.

    Raises:
        HarvestAuthError: If the access token is invalid.
        HarvestHTTPError: If the API returns an error.
    """
```

## Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/AZX-PBC-OSS/harvest-forecast-mcp/discussions)
- **Bug Reports?** Open an [Issue](https://github.com/AZX-PBC-OSS/harvest-forecast-mcp/issues)
- **Feature Requests?** Open an [Issue](https://github.com/AZX-PBC-OSS/harvest-forecast-mcp/issues) with the `enhancement` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make harvest-forecast-mcp better for everyone. We appreciate your time and effort!
