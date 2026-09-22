# Changelog

+## 1.2.0

Cooling-control Backend API milestone.

- add generic semantic Switch control support through Backend API v1
- add `set_switch` control metadata with boolean values
- allow semantic control of external cooling automatic mode
- allow semantic control of external cooling fan power
- allow writes to the external cooling manual PWM setpoint
- dispatch Switch controls through standard Home Assistant `switch.turn_on` and `switch.turn_off` services
- keep Controller-side cooling behavior and safety authoritative in the Charger Controller

This release is a backward-compatible additive extension of Backend API v1.

## 1.1.1

Repository validation and branding alignment release.

- add the official HACS repository validation workflow for integrations
- add an OSI-approved MIT license for HACS repository validation
- align backend icon and logo assets with the dashboard branding
- standardize the integration icon at 256 x 256 pixels
- standardize the integration logo at 768 x 256 pixels
- align README branding presentation with the dashboard repository
- document the active dashboard repository relationship
- prepare repository description and topic metadata for HACS validation

No Backend API v1, semantic role or control behavior changed in this release.

## 1.1.0

Additive Backend API v1 metadata release.

- expose Home Assistant units on every semantic role snapshot when available
- include the same unit metadata in live `role_state` subscription events
- preserve existing writable Number control metadata for compatibility
- keep semantic role identifiers and control behavior unchanged

This release is backward-compatible with Backend API v1 consumers.

## 1.0.2

HACS documentation rendering and usability release.

- use an absolute raw GitHub URL for the README logo so HACS can resolve it
- add a direct Open in HACS button
- reorganize the README around installation, configuration and updates
- add a compact contents section for faster navigation
- make HACS and manual installation sections easier to scan
- make the stable 1.x release status version-independent
- clarify the relationship between integration, firmware and Contract versions

No backend API, semantic role or control behavior changed in this release.

## 1.0.1

Documentation and branding release.

- add local Home Assistant integration icon and logo assets
- add complete HACS custom-repository installation instructions
- document first-time Charger Controller configuration
- document HACS update discovery and restart behavior
- add manual installation and removal instructions
- document diagnostics and common troubleshooting cases
- clarify integration, firmware and Home Assistant Contract versioning
- document the stable release workflow and Backend API v1 compatibility rules

No backend API, semantic role or control behavior changed in this release.

## 1.0.0

First stable backend release.

- add UI-based binding to an existing ESPHome Charger Controller
- validate Home Assistant Contract 1 and resolve the complete semantic role set
- support required and optional capability groups without duplicating ESPHome entities
- preserve semantic resolution across user-renamed Home Assistant entity IDs
- provide the `ChargerInstance` runtime abstraction and instance health states
- expose permission-aware semantic snapshots through the WebSocket API
- provide an allow-listed semantic control path through standard Home Assistant services
- expose Home Assistant Number metadata for writable setpoints
- provide semantic live subscriptions with automatic registry-remap handling
- keep ESPHome unique IDs out of the frontend API and diagnostics-safe through hashing
- preserve Charger Controller authority for charger control, lifecycle and safety behavior
- provide synchronized English and German Home Assistant UI translations

Backend API v1 is considered stable beginning with this release.
