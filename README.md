# AI Entity Renamer for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A custom component for Home Assistant that allows you to bulk rename entities and devices using OpenAI suggestions.

![AI Entity Renamer Screenshot](docs/screenshot.png)

## Overview

Managing entity names in Home Assistant can become tedious as your smart home grows. This integration provides a user-friendly interface to:

- View all entities with their area, device, name, and entity ID
- View devices with area, manufacturer and model information
- Entities are grouped by area with collapsible headers for easier navigation
- Filter and search for specific entities
- Select multiple entities or devices for bulk renaming
- Get AI-powered entity ID or device name suggestions from OpenAI
- Apply suggested IDs and friendly names or device names individually or all at once

The integration adds a dedicated sidebar icon for easy access and provides a clean, intuitive interface for managing your entity names.

## Features

- **Entity Browser**: View and filter all entities in your Home Assistant instance
- **Device Browser**: Review devices with area, manufacturer and model details
- **Tabbed Interface**: Switch between dedicated tabs for entities and devices
- **Collapsible Area Groups**: Entities are grouped by area with expandable headers to keep large lists manageable
- **Bulk Selection**: Select multiple entities or devices for batch operations
- **AI Suggestions**: Get intelligent naming suggestions from OpenAI
- **Bulk Apply**: Apply all suggestions at once or selectively choose which to apply
- **Sidebar Integration**: Access via a dedicated sidebar icon
- **Service API**: Programmatically rename entities or devices via service calls

## Installation

### HACS Installation (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add the URL `https://github.com/gatesry/AI-entity-renamer` and select "Integration" as the category
5. Click "Add"
6. Search for "AI Entity Renamer" in HACS and install it
7. Restart Home Assistant

Once installed, the integration will automatically maintain its version information and can be updated through HACS when new versions are released.

### Manual Installation

1. Download the latest release from the GitHub repository
2. Create a folder called `entity_renamer` in your `custom_components` directory
3. Extract the contents of the release into the `entity_renamer` folder
4. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration" and search for "AI Entity Renamer"
3. Follow the configuration steps to add your OpenAI API key

## Usage

1. After installation, you'll see a new "AI Entity Renamer" icon in your Home Assistant sidebar
2. Click on it to open the AI Entity Renamer interface
3. Use the **Entities** and **Devices** tabs to browse for items you want to rename
4. Select the entities or devices you want to rename
5. Click "Get ID Suggestions" or "Get Name Suggestions" to receive AI-generated suggestions
6. Review the suggestions and apply them individually or all at once. Applying an entity suggestion updates both the entity ID and its friendly name; applying a device suggestion updates the device name.

### How naming suggestions work

When you request suggestions, the integration sends each selected entity's
ID, current name, device and area to OpenAI. The model is prompted to return
concise IDs using the template:

```
<domain>.<location_code>_<device_type>_<function>_<identifier>
```

IDs use lowercase letters, numbers and underscores without leading or trailing
underscores. The API responds with a JSON array of entity IDs in the same order
as the input. The panel displays these IDs along with a readable name generated
from each ID so you can confirm the change before applying it.

## Requirements

- Home Assistant 2023.3.0 or newer
- An OpenAI API key

## Privacy

This integration sends entity or device information (such as entity ID, current name, device name, manufacturer, model, and area name) to OpenAI to generate name suggestions. No other data from your Home Assistant instance is shared.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Brands Compliance

To ensure your integration's logo and UI elements display correctly in Home Assistant, you must register your integration with the [home-assistant/brands](https://github.com/home-assistant/brands) repository. See the official documentation for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
