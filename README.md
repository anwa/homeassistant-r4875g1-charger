# R4875G1 Charger for Home Assistant

Home Assistant backend integration for the R4875G1 three-phase charger project.

## Development status

This repository is in early development.

The backend currently provides:

- UI-based selection of an existing ESPHome Charger Controller device
- validation of the explicit R4875G1 Home Assistant Contract marker
- semantic resolution of the complete Controller-side Contract-1 role set
- explicit capability state for required and optional feature groups
- automatic refresh of semantic mappings when Home Assistant entity-registry entries change
- diagnostic output for resolved roles, capabilities and the complete Charger Controller registry inventory
- a stable read-only runtime and WebSocket API for the future dashboard frontend

It intentionally does not create duplicate charger entities, proxy services or dashboard cards.

The Charger Controller remains authoritative for charger control, CAN communication, lifecycle decisions, thermal protection, START eligibility and blackstart operation.

## Requirements

- Home Assistant 2026.8 or newer
- an ESPHome R4875G1 Charger Controller exposing Home Assistant Contract 1
- current firmware from the R4875G1 charger project

## Architecture

The integration binds one Home Assistant config entry to one existing ESPHome Charger Controller.

The user selects the Charger Controller device once. The integration resolves Home Assistant registry entries to stable semantic roles using the ESPHome platform, entity domain and original entity name. User-renamed Home Assistant entity IDs therefore do not form part of the semantic contract.

Contract 1 currently defines 84 required Controller-side roles and 38 optional roles. Optional roles are grouped into explicit capabilities and do not invalidate the Charger Instance when absent.

The backend refreshes the active runtime mapping after Home Assistant entity-registry changes. Diagnostics expose that active runtime mapping and hash entity unique IDs before including them in diagnostic output.

No charger safety or control logic is implemented here.

## Runtime API

Each loaded config entry owns a `ChargerInstance` runtime object. It is the single backend access layer for semantic roles, current Home Assistant states, capability availability and high-level instance status.

The instance status is one of:

- `ok` when the required contract is compatible, the Controller is online and no optional capability is partially mapped
- `degraded` when the required contract is usable but an optional capability is only partially mapped
- `offline` when the Contract marker has no usable Home Assistant state
- `incompatible` when the live contract version is unsupported or required semantic roles are structurally unusable

A completely absent optional capability does not degrade the Charger Instance.

The backend exposes two read-only WebSocket commands for the future frontend:

- `r4875g1_charger/instances` lists loaded Charger Instances and their capability summaries
- `r4875g1_charger/instance` returns the semantic role map and current state snapshot for one config entry

The WebSocket API never exposes ESPHome unique IDs and does not provide control commands.

## Language policy

Source code, commit messages and project documentation are maintained in English. Home Assistant user-interface translations are maintained in at least English and German, and both translation files must stay in sync when user-facing strings change.

## Capability groups

Required capabilities:

- contract identity
- core charger
- rectifier detail
- cooling environment

Optional capabilities:

- advanced charger telemetry and controls
- per-rectifier fan control
- external chassis cooling
- Controller diagnostics

External battery-bank discovery remains a later milestone because those entities are owned by other Home Assistant integrations rather than the Charger Controller.

## Repository relationship

Firmware and the authoritative semantic contract are maintained in:

`anwa/esphome-r4875g1-3phase-charger`

The planned dashboard frontend will be maintained separately from this backend integration.

## Installation during development

Add this repository to HACS as a custom integration repository, install **R4875G1 Charger**, restart Home Assistant and add the integration from **Settings -> Devices & services**.

The integration is not yet intended as a production release.
