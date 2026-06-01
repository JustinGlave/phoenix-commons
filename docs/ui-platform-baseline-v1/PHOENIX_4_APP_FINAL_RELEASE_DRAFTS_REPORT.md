# Phoenix Family — 4-App Final Release Drafts Report

> **Status:** all 4 stable tags created + pushed; all 4 GitHub Release drafts created with required assets uploaded. **NO release is published.**
> **Date:** 2026-06-01.
> **Companions:** `PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md`, `PHOENIX_4_APP_RC_VALIDATION_SUMMARY.md`.

---

## 1. Stable tags created

All 4 annotated tags created locally + pushed to origin. Each points at the exact same SHA as its corresponding `-rc1` tag (Decision #2 — no re-tagging in place).

| App | Stable tag | Push result |
|-----|------------|-------------|
| Phoenix CAD / Lab Layout Tool | `v0.1.2` | `[new tag] v0.1.2 -> v0.1.2` on `JustinGlave/lab-layout-tool` |
| Phoenix Checkout Tool | `v1.7.1` | `[new tag] v1.7.1 -> v1.7.1` on `JustinGlave/Phoenix-Checkout-Tool` |
| ValveMaster / Phoenix Master Tool | `v1.1.1` | `[new tag] v1.1.1 -> v1.1.1` on `JustinGlave/phoenix-master-tool` |
| Job Tracker / Project Tracking Tool | `v1.8.6` | `[new tag] v1.8.6 -> v1.8.6` on `JustinGlave/project-tracking-tool` |

---

## 2. Tag / SHA mapping

| App | RC tag SHA (immutable) | Stable tag SHA (just created) | SHA match |
|-----|-------------------------|--------------------------------|-----------|
| Phoenix CAD | `v0.1.2-rc1` → `35a06610b0c655e9652d9540070afd37fc97f820` | `v0.1.2` → `35a06610b0c655e9652d9540070afd37fc97f820` | ✅ |
| Phoenix Checkout | `v1.7.1-rc1` → `274b0a8f2914ba4d9123bf8a4c3afe1d03e74077` | `v1.7.1` → `274b0a8f2914ba4d9123bf8a4c3afe1d03e74077` | ✅ |
| ValveMaster | `v1.1.1-rc1` → `e6eefa15b89fba851b1e8acd2d94e83035c58c9a` | `v1.1.1` → `e6eefa15b89fba851b1e8acd2d94e83035c58c9a` | ✅ |
| Job Tracker | `v1.8.6-rc1` → `689e8ee06979b8ff737caa654f53f1c2a0928c8b` | `v1.8.6` → `689e8ee06979b8ff737caa654f53f1c2a0928c8b` | ✅ |

All 4 final-vs-RC SHA pairs identical. RC tags remain immutable forensic markers (`-rc1` tags untouched).

---

## 3. Draft release URLs

Each release is in **draft** state — visible only to repo admins; not visible to end users; not present in the `latest` release pointer.

| App | Title | Tag | Draft URL |
|-----|-------|-----|-----------|
| Phoenix CAD | `Lab Layout Tool v0.1.2` | `v0.1.2` | https://github.com/JustinGlave/lab-layout-tool/releases/tag/untagged-b0a313f78d9d67af2fcd |
| Phoenix Checkout | `Phoenix Checkout Tool v1.7.1` | `v1.7.1` | https://github.com/JustinGlave/Phoenix-Checkout-Tool/releases/tag/untagged-dd390360c01504af11b5 |
| ValveMaster | `Phoenix Master Tool v1.1.1` | `v1.1.1` | https://github.com/JustinGlave/phoenix-master-tool/releases/tag/untagged-404d5fa5ad5e62f7b398 |
| Job Tracker | `Project Tracking Tool v1.8.6` | `v1.8.6` | https://github.com/JustinGlave/project-tracking-tool/releases/tag/untagged-e73da4b55e676b4094f2 |

The `untagged-XXX` URL fragment is GitHub's draft-state URL; on publication it converts to `/releases/tag/v<version>`. The tag binding is correct in the draft metadata (`tag: v<version>`) per `gh release view`.

---

## 4. Assets uploaded per release

Exactly 2 required assets uploaded per draft. No optional `*_FullInstall.zip` uploaded (per brief Step 5: "Do not upload `*_FullInstall.zip` unless operator separately approves").

| App | Asset | Size | Type |
|-----|-------|------|------|
| **Phoenix CAD** | `LabLayoutToolSetup.exe` | 38,016,778 B (36.3 MB) | Inno Setup installer |
| **Phoenix CAD** | `LabLayoutTool.zip` | 58,264,923 B (55.6 MB) | Auto-updater (full-folder, 305 entries) |
| **Phoenix Checkout** | `PhoenixCheckoutToolSetup.exe` | 41,381,486 B (39.5 MB) | Inno Setup installer |
| **Phoenix Checkout** | `PhoenixCheckoutTool.zip` | 4,593,289 B (4.4 MB) | Auto-updater (exe-only, 1 entry) |
| **ValveMaster** | `PhoenixMasterToolSetup.exe` | 33,828,432 B (32.3 MB) | Inno Setup installer |
| **ValveMaster** | `PhoenixMasterTool.zip` | 2,044,232 B (1.9 MB) | Auto-updater (exe-only, ADR-003, 1 entry) |
| **Job Tracker** | `ProjectTrackingToolSetup.exe` | 39,108,336 B (37.3 MB) | Inno Setup installer |
| **Job Tracker** | `ProjectTrackingTool.zip` | 57,508,860 B (54.8 MB) | Auto-updater (full-folder, 260 entries) |

Total: 8 assets across 4 drafts. Total payload uploaded: ~275 MB.

---

## 5. Updater asset-name verification

Asset filenames are byte-exact matches to the names each tool's `updater.py` expects (commons facade looks up by the `ZIP_ASSET_NAME` constant). Any mismatch would silently break in-app auto-update for existing users.

| App | Expected (in `updater.py`) | Uploaded | Match |
|-----|-----------------------------|----------|-------|
| Phoenix CAD | `LabLayoutTool.zip` | `LabLayoutTool.zip` | ✅ |
| Phoenix Checkout | `PhoenixCheckoutTool.zip` | `PhoenixCheckoutTool.zip` | ✅ |
| ValveMaster | `PhoenixMasterTool.zip` | `PhoenixMasterTool.zip` | ✅ |
| Job Tracker | `ProjectTrackingTool.zip` | `ProjectTrackingTool.zip` | ✅ |

All 4 match exactly (case-sensitive). Auto-update path will work end-to-end once the drafts publish.

---

## 6. Release notes verification

Per-draft release notes were authored from `PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md` § 6 and uploaded via `gh release create --notes-file`. Each draft body:

- ✅ Starts with `# <App Name> v<X.Y.Z>` title heading
- ✅ Subheads "What changed" / "Auto-updater compatibility" / "Install" / "Cross-reference"
- ✅ Cross-reference link points at the canonical 4-app promotion plan in `phoenix-commons` repo
- ✅ Mentions retrofit identifier (Phase 3A / 3B / Wave 8a / Wave 8b) per app
- ✅ Mentions visible-change band ("≈ 0%") per app
- ✅ Mentions S1-validated frozen build under Python 3.12
- ✅ Mentions the correct updater payload contract per app (full-folder vs exe-only)
- ✅ Specific to-app callouts:
  - CAD: Phase 3A merge commit `79c7003`
  - Checkout: openpyxl dependency declaration, Phase 3B merge `26a4689`
  - VM: Decoded Fields valid/invalid color states preserved (B8a fix), AppId GUID preserved
  - JT: starter_package removal, Excel/xlsb/PDF dep preservation, AppName-hashed upgrade detection

Tone is factual and conservative — no overstated features.

---

## 7. Remaining final approval steps

Steps below have **not** been executed. Each requires explicit operator approval.

| # | Action | Status |
|---|--------|--------|
| 1 | Operator final review of each draft (web UI or `gh release view`) | ⏳ pending |
| 2 | Operator decision on optional `*_FullInstall.zip` uploads — yes/no per app | ⏳ pending |
| 3 | Operator approval to publish — per app or all-at-once | ⏳ pending |
| 4 | Publish each draft (web UI "Publish" button OR `gh release edit <tag> --draft=false`) | ⏳ pending |
| 5 | (Post-publish) Verify the auto-updater path on each tool by triggering an in-app update check from a v<previous> installed instance | ⏳ pending |

### Optional: full-install zip uploads

Operator can authorize uploading the full-install zip per app at any time before publication:

| App | Full-install zip | Size |
|-----|-------------------|------|
| Phoenix CAD | `LabLayoutTool_FullInstall.zip` | 55.6 MB |
| Phoenix Checkout | `PhoenixCheckoutTool_FullInstall.zip` | — |
| ValveMaster | `PhoenixMasterTool_FullInstall.zip` | — |
| Job Tracker | `ProjectTrackingTool_FullInstall.zip` | 54.9 MB |

Command per app (operator authorizes selectively):
```bash
gh release upload v<X.Y.Z> dist/<App>_FullInstall.zip
```

### Publication commands

When operator approves publication:
```bash
# per app — operator's call whether per-tool sequential or all-at-once
gh release edit v0.1.2 --draft=false --repo JustinGlave/lab-layout-tool
gh release edit v1.7.1 --draft=false --repo JustinGlave/Phoenix-Checkout-Tool
gh release edit v1.1.1 --draft=false --repo JustinGlave/phoenix-master-tool
gh release edit v1.8.6 --draft=false --repo JustinGlave/project-tracking-tool
```

After publication, each release becomes "latest" for its repo and end users + the in-app auto-updater can see it.

---

## 8. Confirmation

- **No source code changed.** No commits to any repo's source tree.
- **No `version.py` changed.** Versions already at the targeted final values in the RC commits.
- **No rebuild occurred.** Existing RC artifacts (built 2026-05-30 / 31 under Python 3.12.10) uploaded as-is.
- **No production deployment.** Drafts are admin-visible only; not published to end users.
- **No releases published.** All 4 are in `draft: true` state.
- **No updater contract changes.** Asset names + payload shapes preserved.
- **No `installer.iss` changes.** AppId / install path / user-data path per-tool preservation intact.
- **No tag renames.** RC `-rc1` tags remain immutable; stable tags are separate annotated tags at the same SHAs.
- **No optional assets uploaded** (`*_FullInstall.zip` left out per brief Step 5).

---

## Awaiting operator action

Choose any combination:

1. **Review each draft** in the web UI (URLs in § 3)
2. **Authorize selective `*_FullInstall.zip` uploads** if any tool needs the manual-install fallback
3. **Edit release notes** if any wording needs tweaking (operator can edit drafts directly; or hand back to me for revision)
4. **Approve publication** — per app or all-at-once

Until step 4, the 4 releases are not visible to end users.
