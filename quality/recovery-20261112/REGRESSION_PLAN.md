# 84 canonical assets — post-recovery regression gate (2026-11-12)

Base: main d5d2f6deea7b11054493f9da9a07d98f9bd38263
Scope: 84 canonical IDs × 3 themes. Do not count 104 unique models or 327 GLBs as 84×3 without catalog mapping.
Status: PLAN ONLY — no newly executed engine tests or release approval.

## Existing evidence (not rerun by this change)
- quality/completion-work-v1/STATUS.md: historical AT01–AT16, AT12 and AT15 NOT_RUN.
- quality/recovery-20261106/validation.json and engine_report.json: 48 recovered stone candidate entries, 144 logical scenes, 336 transition samples.
- quality/recovery-20261106/test_engine.py: isolated Godot test for stone candidates only.
- MEMORY.md: lost V9–V68 state cannot be assumed recovered.

## P0 regression acceptance
1. Enumerate the canonical 84 IDs from trailwood_godot/data/full_catalog.json; reject missing/duplicate IDs and report extra models separately.
2. Resolve each canonical ID to three themes; verify file existence, SHA-256, GLB parser validity, finite positions, indices, UVs, materials and textures. Compare invariants across themes without assuming palette bytes equal.
3. Create a disposable Godot project from a clean checkout. Import all canonical GLBs, record engine version, per-file errors/warnings, scene/node counts and asset IDs. Never mutate product GLBs.
4. Check runtime LOD0/LOD1/LOD2 bindings per asset using explicit available/omitted decisions. Do not treat reusing one candidate at two distances as two distinct LODs. Check 18m and 40m boundaries, orthographic behavior and visibility.
5. Snapshot collision bindings before and after LOD switches; check no unexpected collider changes. Separate structural assertions from real-contact physics, which requires further tests.
6. Re-run existing AT01–AT16 checks where prerequisites exist. Preserve NOT_RUN where approvals or dependencies are missing; never convert historical PASS to new PASS.
7. Emit machine-readable JSON with commit SHA, engine version, input SHA, per-asset/theme outcomes, command, timestamp, error logs and skipped checks. Exit nonzero on any required failure.
8. Keep recovered stone candidates out of final product integration pending art, GPU, physics and mobile reviews.

## Release gates
- Test PASS: only after fresh logs and report artifacts exist for this commit.
- Commit confirmed: GitHub branch SHA verified.
- Deployment confirmed: Actions completed/success with matching SHA.
- Public verified: actual HTTP response and published file SHA match.
- Sales approved: separate human art, license and device performance signoff.

## Reproduction starting points
```sh
python creation/rebuild_all.py --out /tmp/trailwood-rebuild
python quality/completion-work-v1/prepare_checkout.py /tmp/trailwood-checkout /tmp/trailwood-rebuild
python quality/recovery-20261106/test_engine.py
```
The final command only checks the recovered stone subset. Do not claim it validates all 84.

## Open issues
- Confirm availability of Godot and official glTF validator in CI.
- Implement all-84 disposable-project engine runner and failure-injection fixtures.
- Capture GPU, shadow/GI, 28-view visual comparisons, real collision contacts, Android/iOS FPS and memory.
- Rebuild hash-bound omission/LOD decisions before integration.

No change to main, production assets or Pages is authorized by this planning commit.
