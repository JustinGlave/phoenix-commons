# Security Policy

`phoenix-commons` is the **shared UI platform** for the Phoenix
Controls / ATS Automation desktop tool family. It is **internal ATS
Automation tooling**, not a publicly-distributed product. This
document describes how to report security-relevant concerns through
ATS internal channels.

## Reporting a security concern

If you discover a security issue — a vulnerability, an unintended
data exposure, a credential leak, an unsafe code path, anything that
could harm ATS Automation systems or data — report it privately to:

- **Justin Glave** — `justing@atsinc.org`
- Or via the standard **ATS Automation internal incident / IT
  reporting process**.

Do **not**:

- Post the details in a public GitHub issue, public chat, or any
  external forum.
- Include real customer data, credentials, API keys, internal
  hostnames, or other confidential ATS information in any report
  channel that isn't already approved for handling that data.
- Discuss the issue on social media, in conference talks, or in any
  public-facing material before ATS has had a chance to remediate.

If you accidentally pasted secrets or customer data into a GitHub
issue, contact Justin immediately so the issue can be redacted /
removed and the leaked credentials rotated.

## Why phoenix-commons specifically matters

`phoenix-commons` is the **platform layer** under every Phoenix
desktop tool. A vulnerability in commons code becomes a vulnerability
in **every consuming app simultaneously** — `Phoenix Command Center`,
`Job Tracker`, `Phoenix CAD Tool` (Lab Layout Tool), `Phoenix Checkout
Tool`, `ValveMasterTool`, and any future scaffolded tool.

Particular surfaces worth reporting:

- The **auto-updater** (`phoenix_commons.updater`) which downloads
  release zips from GitHub and unpacks them into per-user install
  directories.
- The **path helpers** (`phoenix_commons.paths`) — incorrect
  `user_data_dir` resolution could write user data into an install
  directory that the updater later wipes.
- The **theme loader** (`phoenix_commons.theme`) — any external
  resource resolution that could be tricked into loading from an
  unexpected location.
- Any future **icon / resource provider** API (Phase 2.5 / 2.6).

## What's out of scope

- **Public vulnerability bounty.** There is no bounty program. This
  is internal tooling; security work is part of normal ATS internal
  process, not a paid disclosure scheme.
- **Vulnerabilities in third-party dependencies** (PySide6, Qt,
  Python, PyInstaller, Inno Setup, setuptools). Report those
  upstream to the respective project, and note them internally so
  ATS can pin / upgrade.
- **Issues that require an attacker to already have local file-
  system access at the privilege of the running user.** At that
  point the attacker has full local control regardless of what this
  platform does.

## Confidentiality

Security reports about `phoenix-commons` may inevitably touch on
non-public ATS Automation infrastructure (hostnames, internal repo
URLs, deployment paths, credentials). Treat any report — and any
discussion thread or fix branch derived from it — as confidential
under the same expectations that apply to other internal ATS
material. See `LICENSE` for the full proprietary-use language.

## Response

Reports go to Justin first. Acknowledgement target: **5 business
days**. Resolution depends on severity and the blast radius across
consuming apps; a vulnerability that touches the updater or the
path helpers is treated as P0 because it affects every shipping
Phoenix tool.

## Disclosure

Because this is internal tooling there is no public disclosure
timeline or CVE process. Fixes ship via the normal phoenix-commons
release workflow plus a coordinated bump in each consuming app's
`requirements.txt` / submodule reference.

## Coordinating with consuming apps

A security fix in `phoenix-commons` requires coordinated propagation
into the production Phoenix tools. The current release cadence per
the [UI Platform Baseline](docs/ui-platform-baseline-v1/BASELINE.md):

- `phoenix-command-center` consumes commons directly (planned Phase 7+).
- The 4 production tools (`Job Tracker`, `Phoenix_CAD_Tool`,
  `Phoenix-Checkout-Tool`, `ValveMasterTool`) currently ship with
  local copies of commons primitives. Their retrofit to commons-backed
  imports is the Phase 7 / Phase 8 work, blocked on the S1 / AV gate
  (see `docs/ui-platform-baseline-v1/BLOCKERS.md`).

Until retrofit, a security issue in commons affects the platform
contract but not the deployed installers. After retrofit, every
released installer of every Phoenix tool consumes the fix on its
next release.
