# AI Entity Renamer for Home Assistant

A custom component for Home Assistant that allows you to bulk rename entities using OpenAI suggestions.

## Features

- View all entities in your Home Assistant instance with their area, device, name, and entity ID
- Filter entities by area, device, or search term
- Select multiple entities for bulk renaming
- Get AI-powered entity ID suggestions from OpenAI following a structured naming template
- Apply suggested IDs and friendly names individually or all at once
- Access via a dedicated sidebar icon

## Installation

### HACS Installation (Recommended)

This integration is fully compatible with [HACS](https://hacs.xyz/).

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add the URL `https://github.com/terkilddk/AI-entity-renamer` and select "Integration" as the category
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
3. Browse or search for entities you want to rename
4. Select the entities you want to rename
5. Click "Get ID Suggestions" to receive AI-generated entity ID suggestions
6. Review the suggestions and apply them individually or all at once. When a suggestion is applied, the entity's ID and friendly name are updated to match the template.

### How naming suggestions work

The integration submits each selected entity's ID, friendly name, device and
area to OpenAI. The model is instructed to produce entity IDs in the form:

```
<domain>.<location_code>_<device_type>_<function>_<identifier>
```

Identifiers use lowercase letters, numbers and underscores with no leading or
trailing underscore. OpenAI returns a JSON array of IDs in the same order,
which are shown in the UI together with a human-readable name generated from
each ID so you can review the proposed change.

## Services

The integration provides the following service:

- `entity_renamer.apply_rename`: Rename a specific entity
  - `entity_id`: The current entity ID
  - `new_entity_id`: The new entity ID
  - `new_name` (optional): The friendly name to apply

Example service call:

```yaml
service: entity_renamer.apply_rename
data:
  entity_id: light.living_room
  new_entity_id: light.lr_ceiling_light
  new_name: "LR Ceiling Light"
```

## Versioning

The current version of this integration is managed in multiple places for consistency:
- `custom_components/entity_renamer/manifest.json`
- `version.json`
- `CHANGELOG.md`

Version updates are handled automatically during releases. You can always find the current version in the Home Assistant integrations page or in the files above.

## Requirements

- Home Assistant 2023.3.0 or newer
- An OpenAI API key

## Privacy

This integration sends entity information (entity ID, current name, device name, and area name) to OpenAI to generate name suggestions. No other data from your Home Assistant instance is shared.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

## Brands Compliance

To ensure your integration's logo and UI elements display correctly in Home Assistant, you must register your integration with the [home-assistant/brands](https://github.com/home-assistant/brands) repository. See the official documentation for details.

## License

This project is licensed under the MIT License.
