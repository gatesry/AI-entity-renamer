# AGENTS.md

This file provides instructions for AI agents working with the **AI Entity Renamer for Home Assistant** codebase.

## Project Overview

This is a custom component for Home Assistant that allows users to bulk rename entities using AI-powered suggestions from OpenAI. The integration provides a user-friendly interface within Home Assistant to manage entity names efficiently.

- **Backend:** Python (Home Assistant custom component)
- **Frontend:** JavaScript (a simple panel)
- **Repository:** `https://github.com/gatesry/AI-entity-renamer`

## Development Setup

To get started with development, you'll need to set up a Python environment and install the required dependencies.

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    The development dependencies, including tools for testing and linting, are listed in `requirements_dev.txt`.
    ```bash
    pip install -r requirements_dev.txt
    ```

## Running Tests

This project uses `pytest` for testing. The tests are located in the `tests/` directory.

To run the tests and generate a coverage report, use the following command:

```bash
pytest --cov=custom_components/entity_renamer --cov-report=xml
```

**Important:** Before submitting any changes, please ensure that all tests pass. If you add new features, please include corresponding tests.

## Coding Conventions

Please adhere to the following coding conventions to maintain code quality and consistency.

- **Formatting:** The project uses `black` for code formatting and `isort` for sorting imports. Please run these tools before committing your changes.
- **Linting:** `pylint` is used for linting.
- **Line Length:** The maximum line length is 100 characters.
- **Configuration:** All formatting and linting tools are configured in the `pyproject.toml` file.

## Project Structure

- `custom_components/entity_renamer/`: The main source code for the Home Assistant integration.
  - `__init__.py`: The main entry point of the integration.
  - `config_flow.py`: Handles the configuration flow for the integration.
  - `frontend/`: Contains the JavaScript frontend files.
- `tests/`: Contains the Python tests for the integration.
- `pyproject.toml`: Contains project metadata and tool configurations.

## Frontend Development

The frontend is a simple JavaScript panel located in `custom_components/entity_renamer/frontend/`. While there are no automated frontend tests, please ensure that any changes to the frontend are manually tested for functionality and visual consistency.

## Submission Checklist

Before submitting a pull request, please ensure you have completed the following:

- [ ] All Python tests pass (`pytest`).
- [ ] The code is formatted with `black` and `isort`.
- [ ] New features are accompanied by corresponding tests.
- [ ] The `README.md` is updated if any user-facing changes were made.
- [ ] The `CHANGELOG.md` is updated with a summary of changes.