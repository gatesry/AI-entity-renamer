"""Entity Renamer integration for Home Assistant."""

import json
import logging
import os

import homeassistant.helpers.entity_registry as er
import voluptuous as vol
from homeassistant.components import frontend
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Entity Renamer component."""
    _LOGGER.info("Starting AI Entity Renamer version %s", VERSION)
    hass.data[DOMAIN] = {}

    # Register the panel
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="AI Entity Renamer",
        sidebar_icon="mdi:rename-box",
        frontend_url_path="entity-renamer",
        require_admin=True,
        config={
            "_panel_custom": {
                "name": "entity-renamer-panel",
                "module_url": "/entity_renamer/entity-renamer-panel.js",
                "embed_iframe": True,
            }
        },
    )

    # Register API endpoints
    hass.http.register_view(EntityListView)
    hass.http.register_view(RenameEntityView)
    hass.http.register_view(OpenAISuggestionsView)
    hass.http.register_view(DeviceListView)
    hass.http.register_view(RenameDeviceView)
    hass.http.register_view(OpenAIDeviceSuggestionsView)

    # Register services
    hass.services.async_register(
        DOMAIN,
        "apply_rename",
        apply_rename_service,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("new_entity_id"): cv.string,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "apply_device_rename",
        apply_device_rename_service,
        schema=vol.Schema(
            {
                vol.Required("device_id"): cv.string,
                vol.Required("new_name"): cv.string,
            }
        ),
    )

    # Serve local files
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/entity_renamer", os.path.join(os.path.dirname(__file__), "frontend"), False
            )
        ]
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Entity Renamer from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


class EntityListView(HomeAssistantView):
    """View to handle Entity List requests."""

    url = "/api/entity_renamer/entities"
    name = "api:entity_renamer:entities"

    async def get(self, request):
        """Handle GET request for entity list."""
        hass = request.app["hass"]
        registry = er.async_get(hass)

        entities = []
        for entity_id, entity in registry.entities.items():
            # Get device info if available
            device_id = entity.device_id
            device_name = "No Device"
            area_id = None
            area_name = "No Area"

            if device_id:
                device_registry = async_get_device_registry(hass)
                device = device_registry.async_get(device_id)
                if device:
                    device_name = device.name or device.model or "Unknown Device"
                    area_id = device.area_id

            # Get area info if available
            if area_id:
                area_registry = async_get_area_registry(hass)
                area = area_registry.async_get_area(area_id)
                if area:
                    area_name = area.name

            entities.append(
                {
                    "entity_id": entity_id,
                    "name": entity.name or entity_id.split(".")[-1],
                    "device_name": device_name,
                    "area_name": area_name,
                    "original_name": entity.original_name,
                }
            )

        return self.json(entities)


class DeviceListView(HomeAssistantView):
    """View to handle Device List requests."""

    url = "/api/entity_renamer/devices"
    name = "api:entity_renamer:devices"

    async def get(self, request):
        """Handle GET request for device list."""
        hass = request.app["hass"]
        device_registry = async_get_device_registry(hass)
        area_registry = async_get_area_registry(hass)

        devices = []
        for device_id, device in device_registry.devices.items():
            area_name = "No Area"
            if device.area_id:
                area = area_registry.async_get_area(device.area_id)
                if area:
                    area_name = area.name
            devices.append(
                {
                    "id": device_id,
                    "name": device.name or device.model or "Unknown Device",
                    "manufacturer": device.manufacturer or "",
                    "model": device.model or "",
                    "area_name": area_name,
                }
            )

        return self.json(devices)


class RenameEntityView(HomeAssistantView):
    """View to handle Entity Rename requests."""

    url = "/api/entity_renamer/rename"
    name = "api:entity_renamer:rename"

    async def post(self, request):
        """Handle POST request for renaming entities."""
        hass = request.app["hass"]
        data = await request.json()

        entity_id = data.get("entity_id")
        new_entity_id = data.get("new_entity_id")
        new_name = data.get("new_name")

        if not entity_id or not new_entity_id:
            return self.json(
                {"success": False, "error": "Missing entity_id or new_entity_id"},
                status_code=400,
            )

        registry = er.async_get(hass)
        try:
            update_kwargs = {"new_entity_id": new_entity_id}
            if new_name:
                update_kwargs["name"] = new_name
            registry.async_update_entity(entity_id, **update_kwargs)
            return self.json({"success": True})
        except Exception as e:
            _LOGGER.error("Error renaming entity: %s", e)
            return self.json({"success": False, "error": str(e)}, status_code=500)


class RenameDeviceView(HomeAssistantView):
    """View to handle Device Rename requests."""

    url = "/api/entity_renamer/rename_device"
    name = "api:entity_renamer:rename_device"

    async def post(self, request):
        """Handle POST request for renaming devices."""
        hass = request.app["hass"]
        data = await request.json()

        device_id = data.get("device_id")
        new_name = data.get("new_name")

        if not device_id or new_name is None:
            return self.json(
                {"success": False, "error": "Missing device_id or new_name"},
                status_code=400,
            )

        registry = async_get_device_registry(hass)
        try:
            registry.async_update_device(device_id, name=new_name)
            return self.json({"success": True})
        except Exception as e:
            _LOGGER.error("Error renaming device: %s", e)
            return self.json({"success": False, "error": str(e)}, status_code=500)


class OpenAISuggestionsView(HomeAssistantView):
    """View to handle OpenAI Suggestions requests."""

    url = "/api/entity_renamer/suggest"
    name = "api:entity_renamer:suggest"

    async def post(self, request):
        """Handle POST request for OpenAI suggestions."""
        hass = request.app["hass"]
        data = await request.json()

        entities = data.get("entities", [])

        if not entities:
            return self.json({"success": False, "error": "No entities provided"}, status_code=400)

        try:
            import openai

            # Get API key from config
            config_entries = hass.config_entries.async_entries(DOMAIN)
            if not config_entries:
                return self.json(
                    {"success": False, "error": "Integration not configured"}, status_code=400
                )

            api_key = config_entries[0].data.get("api_key")
            if not api_key:
                return self.json(
                    {"success": False, "error": "OpenAI API key not configured"}, status_code=400
                )

            # Initialize client with explicit parameters to avoid environment issues
            try:
                client = openai.OpenAI(api_key=api_key, timeout=30.0)
            except TypeError as init_error:
                # Fallbacks for older versions or environment issues
                _LOGGER.warning(
                    "OpenAI client init failed, trying alternative: %s",
                    init_error,
                )
                try:
                    client = openai.OpenAI(api_key=api_key)
                except TypeError as second_error:
                    _LOGGER.warning(
                        "OpenAI client init failed again, using basic HTTP client: %s",
                        second_error,
                    )
                    import httpx

                    client = openai.OpenAI(
                        api_key=api_key,
                        http_client=httpx.Client(timeout=30.0),
                    )

            # Prepare the prompt
            prompt = (
                "Suggest Home Assistant entity IDs following the official naming convention:\n"
                "- Format: `<domain>.<location_code>_<device_type>_<function>_<identifier>`\n"
                "- Use ONLY lowercase letters, numbers, and underscores\n"
                "- Do NOT start or end with underscores\n"
                "- Examples: 'light.kitchen_ceiling_main', 'sensor.bedroom_temp_primary'\n"
                "- Keep location codes short (living_room → living, master_bedroom → master)\n"
                "- Prioritize clarity and consistency over brevity\n"
                "Return only a JSON array of entity_id strings in the original order.\n\n"
            )

            for entity in entities:
                prompt += f"Entity ID: {entity['entity_id']}\n"
                prompt += f"Current Name: {entity['name']}\n"
                prompt += f"Device: {entity['device_name']}\n"
                prompt += f"Area: {entity['area_name']}\n"
                prompt += f"Domain: {entity['entity_id'].split('.')[0]}\n"
                prompt += "Goal: Create systematic entity_id for automations\n\n"

            # Call OpenAI API
            response = await hass.async_add_executor_job(
                lambda: client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a Home Assistant entity naming expert. Create technical entity IDs "
                                "following HA's strict naming conventions for use in automations and integrations. "
                                "Focus on machine-readability and systematic organization."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
            )

            # Parse the response
            try:
                content = response.choices[0].message.content
                # Extract JSON from the response
                import re

                json_match = re.search(r"\[.*\]", content, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group(0))
                else:
                    suggestions = json.loads(content)

                # Ensure we have the right number of suggestions
                if len(suggestions) != len(entities):
                    return self.json(
                        {"success": False, "error": "Received incorrect number of suggestions"},
                        status_code=500,
                    )

                # Combine original entities with suggestions
                result = []

                def _id_to_name(eid: str) -> str:
                    parts = eid.split(".", 1)
                    if len(parts) > 1:
                        name_part = parts[1]
                    else:
                        name_part = parts[0]
                    return " ".join(word.capitalize() for word in name_part.split("_"))

                for i, entity in enumerate(entities):
                    suggested_id = suggestions[i]
                    result.append(
                        {
                            **entity,
                            "suggested_id": suggested_id,
                            "suggested_name": _id_to_name(suggested_id),
                        }
                    )

                return self.json({"success": True, "suggestions": result})

            except json.JSONDecodeError:
                return self.json(
                    {"success": False, "error": "Failed to parse OpenAI response"}, status_code=500
                )

        except ImportError:
            return self.json(
                {"success": False, "error": "OpenAI package not installed"}, status_code=500
            )
        except Exception as e:
            _LOGGER.error("Error getting suggestions: %s", e)
            return self.json({"success": False, "error": str(e)}, status_code=500)


class OpenAIDeviceSuggestionsView(HomeAssistantView):
    """View to handle OpenAI Device Name Suggestions requests."""

    url = "/api/entity_renamer/suggest_device"
    name = "api:entity_renamer:suggest_device"

    async def post(self, request):
        """Handle POST request for device name suggestions."""
        hass = request.app["hass"]
        data = await request.json()

        devices = data.get("devices", [])

        if not devices:
            return self.json({"success": False, "error": "No devices provided"}, status_code=400)

        try:
            import openai

            config_entries = hass.config_entries.async_entries(DOMAIN)
            if not config_entries:
                return self.json(
                    {"success": False, "error": "Integration not configured"}, status_code=400
                )

            api_key = config_entries[0].data.get("api_key")
            if not api_key:
                return self.json(
                    {"success": False, "error": "OpenAI API key not configured"}, status_code=400
                )

            try:
                client = openai.OpenAI(api_key=api_key, timeout=30.0)
            except TypeError as init_error:
                _LOGGER.warning("OpenAI client init failed, trying alternative: %s", init_error)
                try:
                    client = openai.OpenAI(api_key=api_key)
                except TypeError as second_error:
                    _LOGGER.warning(
                        "OpenAI client init failed again, using basic HTTP client: %s",
                        second_error,
                    )
                    import httpx

                    client = openai.OpenAI(api_key=api_key, http_client=httpx.Client(timeout=30.0))

            prompt = (
                "Suggest human-readable device names for Home Assistant following these rules:\n"
                "- Use proper capitalization and spaces\n"
                "- Format: '[Location] [Device Type]' or '[Descriptive Name]'\n"
                "- Be concise but clear for UI display\n"
                "- Consider the device's physical location and purpose\n"
                "- Examples: 'Kitchen Light', 'Living Room Thermostat', 'Main Bedroom Motion Sensor'\n"
                "Return only a JSON array of device names in the original order.\n\n"
            )

            for device in devices:
                prompt += f"Device: {device['name']}\n"
                prompt += f"Manufacturer: {device.get('manufacturer', 'Unknown')}\n"
                prompt += f"Model: {device.get('model', 'Unknown')}\n"
                prompt += f"Area: {device.get('area_name', 'No Area')}\n"
                prompt += "Goal: Create a user-friendly name for dashboard display\n\n"

            response = await hass.async_add_executor_job(
                lambda: client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a Home Assistant device naming expert. Create user-friendly device names "
                                "that are clear, location-based, and suitable for UI display. Focus on human "
                                "readability over technical structure."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
            )

            try:
                content = response.choices[0].message.content
                import re

                json_match = re.search(r"\[.*\]", content, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group(0))
                else:
                    suggestions = json.loads(content)

                if len(suggestions) != len(devices):
                    return self.json(
                        {"success": False, "error": "Received incorrect number of suggestions"},
                        status_code=500,
                    )

                # Validate device name format
                def _validate_device_name(name: str) -> str:
                    """Ensure device name follows proper conventions."""
                    if not name or not isinstance(name, str):
                        return "Unnamed Device"

                    # Ensure proper capitalization
                    name = name.strip()
                    if name.islower():
                        name = " ".join(word.capitalize() for word in name.split())

                    return name

                result = []
                for i, device in enumerate(devices):
                    suggestion = suggestions[i]
                    if isinstance(suggestion, dict):
                        suggestion = (
                            suggestion.get("name")
                            or suggestion.get("suggested_name")
                            or next(iter(suggestion.values()), "")
                        )

                    # Add validation
                    validated_name = _validate_device_name(suggestion)
                    result.append({**device, "suggested_name": validated_name})

                return self.json({"success": True, "suggestions": result})

            except json.JSONDecodeError:
                return self.json(
                    {"success": False, "error": "Failed to parse OpenAI response"}, status_code=500
                )

        except ImportError:
            return self.json(
                {"success": False, "error": "OpenAI package not installed"}, status_code=500
            )
        except Exception as e:
            _LOGGER.error("Error getting device suggestions: %s", e)
            return self.json({"success": False, "error": str(e)}, status_code=500)


async def apply_rename_service(hass, service):
    """Apply rename service call."""
    entity_id = service.data.get("entity_id")
    new_entity_id = service.data.get("new_entity_id")
    new_name = service.data.get("new_name")

    registry = er.async_get(hass)
    update_kwargs = {"new_entity_id": new_entity_id}
    if new_name:
        update_kwargs["name"] = new_name
    registry.async_update_entity(entity_id, **update_kwargs)


async def apply_device_rename_service(hass, service):
    """Apply device rename service call."""
    device_id = service.data.get("device_id")
    new_name = service.data.get("new_name")

    registry = async_get_device_registry(hass)
    registry.async_update_device(device_id, name=new_name)
