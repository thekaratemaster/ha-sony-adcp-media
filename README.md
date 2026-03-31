# ha-sony-adcp-media

Home Assistant custom integration for Sony projectors using ADCP (Advanced Display Control Protocol) over TCP.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

## Features

- Power on/off control
- Source selection
- Mute control
- Periodic state polling via local TCP connection

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** → click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/thekaratemaster/ha-sony-adcp-media` with category **Integration**.
4. Search for **Sony ADCP Media Player** and install it.
5. Restart Home Assistant.

### Manual

1. Copy `custom_components/sony_adcp_media/` into your Home Assistant `custom_components/` directory.
2. Restart Home Assistant.

## Setup

After installation, go to **Settings → Devices & Services → Add Integration** and search for **Sony ADCP Media Player**.

You will be prompted for:

| Field | Description |
|-------|-------------|
| Host | IP address or hostname of the projector |
| Port | TCP port (default: 53595) |
| Password | ADCP password (if set) |
| Sources | Comma-separated list of input source names |

## Compatibility

- Home Assistant 2024.1.0 or later
- Sony projectors with ADCP TCP control enabled

## Documentation

See [docs/integration-contract.md](docs/integration-contract.md) for the integration contract and automation-facing usage notes.
