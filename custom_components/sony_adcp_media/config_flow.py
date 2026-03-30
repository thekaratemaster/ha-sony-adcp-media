from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_COMMUNITY,
    CONF_SOURCES,
    DEFAULT_COMMUNITY,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SOURCES,
)


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_COMMUNITY, default=DEFAULT_COMMUNITY): vol.All(str, vol.Length(min=4, max=4)),
        vol.Optional(CONF_SOURCES, default=",".join(DEFAULT_SOURCES)): str,  # comma-separated in UI
    }
)


def _parse_sources(s: str) -> list[str]:
    return [x.strip() for x in (s or "").split(",") if x.strip()]


class SonyAdcpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

        host = user_input[CONF_HOST]
        await self.async_set_unique_id(f"sony_adcp_{host}")
        self._abort_if_unique_id_configured()

        data = {
            CONF_HOST: host,
            CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
            CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
            CONF_PASSWORD: user_input.get(CONF_PASSWORD),
            CONF_COMMUNITY: user_input.get(CONF_COMMUNITY, DEFAULT_COMMUNITY),
            CONF_SOURCES: _parse_sources(user_input.get(CONF_SOURCES, "")),
        }

        return self.async_create_entry(title=data[CONF_NAME], data=data)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SonyAdcpOptionsFlowHandler(config_entry)


class SonyAdcpOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        current = {**self.entry.data, **self.entry.options}
        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=current.get(CONF_NAME, DEFAULT_NAME)): str,
                vol.Optional(CONF_PORT, default=current.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Optional(CONF_PASSWORD, default=current.get(CONF_PASSWORD) or ""): str,
                vol.Optional(CONF_COMMUNITY, default=current.get(CONF_COMMUNITY, DEFAULT_COMMUNITY)): vol.All(
                    str, vol.Length(min=4, max=4)
                ),
                vol.Optional(
                    CONF_SOURCES,
                    default=",".join(current.get(CONF_SOURCES, DEFAULT_SOURCES)),
                ): str,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=schema)

        return self.async_create_entry(
            title="",
            data={
                CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
                CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                CONF_PASSWORD: user_input.get(CONF_PASSWORD) or None,
                CONF_COMMUNITY: user_input.get(CONF_COMMUNITY, DEFAULT_COMMUNITY),
                CONF_SOURCES: _parse_sources(user_input.get(CONF_SOURCES, "")),
            },
        )
