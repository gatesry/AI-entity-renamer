# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Device renaming support with new backend API endpoints
- OpenAI-powered device name suggestions
- Frontend table for selecting devices and applying name suggestions
- `apply_device_rename` service for programmatic device updates
- Separate tabs for entity and device renaming in the web interface
- Development requirements now include Home Assistant and pytest-asyncio for testing

## [1.0.0] - 2025-04-22

### Added
- Initial release of AI Entity Renamer
- View all entities with their area, device, name, and entity ID
- Filter entities by area, device, or search term
- Select multiple entities for bulk renaming
- Get AI-powered name suggestions from OpenAI
- Apply suggested names individually or all at once
- Access via a dedicated sidebar icon
- Service API for programmatically renaming entities
