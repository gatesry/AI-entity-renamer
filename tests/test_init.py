"""Tests for AI Entity Renamer integration."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from homeassistant.setup import async_setup_component

from custom_components.entity_renamer import DOMAIN


@pytest.mark.asyncio
async def test_setup(hass):
    """Test the setup of the integration."""
    with (
        patch("custom_components.entity_renamer.frontend.async_register_built_in_panel"),
        patch("custom_components.entity_renamer.EntityListView"),
        patch("custom_components.entity_renamer.RenameEntityView"),
        patch("custom_components.entity_renamer.OpenAISuggestionsView"),
    ):

        assert await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
        assert DOMAIN in hass.data


@pytest.mark.asyncio
async def test_apply_rename_service(hass):
    """Test the apply_rename service."""
    from custom_components.entity_renamer import apply_rename_service

    # Mock the entity registry
    mock_registry = MagicMock()
    with patch("homeassistant.helpers.entity_registry.async_get", return_value=mock_registry):
        # Create a mock service call
        service = MagicMock()
        service.data = {"entity_id": "light.test_light", "new_name": "New Light Name"}

        # Call the service
        await apply_rename_service(hass, service)

        # Verify the entity was updated
        mock_registry.async_update_entity.assert_called_once_with(
            "light.test_light", name="New Light Name"
        )


@pytest.mark.asyncio
async def test_apply_device_rename_service(hass):
    """Test the apply_device_rename service."""
    from custom_components.entity_renamer import apply_device_rename_service

    mock_registry = MagicMock()
    with patch("homeassistant.helpers.device_registry.async_get", return_value=mock_registry):
        service = MagicMock()
        service.data = {"device_id": "abc123", "new_name": "New Device"}

        await apply_device_rename_service(hass, service)

        mock_registry.async_update_device.assert_called_once_with("abc123", name="New Device")
