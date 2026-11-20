# AGENTS.md

## Scope

These rules apply to the complete `homeassistant-r4875g1-charger` repository.

## Language

- Source code, comments, commit messages, changelog entries and project documentation are written in English.
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

## Change workflow

- Work in small, reviewable functional steps.
- Before implementing a change, inspect the current local branch and relevant repository rules.
- Edit files directly in the local working tree. Keep each change limited to the current concern and review the resulting diff before reporting it as complete.
- Before committing a change, run the local checks and report the results:
  - `py -3.13 -m compileall -q custom_components`
  - JSON validation of `manifest.json`, `translations/*.json` and `hacs.json`
  - `git diff --check`
- HACS validation runs in GitHub Actions and is not available locally.
- Do not claim runtime testing that has not actually been performed in Home Assistant.
- Provide a patch that passes `git apply --check` only when the user asks for one or the working tree cannot be edited directly.

## Repository access

- Treat GitHub as read-only for the assistant. Do not perform repository mutations through GitHub or a GitHub integration.
- The assistant may create a local feature branch and local commits when the user asks for commits. Do not commit directly on `main` unless the user says so.
- The assistant must not push, merge into `main`, create or move tags, publish GitHub Releases, delete branches or rewrite commits that already exist on the remote. The user performs these steps.

## Versioning

- The integration version is defined in `custom_components/r4875g1_charger/manifest.json`.
- Every commit that changes runtime behavior, source code, packaging or other functionality must increase the version.
- Documentation-only commits may omit a version increase.
- Use a patch increment for small fixes and narrowly scoped changes, and a minor increment for new capabilities or larger backward-compatible milestones.
- Do not defer a required version increment to a later commit.
- Update `CHANGELOG.md` in the same commit as the version increase.

## Release workflow

- The version in `manifest.json`, the Git tag and the published GitHub Release use the same number, for example `1.4.1` -> `v1.4.1`.
- Any version intended to be offered through HACS must be published as a full GitHub Release; a tag alone is not sufficient.
- The user performs the merge, tag and GitHub Release. The assistant provides the release material: commit message or local commit, merge commands, tag command and message, release title, release notes and verification commands.

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
