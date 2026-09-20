# Changelog

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
