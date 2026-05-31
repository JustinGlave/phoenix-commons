# Phoenix 4-App RC — Kickoff Readiness

> **Status:** all 5 plan decisions resolved 2026-05-29. RC execution unblocked.
> **Companion:** `PHOENIX_4_APP_RC_RELEASE_PLAN.md`.

---

## What's resolved

| # | Decision | Resolution |
|---|----------|------------|
| 1 | Version bump | Patch-bump all 4: `v0.1.2-rc1` / `v1.7.1-rc1` / `v1.1.1-rc1` / `v1.8.6-rc1` |
| 2 | Tag promotion | Keep `-rc1` immutable; create final stable tags as separate annotated tags at the same SHA after bake |
| 3 | Bake window | **WAIVED 2026-05-30.** RC progression proceeds after successful operator validation. |
| 4 | Build order | CAD → Checkout → ValveMaster → Job Tracker |
| 5 | Asset upload | Wait until all 4 RC builds pass before uploading GitHub Release assets |

## What's ready

All 4 production tools are operator-validated and structurally release-ready:

| Tool | Source HEAD | Hardening / Retrofit state |
|------|-------------|-----------------------------|
| Phoenix CAD | `release-hardening/cad-rc-readiness` @ `38cb3a5` | hardening branch pushed; needs merge to `master` + version bump |
| Phoenix Checkout | `release-hardening/checkout-rc-readiness` @ `9b638cb` | hardening + openpyxl fix pushed; needs merge to `main` + version bump |
| ValveMaster | `main` @ `631dbe8` (Wave 8a merged) | needs only version bump |
| Job Tracker | `main` @ `6a0d60b` (Wave 8b merged) | needs only version bump |

## Next operator action

Issue the first RC execution brief — **Phoenix CAD v0.1.2-rc1**:

```
# Operator brief template — first RC build (Phoenix CAD)

Proceed with: Phoenix CAD v0.1.2-rc1

1. Merge release-hardening/cad-rc-readiness → master (--no-ff)
2. Bump version.py to 0.1.2; update README + CHANGELOG.md
3. Commit version bump on master
4. Create release/v0.1.2-rc1 branch from the version-bump commit
5. Create annotated tag v0.1.2-rc1 on the same SHA
6. Push master + release branch + tag
7. Build artifacts via build.bat (Python 3.12 venv)
8. Verify 4 artifacts produced + commons bundled + updater zip
   full-folder contract intact
9. Operator interactive validation:
   - install dist\LabLayoutToolSetup.exe
   - launch installed exe, 5-min S1 idle
   - visual review (≈ 0% change vs prior v0.1.1)
   - upgrade smoke (install v0.1.2 over v0.1.1 if you have it)
10. Author WAVE_RC_CAD_v0.1.2_RC1_REPORT.md on commons
11. Push commons doc

Do NOT:
- create GitHub Release yet (Decision #5)
- upload assets yet (Decision #5)
- proceed to Checkout RC until CAD bakes 1 day (Decision #3)
- promote -rc1 tag (Decision #2)
```

Subsequent RCs follow the same pattern with their respective tool names + versions.

## Doc status

- ✅ Plan committed: `PHOENIX_4_APP_RC_RELEASE_PLAN.md` (updated with all 5 decisions)
- ✅ This readiness summary: `PHOENIX_4_APP_RC_KICKOFF_READY.md`
- ⏳ Per-RC reports: `WAVE_RC_<TOOL>_v<X.Y.Z>_RC1_REPORT.md` (1 per RC build, authored at RC time)
- ⏳ Coordinated release closure report: `PHOENIX_4_APP_RC_CLOSURE_REPORT.md` (after all 4 baked + GitHub Releases published)

## What has NOT happened

- ❌ No version.py bumps applied
- ❌ No hardening branches merged to mainline
- ❌ No RC branches created
- ❌ No RC tags created
- ❌ No builds executed
- ❌ No GitHub Release drafts authored on GitHub
- ❌ No installer or zip assets uploaded
- ❌ No production deployment

All work to date is read-only / decision-tracking only.

---

*Awaits operator kickoff signal: "Proceed with Phoenix CAD v0.1.2-rc1".*
