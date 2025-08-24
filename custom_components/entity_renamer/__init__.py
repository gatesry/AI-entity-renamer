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

    # Register services
    hass.services.async_register(
        DOMAIN,
        "apply_rename",
        apply_rename_service,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.string,
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


class RenameEntityView(HomeAssistantView):
    """View to handle Entity Rename requests."""

    url = "/api/entity_renamer/rename"
    name = "api:entity_renamer:rename"

    async def post(self, request):
        """Handle POST request for renaming entities."""
        hass = request.app["hass"]
        data = await request.json()

        entity_id = data.get("entity_id")
        new_name = data.get("new_name")

        if not entity_id or not new_name:
            return self.json(
                {"success": False, "error": "Missing entity_id or new_name"}, status_code=400
            )

        registry = er.async_get(hass)
        try:
            registry.async_update_entity(entity_id, name=new_name)
            return self.json({"success": True})
        except Exception as e:
            _LOGGER.error("Error renaming entity: %s", e)
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
                "Suggest concise Home Assistant entity IDs using "
                "`<domain>.<location_code>_<device_type>_<function>_<identifier>`. "
                "Use lowercase letters, numbers and underscores, "
                "and do not begin or end an ID with an underscore. "
                "Return only a JSON array of `entity_id` strings "
                "in the original order.\n\n"
            )

            for entity in entities:
                prompt += f"Entity ID: {entity['entity_id']}\n"
                prompt += f"Current Name: {entity['name']}\n"
                prompt += f"Device: {entity['device_name']}\n"
                prompt += f"Area: {entity['area_name']}\n\n"

            # Call OpenAI API
            response = await hass.async_add_executor_job(
                lambda: client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant that suggests concise Home Assistant "
                                "entity IDs following a standardized naming template."
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
                for i, entity in enumerate(entities):
                    result.append({**entity, "suggested_id": suggestions[i]})

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


async def apply_rename_service(hass, service):
    """Apply rename service call."""
    entity_id = service.data.get("entity_id")
    new_name = service.data.get("new_name")

    registry = er.async_get(hass)
    registry.async_update_entity(entity_id, name=new_name)
