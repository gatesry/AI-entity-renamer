"""Test the config flow for AI Entity Renamer."""
from unittest.mock import patch, MagicMock

import pytest
from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_FORM, RESULT_TYPE_CREATE_ENTRY

from custom_components.entity_renamer.config_flow import EntityRenamerConfigFlow
from custom_components.entity_renamer.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "http", {})
    
    # Initialize the config flow
    flow = EntityRenamerConfigFlow()
    flow.hass = hass
    
    # Test that the form is returned
    result = await flow.async_step_user()
    assert result["type"] == RESULT_TYPE_FORM
    assert result["step_id"] == "user"
    
    # Test form submission with valid data
    with patch(
        "custom_components.entity_renamer.config_flow.openai.OpenAI",
        return_value=MagicMock(),
    ), patch(
        "homeassistant.components.http.ban.async_is_banned",
        return_value=False,
    ):
        result = await flow.async_step_user(
            {
                "api_key": "test_api_key",
            }
        )
        
        assert result["type"] == RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == "AI Entity Renamer"
        assert result["data"] == {
            "api_key": "test_api_key",
        }


async def test_form_invalid_api_key(hass: HomeAssistant) -> None:
    """Test we handle invalid API key."""
    await setup.async_setup_component(hass, "http", {})
    
    # Initialize the config flow
    flow = EntityRenamerConfigFlow()
    flow.hass = hass
    
    # Test form submission with invalid API key
    with patch(
        "custom_components.entity_renamer.config_flow.openai.OpenAI",
        return_value=MagicMock(),
    ), patch(
        "homeassistant.components.http.ban.async_is_banned",
        return_value=False,
    ), patch(
        "custom_components.entity_renamer.config_flow.EntityRenamerConfigFlow.hass.async_add_executor_job",
        side_effect=Exception("Invalid API key"),
    ):
        result = await flow.async_step_user(
            {
                "api_key": "invalid_api_key",
            }
        )
        
        assert result["type"] == RESULT_TYPE_FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {"api_key": "invalid_api_key"}


async def test_form_no_api_key(hass: HomeAssistant) -> None:
    """Test we handle no API key."""
    await setup.async_setup_component(hass, "http", {})
    
    # Initialize the config flow
    flow = EntityRenamerConfigFlow()
    flow.hass = hass
    
    # Test form submission with no API key
    result = await flow.async_step_user(
        {
            "api_key": "",
        }
    )
    
    assert result["type"] == RESULT_TYPE_FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"api_key": "api_key_required"}
