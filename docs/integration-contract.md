# Integration Contract

## Domain

`sony_adcp_media`

## What Home Assistant gets

- a media player entity for Sony projectors
- power control
- source selection
- mute control
- periodic state polling

## Setup surface

- host
- port
- password
- sources list

## Compatibility expectations

- projector control remains available through standard Home Assistant media player actions
- source names and config-flow fields should only change with a migration note
- polling behavior changes should be documented in release notes
