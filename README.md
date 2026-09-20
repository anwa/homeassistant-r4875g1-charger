<p align="center">
  <img
    src="https://raw.githubusercontent.com/anwa/homeassistant-r4875g1-charger/main/custom_components/r4875g1_charger/brand/logo.png"
    alt="R4875G1 Charger"
    width="420">
</p>

# R4875G1 Charger for Home Assistant

Home Assistant integration for the R4875G1 three-phase charger project.

It connects an existing ESPHome R4875G1 Charger Controller to Home Assistant through a stable semantic interface without duplicating ESPHome entities or moving charger safety logic away from the Controller.

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=anwa&repository=homeassistant-r4875g1-charger&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open R4875G1 Charger in HACS">
  </a>
</p>

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Updating](#updating)
- [Diagnostics](#diagnostics)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Runtime API](#runtime-api)
- [Release status and compatibility](#release-status-and-compatibility)

## Requirements

- Home Assistant 2026.8 or newer
- HACS for the recommended installation method
- an ESPHome R4875G1 Charger Controller already configured in Home Assistant
- Charger Controller firmware exposing Home Assistant Contract 1

## Installation

<details open>
<summary><b>Install with HACS (recommended)</b></summary>

HACS is the recommended installation method. Use the button above or add this repository manually as a custom integration repository.

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu in the upper-right corner.
3. Select **Custom repositories**.
4. Enter `https://github.com/anwa/homeassistant-r4875g1-charger`.
5. Select **Integration** as the repository type.
6. Select **Add**.
7. Open **R4875G1 Charger** in HACS.
8. Select **Download** and keep the newest stable release selected unless you intentionally need an older version.
9. Restart Home Assistant after HACS reports that a restart is required.

After the restart, the integration is available under **Settings -> Devices & services -> Add integration**.

</details>

<details>
<summary><b>Manual installation</b></summary>

Manual installation is supported as a fallback when HACS is not used.

1. Download or clone the desired release.
2. Copy `custom_components/r4875g1_charger` into the Home Assistant configuration directory so that the final path is `/config/custom_components/r4875g1_charger`.
3. Restart Home Assistant.
4. Configure the integration from **Settings -> Devices & services -> Add integration**.

Manual installations are not managed by HACS and therefore do not receive HACS update notifications.

</details>

## Configuration

The Charger Controller must already exist in Home Assistant through the ESPHome integration before this integration is configured.

1. Open **Settings -> Devices & services**.
2. Select **Add integration**.
3. Search for **R4875G1 Charger**.
4. Select the existing ESPHome Charger Controller from the device selector.
5. Confirm the setup.

The selected device must be the Charger Controller itself. The Remote HMI is not a valid Charger Controller source.

During setup, the integration validates the Home Assistant Contract marker and the required semantic Charger Controller roles. A successful setup creates one R4875G1 Charger config entry for the selected Charger Controller.

Multiple Charger Controllers are supported by adding the integration once for each Controller device.

## Updating

HACS tracks the repository after installation and provides an update path when a newer stable GitHub Release is available.

To install an update:

1. Open the Home Assistant update notification or the R4875G1 Charger repository in HACS.
2. Review the release notes.
3. Install the offered update.
4. Restart Home Assistant when HACS reports that a restart is required.

HACS normally refreshes repository metadata automatically. To request an immediate metadata refresh after a new release has been published, open the repository in HACS, open its three-dot menu and select **Update information**.

Refreshing repository information does not install the new version by itself.

## Diagnostics

Home Assistant diagnostics for the integration include the active semantic resolution, capability state, compatibility state and the ESPHome registry inventory used by the resolver.

Entity unique IDs are not exposed directly in diagnostics; they are represented by shortened SHA-256 hashes.

Useful high-level fields include:

- `instance_status`
- `online`
- `compatible`
- `contract_version`
- `contract_supported`
- `resolved_role_count`
- `capabilities`
- missing, disabled or ambiguous required and optional roles

Diagnostics can be downloaded from the integration entry under **Settings -> Devices & services**.

## Troubleshooting

### The integration is not listed after installation

Make sure HACS downloaded the integration successfully and restart Home Assistant. If the integration still does not appear under **Add integration**, perform a hard refresh of the browser and check the Home Assistant logs for errors while loading `r4875g1_charger`.

### No Charger Controller appears in the device selector

The Charger Controller must first be configured through the ESPHome integration and must exist as a Home Assistant device. The Remote HMI is intentionally excluded as a valid Controller source.

### Contract unavailable

The integration could not read a usable Home Assistant Contract marker from the selected Controller. Verify that the Controller is online in Home Assistant and that the installed Controller firmware exposes Home Assistant Contract 1.

### Unsupported contract

The selected Controller reports a Home Assistant Contract version that this integration does not support. Check the integration and firmware release notes before changing either component.

### Missing or disabled required roles

The selected ESPHome device does not currently expose every required Contract-1 role, or one of those entities is disabled in Home Assistant.

Check the integration diagnostics for:

- `missing_required_roles`
- `disabled_required_roles`
- `ambiguous_required_roles`

Do not create replacement template entities for missing Contract roles. Fix the Controller firmware, ESPHome device registration or Home Assistant entity availability instead.

### An entity was renamed in Home Assistant

User-renamed Home Assistant entity IDs are supported. The resolver uses stable ESPHome registry metadata rather than installation-specific entity IDs, and active semantic subscriptions rebind automatically after relevant entity-registry changes.

Renaming an entity should therefore not require removing and re-adding the R4875G1 Charger integration.

### HACS does not show a newly published release

HACS checks repository metadata automatically, but update discovery is not necessarily immediate. Open the repository in HACS and use **three-dot menu -> Update information** to request a refresh.

If HACS still does not offer the new version, verify that the version was published as a GitHub Release and not only created as a Git tag.

### HACS reports that a restart is required

Restart Home Assistant to activate the newly downloaded integration version.

## Architecture

The integration binds one Home Assistant config entry to one existing ESPHome Charger Controller.

The user selects the Charger Controller device once. The integration resolves Home Assistant registry entries to stable semantic roles using the ESPHome platform, entity domain and original entity name. User-renamed Home Assistant entity IDs therefore do not form part of the semantic contract.

Contract 1 currently defines 84 required Controller-side roles and 38 optional roles. Optional roles are grouped into explicit capabilities and do not invalidate the Charger Instance when absent.

The backend refreshes the active runtime mapping after Home Assistant entity-registry changes. Diagnostics expose that active runtime mapping and hash entity unique IDs before including them in diagnostic output.

No charger safety or control logic is implemented here. The Charger Controller remains authoritative for charger control, CAN communication, lifecycle decisions, thermal protection, START eligibility and blackstart operation.

## Runtime API

Each loaded config entry owns a `ChargerInstance` runtime object. It is the single backend access layer for semantic roles, current Home Assistant states, capability availability and high-level instance status.

The instance status is one of:

- `ok` when the required contract is compatible, the Controller is online and no optional capability is partially mapped
- `degraded` when the required contract is usable but an optional capability is only partially mapped
- `offline` when the Contract marker has no usable Home Assistant state
- `incompatible` when the live contract version is unsupported or required semantic roles are structurally unusable

A completely absent optional capability does not degrade the Charger Instance.

The backend exposes four WebSocket commands for frontend consumers:

- `r4875g1_charger/instances` lists loaded Charger Instances and their capability summaries
- `r4875g1_charger/instance` returns the semantic role map and current state snapshot for one config entry
- `r4875g1_charger/control` dispatches one explicitly allow-listed semantic control through the resolved Home Assistant entity
- `r4875g1_charger/subscribe` streams semantic state and mapping updates for one config entry

Writable role snapshots expose their control action and current Home Assistant Number metadata (`min`, `max`, `step`, `unit`) where applicable. Frontend consumers therefore do not need to know the underlying entity domain or service name.

The initial writable role set is intentionally limited to Charger and per-rectifier START/STOP plus AC current limit, DC voltage limit, DC sum power and fallback voltage/current setpoints.

The control API checks the Charger Instance state, resolved role, current entity availability, Home Assistant user permissions and Number limits before dispatching the standard `button.press` or `number.set_value` service. It contains no charger safety logic and never reports a service call as proof of a Controller state transition; frontend consumers must observe semantic state roles for the resulting state.

The semantic subscription sends an initial `snapshot` event and then `role_state` events keyed by semantic role. State events intentionally omit the concrete Home Assistant entity ID and domain. Registry changes rebind the internal state listener automatically and emit a `mapping_changed` snapshot, so entity renames do not require frontend resubscription.

The instance list, snapshot and subscription APIs honor Home Assistant entity read permissions. A user must be able to read the Contract marker to access a Charger Instance, and individual snapshot/subscription roles are filtered through `POLICY_READ`.

The WebSocket API never exposes ESPHome unique IDs.

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

## Branding

The integration ships local Home Assistant brand assets in:

```text
custom_components/
└── r4875g1_charger/
    └── brand/
        ├── icon.png
        └── logo.png
```

`icon.png` is the square integration icon used where Home Assistant has limited display space. `logo.png` is the integration logo used where more space is available.

The README uses an absolute raw GitHub URL for the logo so that renderers outside the GitHub repository context, including HACS, can resolve the image.

No manifest entry is required for these local brand assets.

## Repository relationship

Firmware and the authoritative semantic contract are maintained in:

`anwa/esphome-r4875g1-3phase-charger`

The planned dashboard frontend will be maintained separately from this backend integration.

## Release status and compatibility

The 1.x release series is the stable Backend API v1 line. Backend API v1 was established with version 1.0.0 and remains compatible throughout the 1.x release series.

The backend is considered stable for the documented Contract-1 discovery, runtime, control and live-subscription interfaces. The dashboard frontend, external battery-bank discovery and history/trend presentation are separate project milestones and are not part of this backend release line.

The documented WebSocket commands, semantic role identifiers and subscription event structures form Backend API v1.

For releases in the 1.x series:

- existing documented v1 commands and fields remain compatible
- additive fields, roles and endpoints may be introduced without breaking existing v1 consumers
- a breaking change to the documented backend API requires a new major integration version

The integration version, Controller firmware version and Home Assistant Contract version are intentionally independent:

- Home Assistant Contract 1 defines the semantic interface between the Charger Controller firmware and this integration.
- A newer integration release does not automatically require newer Controller firmware unless the release notes explicitly state a changed requirement.
- A firmware release may remain compatible with the same Home Assistant Contract version.

Review the release notes before installing a future major integration release.

## Releases

Stable versions follow semantic versioning.

For each release, the integration version in `manifest.json`, the Git tag and the published GitHub Release use the same version number, for example:

`1.1.0` -> `v1.1.0`

Release notes are maintained in `CHANGELOG.md` and in the corresponding GitHub Release.

## Removal

To remove the integration completely:

1. Remove the R4875G1 Charger config entry from **Settings -> Devices & services**.
2. Remove **R4875G1 Charger** from HACS if it was installed through HACS.
3. Restart Home Assistant if requested.

Removing this integration does not remove the ESPHome Charger Controller device and does not change Controller firmware behavior.

## Language policy

Source code, commit messages and project documentation are maintained in English. Home Assistant user-interface translations are maintained in at least English and German, and both translation files must stay in sync when user-facing strings change.
