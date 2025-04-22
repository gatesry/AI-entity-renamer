"""Tests for AI Entity Renamer integration."""
import pytest
from unittest.mock import patch, MagicMock

from homeassistant.setup import async_setup_component
from custom_components.entity_renamer import DOMAIN


async def test_setup(hass):
    """Test the setup of the integration."""
    with patch("custom_components.entity_renamer.frontend.async_register_built_in_panel"), \
         patch("custom_components.entity_renamer.EntityListView"), \
         patch("custom_components.entity_renamer.RenameEntityView"), \
         patch("custom_components.entity_renamer.OpenAISuggestionsView"):
        
        assert await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
        assert DOMAIN in hass.data


async def test_apply_rename_service(hass):
    """Test the apply_rename service."""
    from custom_components.entity_renamer import apply_rename_service
    
    # Mock the entity registry
    mock_registry = MagicMock()
    with patch("homeassistant.helpers.entity_registry.async_get", return_value=mock_registry):
        # Create a mock service call
        service = MagicMock()
        service.data = {
            "entity_id": "light.test_light",
            "new_name": "New Light Name"
        }
        
        # Call the service
        await apply_rename_service(hass, service)
        
        # Verify the entity was updated
        mock_registry.async_update_entity.assert_called_once_with(
            "light.test_light", name="New Light Name"
        )
