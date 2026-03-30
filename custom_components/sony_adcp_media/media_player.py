from __future__ import annotations

from datetime import timedelta
import logging
from typing import Optional

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)

from .adcp import adcp_exchange
from .const import (
    DOMAIN,
    CONF_COMMUNITY,
    CONF_SOURCES,
    DEFAULT_NAME,
    UPDATE_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.VOLUME_MUTE
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    cfg = {**entry.data, **entry.options}

    host: str = cfg[CONF_HOST]
    port: int = cfg.get(CONF_PORT, 53595)
    password: Optional[str] = cfg.get(CONF_PASSWORD)
    community: str = cfg.get(CONF_COMMUNITY, "SONY")  # stored for compatibility; not used in commands
    sources: list[str] = cfg.get(CONF_SOURCES, ["HDMI1", "HDMI2"])
    name: str = cfg.get(CONF_NAME, DEFAULT_NAME)

    async def _async_update_data() -> dict:
        power = await adcp_exchange(host, port, password, "power_status ?")
        if power is None:
            raise UpdateFailed(f"Unable to reach projector at {host}:{port}")

        input_ = await adcp_exchange(host, port, password, "input ?")
        muting = await adcp_exchange(host, port, password, "muting ?")

        return {
            "power_status": power.strip('"') if power else None,
            "input": (input_ or "").strip('"') if input_ else None,
            "muting": (muting or "").strip('"') if muting else None,
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            SonyAdcpMediaPlayer(
                coordinator=coordinator,
                host=host,
                name=name,
                sources=sources,
                community=community,
                port=port,
                password=password,
            )
        ]
    )


class SonyAdcpMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    _attr_supported_features = SUPPORTED_FEATURES
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: DataUpdateCoordinator,
        host: str,
        name: str,
        sources: list[str],
        community: str,
        port: int,
        password: Optional[str],
    ) -> None:
        super().__init__(coordinator)
        self._host = host
        self._port = port
        self._password = password
        self._community = community

        self._attr_unique_id = f"sony_adcp_media_{host.replace('.', '_')}"
        self._attr_name = name
        self._attr_source_list = sources

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self) -> MediaPlayerState:
        ps = (self.coordinator.data or {}).get("power_status")
        if ps is None:
            return MediaPlayerState.UNKNOWN

        ps_l = str(ps).lower()
        return MediaPlayerState.OFF if ps_l == "standby" else MediaPlayerState.ON

    @property
    def is_on(self) -> Optional[bool]:
        st = self.state
        if st == MediaPlayerState.UNKNOWN:
            return None
        return st == MediaPlayerState.ON

    @property
    def source(self) -> Optional[str]:
        return (self.coordinator.data or {}).get("input")

    @property
    def is_volume_muted(self) -> bool:
        return (self.coordinator.data or {}).get("muting") == "on"

    async def _cmd(self, cmd: str) -> None:
        await adcp_exchange(self._host, self._port, self._password, cmd)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self._cmd('power "on"')

    async def async_turn_off(self) -> None:
        await self._cmd('power "off"')

    async def async_select_source(self, source: str) -> None:
        if source not in (self._attr_source_list or []):
            _LOGGER.warning("Unknown source %s", source)
            return
        await self._cmd(f'input "{source}"')

    async def async_mute_volume(self, mute: bool) -> None:
        await self._cmd(f'muting "{"on" if mute else "off"}"')
