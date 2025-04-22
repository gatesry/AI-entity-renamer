"""Fixtures for AI Entity Renamer tests."""
import pytest
from unittest.mock import patch, MagicMock

from homeassistant.core import HomeAssistant


@pytest.fixture
def hass(event_loop):
    """Return a Home Assistant instance for testing."""
    hass = HomeAssistant(event_loop)
    hass.config.components.add("http")
    
    # Set up mocks for HTTP
    hass.http = MagicMock()
    hass.http.register_view = MagicMock()
    hass.http.register_static_path = MagicMock()
    
    # Set up mocks for services
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    
    # Set up mocks for config entries
    hass.config_entries = MagicMock()
    hass.config_entries.async_entries = MagicMock(return_value=[])
    
    # Set up mocks for helpers
    hass.helpers = MagicMock()
    hass.helpers.device_registry = MagicMock()
    hass.helpers.area_registry = MagicMock()
    hass.helpers.entity_registry = MagicMock()
    
    yield hass
    
    event_loop.run_until_complete(hass.async_stop())


@pytest.fixture
def mock_entity_registry():
    """Return a mocked entity registry."""
    registry = MagicMock()
    registry.entities = {
        "light.living_room": MagicMock(
            entity_id="light.living_room",
            name="Living Room Light",
            device_id="device_1",
            original_name="Hue Light 1"
        ),
        "switch.kitchen": MagicMock(
            entity_id="switch.kitchen",
            name="Kitchen Switch",
            device_id="device_2",
            original_name="Z-Wave Switch"
        )
    }
    return registry


@pytest.fixture
def mock_device_registry():
    """Return a mocked device registry."""
    registry = MagicMock()
    registry.devices = {
        "device_1": MagicMock(
            id="device_1",
            name="Philips Hue",
            model="Hue Bulb",
            area_id="area_1"
        ),
        "device_2": MagicMock(
            id="device_2",
            name="Z-Wave Switch",
            model="Z-Wave Switch",
            area_id="area_2"
        )
    }
    
    def get_device(device_id):
        return registry.devices.get(device_id)
    
    registry.async_get = get_device
    return registry


@pytest.fixture
def mock_area_registry():
    """Return a mocked area registry."""
    registry = MagicMock()
    registry.areas = {
        "area_1": MagicMock(
            id="area_1",
            name="Living Room"
        ),
        "area_2": MagicMock(
            id="area_2",
            name="Kitchen"
        )
    }
    
    def get_area(area_id):
        return registry.areas.get(area_id)
    
    registry.async_get_area = get_area
    return registry
