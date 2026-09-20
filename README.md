# R4875G1 Charger for Home Assistant

Home Assistant backend integration for the R4875G1 three-phase charger project.

## Development status

This repository is in early development.

The first milestone provides only:

- UI-based selection of an existing ESPHome Charger Controller device
- validation of the explicit R4875G1 Home Assistant Contract marker
- semantic resolution of a small bootstrap role set
- diagnostic output for the complete Charger Controller entity-registry inventory

It intentionally does not create duplicate charger entities, proxy services or dashboard cards.

The Charger Controller remains authoritative for charger control, CAN communication, lifecycle decisions, thermal protection, START eligibility and blackstart operation.

## Requirements

- Home Assistant 2026.8 or newer
- an ESPHome R4875G1 Charger Controller exposing Home Assistant Contract 1
- current firmware from the R4875G1 charger project

## Architecture

The integration binds one Home Assistant config entry to one existing ESPHome Charger Controller.

The user selects the Charger Controller device once. The integration then resolves Home Assistant entities to stable semantic roles.

The initial bootstrap resolver intentionally covers only a representative core role set. Config-entry diagnostics also expose the selected device's complete registry inventory using hashed entity unique IDs. That inventory will be used to verify the final Contract-1 resolver against a real installation before the full semantic role table is frozen.

No charger safety or control logic is implemented here.

## Repository relationship

Firmware and the authoritative semantic contract are maintained in:

`anwa/esphome-r4875g1-3phase-charger`

The planned dashboard frontend will be maintained separately from this backend integration.

## Installation during development

Add this repository to HACS as a custom integration repository, install **R4875G1 Charger**, restart Home Assistant and add the integration from **Settings -> Devices & services**.

The integration is not yet intended as a production release.
