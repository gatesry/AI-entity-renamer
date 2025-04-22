# Entity Renamer for Home Assistant

A custom component for Home Assistant that allows you to bulk rename entities using OpenAI suggestions.

## Features

- View all entities in your Home Assistant instance with their area, device, name, and entity ID
- Filter entities by area, device, or search term
- Select multiple entities for bulk renaming
- Get AI-powered name suggestions from OpenAI
- Apply suggested names individually or all at once
- Access via a dedicated sidebar icon

## Installation

### HACS Installation (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add the URL of this repository and select "Integration" as the category
5. Click "Add"
6. Search for "Entity Renamer" in HACS and install it
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from the GitHub repository
2. Create a folder called `entity_renamer` in your `custom_components` directory
3. Extract the contents of the release into the `entity_renamer` folder
4. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration" and search for "Entity Renamer"
3. Follow the configuration steps to add your OpenAI API key

## Usage

1. After installation, you'll see a new "Entity Renamer" icon in your Home Assistant sidebar
2. Click on it to open the Entity Renamer interface
3. Browse or search for entities you want to rename
4. Select the entities you want to rename
5. Click "Get Name Suggestions" to receive AI-generated name suggestions
6. Review the suggestions and apply them individually or all at once

## Services

The integration provides the following service:

- `entity_renamer.apply_rename`: Rename a specific entity
  - `entity_id`: The entity ID to rename
  - `new_name`: The new name for the entity

Example service call:

```yaml
service: entity_renamer.apply_rename
data:
  entity_id: light.living_room
  new_name: Living Room Ceiling Light
```

## Requirements

- Home Assistant 2023.3.0 or newer
- An OpenAI API key

## Privacy

This integration sends entity information (entity ID, current name, device name, and area name) to OpenAI to generate name suggestions. No other data from your Home Assistant instance is shared.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License.
