# AGENTS.md

## Scope

These rules apply to the complete `homeassistant-r4875g1-charger` repository.

## Inherited Rules

This repository lives in a rule hierarchy. Apply these files in addition to the rules below, in this order of increasing precedence:

| Level | File | Applies to |
|---|---|---|
| Global | `../../../../AGENTS.md` | everything: language, Git authority, branches, commits, versioning principles, documentation style, evidence |
| ESPHome | `../../../AGENTS.md` | only its "HMI Over Home Assistant" principles |

The Waveshare rules (`../../AGENTS.md`) do not apply to this repository. This file contains only what is specific to this repository and takes precedence over the inherited files.

If the inherited files are not present, for example in a fresh clone: write all repository content in English, never commit secrets, and never push, tag or publish without the user's approval.

## Translations

- Home Assistant user-interface translations are maintained in at least English and German.
- When a user-facing string changes, `custom_components/r4875g1_charger/translations/en.json` and `de.json` must be checked and kept in sync.

## Architecture

- The Charger Controller firmware remains authoritative for charger lifecycle, CAN communication, safety checks, thermal protection, START eligibility and blackstart behavior.
- The integration resolves and transports only. It must not implement, duplicate or weaken Controller safety or control logic.
- Semantic roles are resolved from the ESPHome platform, entity domain and original entity name. Do not depend on installation-specific or user-renamed entity IDs.
- A successful control service call means only that Home Assistant accepted the call. It must never be reported as proof of a Controller state transition.
- Control dispatch stays explicitly allow-listed and checks instance state, role resolution, entity availability, user permissions and Number limits before calling standard Home Assistant services.
- The WebSocket API must not expose ESPHome unique IDs. Diagnostics must hash entity unique IDs.
- Prefer a consistent reusable architecture over local workarounds, even when the consistent solution requires more refactoring.

## Compatibility

- The documented WebSocket commands, semantic role identifiers and subscription event structures form Backend API v1.
- Within the 1.x series, existing documented commands and fields remain compatible. Additive fields, roles and endpoints are allowed.
- A breaking Backend API change requires a new major version. The assistant must propose and discuss a major version with the user before applying it.
- The integration version, Controller firmware version and Home Assistant Contract version are independent.

## Local checks

Before committing a change, run these checks and report the results:

- `py -3.13 -m compileall -q custom_components`
- JSON validation of `manifest.json`, `translations/*.json` and `hacs.json`
- `git diff --check`

HACS validation runs in GitHub Actions and is not available locally.

## Versioning and releases

- The integration version is defined in `custom_components/r4875g1_charger/manifest.json`.
- Update `CHANGELOG.md` in the same commit as the version increase.
- The version in `manifest.json`, the Git tag and the GitHub Release use the same number, for example `1.4.1` -> `v1.4.1`.
- Any version intended to be offered through HACS must be published as a full GitHub Release; a tag alone is not sufficient. Releases are published with the user's approval, as defined by the global Git authority rules.

## Related repositories

This repository is one part of a project family. The sibling repositories are expected next to this one:

| Repository | Local path | Role |
|---|---|---|
| `esphome-r4875g1-3phase-charger` | `../esphome-r4875g1-3phase-charger` | Charger Controller and Remote HMI firmware; defines the Home Assistant entity contract in `HomeAssistant/ENTITY_CONTRACT.md` |
| `homeassistant-r4875g1-charger` | `.` | Home Assistant integration; resolves Controller entities into semantic roles and exposes Backend API v1 |
| `r4875g1-charger-dashboard` | `../r4875g1-charger-dashboard` | Dashboard card and Grafana history dashboard; consumes Backend API semantic roles |

### Contract surfaces

- `../esphome-r4875g1-3phase-charger/HomeAssistant/ENTITY_CONTRACT.md` is the authoritative description of the Controller entity contract.
- Upstream: role specifications bind Controller entities by entity domain and original entity name, which is the ESPHome `name:` in the firmware packages. A firmware rename or domain change breaks role resolution even when firmware behavior is unchanged.
- Contract marker: the Controller publishes `R4875G1 Charger Contract` from `packages/controller/ha-contract.yaml`. This integration accepts the versions in `SUPPORTED_CONTRACT_VERSIONS` in `const.py`. An incompatible contract change requires a new contract version on both sides.
- Downstream: the dashboard card consumes Backend API v1 through `../r4875g1-charger-dashboard/src/api/client.ts` and `src/api/types.ts`.
- Not through this integration: the Grafana history dashboard and the Remote HMI firmware read Controller entity IDs directly. Changes in this repository do not affect them, but contract changes discussed here may.

### Cross-repository rules

- A new or changed role specification must match the firmware entity name and domain. Check the firmware packages and `ENTITY_CONTRACT.md` in the same task, and run the cross-repository contract check from the firmware repository: `../esphome-r4875g1-3phase-charger/.venv/Scripts/python.exe ../esphome-r4875g1-3phase-charger/scripts/check-contract.py`.
- A role domain change also changes its state values, for example from `on`/`off` to numeric strings. Review every dashboard consumer that interprets the role state.
- A Backend API v1 change must be checked against the dashboard API client and types in the same task.
- Each repository keeps its own versioning, changelog and validation rules. Apply the rules of the repository being changed.
