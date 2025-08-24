# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Entity Renamer is a Home Assistant custom integration that provides bulk entity renaming capabilities with AI-powered suggestions using OpenAI's API. The integration adds a dedicated sidebar panel and REST API endpoints for managing entity names.

## Development Commands

### Testing
```bash
# Run tests with coverage
pytest --cov=custom_components/entity_renamer --cov-report=xml

# Run tests only
pytest
```

### Code Quality
```bash
# Format code with Black (line length 100)
black --line-length 100 custom_components/entity_renamer tests/

# Sort imports with isort (Black profile)
isort --profile black --line-length 100 custom_components/entity_renamer tests/

# Lint with flake8
flake8 custom_components/entity_renamer tests/

# Lint with pylint (line length 100)
pylint --max-line-length=100 custom_components/entity_renamer/

# Type checking with mypy
mypy custom_components/entity_renamer/

# Run pre-commit hooks
pre-commit run --all-files
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements_dev.txt

# Install the integration in development mode
pip install -e .
```

## Architecture

### Core Components

- **`__init__.py`**: Main integration setup, registers panel, API views, and services
- **`config_flow.py`**: Configuration flow for OpenAI API key setup
- **`const.py`**: Constants and version management (reads from manifest.json)
- **`manifest.json`**: Home Assistant integration metadata
- **`services.yaml`**: Service definitions for programmatic access

### Frontend
- **`frontend/entity-renamer-panel.js`**: Main JavaScript panel implementation
- **`frontend/index.html`**: Panel HTML template

### API Endpoints
- `/api/entity_renamer/entities` - GET: List all entities with metadata
- `/api/entity_renamer/rename` - POST: Rename individual entities
- `/api/entity_renamer/suggest` - POST: Get OpenAI name suggestions

### Services
- `entity_renamer.apply_rename`: Service call for programmatic entity renaming

## Key Dependencies

- `openai>=1.0.0`: OpenAI API client for name suggestions
- Home Assistant core dependencies: `voluptuous`, `aiohttp`

## Testing Architecture

Tests use pytest with Home Assistant test framework:
- Mock objects for HA registries (entity, device, area)
- Fixtures in `conftest.py` for consistent test setup
- Coverage reporting configured for CI/CD

## Configuration

The integration uses Home Assistant's config entry system to store the OpenAI API key securely. Configuration is handled through the standard HA integration setup flow.

## Home Assistant Integration Patterns

This integration follows standard HA custom component patterns:
- Uses `async_setup()` and `async_setup_entry()` for initialization
- Registers frontend panels with `frontend.async_register_built_in_panel()`
- Implements `HomeAssistantView` classes for REST API endpoints
- Uses entity/device/area registries for metadata lookup
- Follows HA service registration patterns with schema validation