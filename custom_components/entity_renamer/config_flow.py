"""Config flow for Entity Renamer integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EntityRenamerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Entity Renamer."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the API key (we could test it here if needed)
            api_key = user_input.get("api_key", "")
            
            if not api_key:
                errors["api_key"] = "api_key_required"
            else:
                # Test the API key with OpenAI
                try:
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    
                    # Simple test call to validate the API key
                    await self.hass.async_add_executor_job(
                        lambda: client.models.list()
                    )
                    
                    # If we get here, the API key is valid
                    return self.async_create_entry(
                        title="Entity Renamer",
                        data=user_input,
                    )
                except ImportError:
                    errors["base"] = "openai_not_installed"
                except openai.AuthenticationError as e:
                    _LOGGER.error("Invalid OpenAI API key: %s", e)
                    errors["api_key"] = "invalid_api_key"
                except openai.RateLimitError as e:
                    _LOGGER.error("OpenAI API rate limit exceeded: %s", e)
                    errors["base"] = "rate_limit_exceeded"
                except openai.APIConnectionError as e:
                    _LOGGER.error("Failed to connect to OpenAI API: %s", e)
                    errors["base"] = "connection_error"
                except openai.APITimeoutError as e:
                    _LOGGER.error("OpenAI API request timed out: %s", e)
                    errors["base"] = "timeout_error"
                except openai.BadRequestError as e:
                    _LOGGER.error("Bad request to OpenAI API: %s", e)
                    errors["base"] = "bad_request_error"
                except openai.InternalServerError as e:
                    _LOGGER.error("OpenAI API internal server error: %s", e)
                    errors["base"] = "openai_server_error"
                except openai.PermissionDeniedError as e:
                    _LOGGER.error("Permission denied by OpenAI API: %s", e)
                    errors["api_key"] = "permission_denied"
                except openai.UnprocessableEntityError as e:
                    _LOGGER.error("Unprocessable entity error from OpenAI API: %s", e)
                    errors["base"] = "unprocessable_entity"
                except Exception as e:
                    _LOGGER.error("Unexpected error validating OpenAI API key: %s", e)
                    errors["base"] = "unknown_error"

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EntityRenamerOptionsFlow(config_entry)


class EntityRenamerOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the component."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Validate the API key
            api_key = user_input.get("api_key", "")
            
            if not api_key:
                errors["api_key"] = "api_key_required"
            else:
                # Test the API key with OpenAI
                try:
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    
                    # Simple test call to validate the API key
                    await self.hass.async_add_executor_job(
                        lambda: client.models.list()
                    )
                    
                    # If we get here, the API key is valid
                    return self.async_create_entry(
                        title="",
                        data=user_input,
                    )
                except ImportError:
                    errors["base"] = "openai_not_installed"
                except openai.AuthenticationError as e:
                    _LOGGER.error("Invalid OpenAI API key: %s", e)
                    errors["api_key"] = "invalid_api_key"
                except openai.RateLimitError as e:
                    _LOGGER.error("OpenAI API rate limit exceeded: %s", e)
                    errors["base"] = "rate_limit_exceeded"
                except openai.APIConnectionError as e:
                    _LOGGER.error("Failed to connect to OpenAI API: %s", e)
                    errors["base"] = "connection_error"
                except openai.APITimeoutError as e:
                    _LOGGER.error("OpenAI API request timed out: %s", e)
                    errors["base"] = "timeout_error"
                except openai.BadRequestError as e:
                    _LOGGER.error("Bad request to OpenAI API: %s", e)
                    errors["base"] = "bad_request_error"
                except openai.InternalServerError as e:
                    _LOGGER.error("OpenAI API internal server error: %s", e)
                    errors["base"] = "openai_server_error"
                except openai.PermissionDeniedError as e:
                    _LOGGER.error("Permission denied by OpenAI API: %s", e)
                    errors["api_key"] = "permission_denied"
                except openai.UnprocessableEntityError as e:
                    _LOGGER.error("Unprocessable entity error from OpenAI API: %s", e)
                    errors["base"] = "unprocessable_entity"
                except Exception as e:
                    _LOGGER.error("Unexpected error validating OpenAI API key: %s", e)
                    errors["base"] = "unknown_error"

        # Get current values
        current_api_key = self.config_entry.data.get("api_key", "")

        # Show the form
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key", default=current_api_key): str,
                }
            ),
            errors=errors,
        )
