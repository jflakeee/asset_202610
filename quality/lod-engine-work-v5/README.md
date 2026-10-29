# 84-model Godot LOD / collider review

Internal engineering evidence, not an approved sales release. This extends the 91 LOD candidates and 77 pending omission decisions in ../lod-catalog-work-v4/.

`godot/lod_asset.gd` loads three visual levels, switches at natural12/28 metres or boundary18/40 metres (grass cull25 metres) and creates the selected collider once. These distances are review defaults, not measured mobile settings. Pending omissions reuse the nearest higher-detail file; they are not new exported models or approved exceptions. Only Moss is imported in this test; the prior three-theme geometry invariance evidence is separate.

Collider source coordinates are Z-up, converted to Godot Y-up as `(x,z,-y)`. Compound convex, box, cylinder and endpoint-defined capsule descriptors are supported. Use --colliders ../collider-work-v8/overrides.json with prepare.py to select the hash-bound24-model revision. The current downloadable review project uses that revision; original GLBs remain unchanged. Native visibility ranges are configured for perspective cameras; orthographic mode fixes LOD0 and clears all ranges. Official4.7.2 import files explicitly disable automatic LODs, and the test reads both those options and imported RenderingServer surface data to check zero automatic LOD levels. GPU evaluation of visibility ranges remains untested.

Twelve vegetation models with no descriptors remain nonblocking. Changing a visual level never replaces the StaticBody, CollisionShape nodes, shape resources or margin settings. Caller supplies camera distance to `update_distance`; this review component does not create a camera or run a per-frame scan itself.

The checks instantiate all84 canonical models in official Godot4.7.2 Linux headless, then test seven distances per category including exact boundaries and return to LOD0. Each transition checks triangle count, exactly one visible level, socket transforms, persistent collider IDs/data/transforms and actual physics ray hits through each collider component. V8 additionally checks capsule endpoint world transforms/radii/heights,16-point rock hulls,1mm margins and an above-capsule ray with no canopy collider. Negative controls disable all shapes (rays must stop hitting) change a shape margin and move an existing socket (comparison must reject both). Levels outside0–2 are clamped. Null negative-control results mean not applicable, not a performed pass.

No character passage, GPU frame, silhouette appearance, device performance, art approval or omission approval is established by these tests. V8 collider fidelity still requires review: simplified rocks can have inward gaps up to12.1cm and rounded tree caps extend below ground. AT12 therefore remains incomplete.

## Reproduce

Use the generated disposable repository described in ../completion-work-v1/STATUS.md, and unzip the LOD candidate archive into a folder containing models/ and reports/catalog.json. Then:

```sh
python quality/lod-engine-work-v5/prepare.py /disposable/repository /extracted/trailwood_lod_review --colliders quality/collider-work-v8/overrides.json
/path/to/Godot_v4.7.2-stable_linux.x86_64 --headless --path quality/lod-engine-work-v5/godot --editor --import
/path/to/Godot_v4.7.2-stable_linux.x86_64 --headless --path quality/lod-engine-work-v5/godot --script check.gd
```

`prepare.py` checks original and reduced GLB hashes before copying; use a fresh output folder when inputs change. The downloadable archive includes the175 unique GLBs and runnable native project, with explicit import settings and without import cache. Import it before running the script. See reports/summary.json for measured counts and the full report for individual transitions. The archive includes internal review scripts; it is not the customer ZIP.
