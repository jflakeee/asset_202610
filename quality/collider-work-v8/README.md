# Canonical tree / rock collider review v8

This changes physics descriptors for24 canonical models, never the visible GLBs. The original catalog remains intact; overrides.json binds its SHA-256 and all24 source GLB hashes. It is a review revision, not a human approval or sales release.

Trees:12 models,2 capsules each. Every capsule uses only the explicit trunk's ordered rings; branches and canopy are excluded. All vertices of each original trunk triangle lie inside the same convex capsule, proving full triangle containment. Endpoints are sphere centers in sourceZ-up metres. Godot converts(x,y,z) to(x,z,-y), sets totalheight to endpoint distance+2radius and rotates localY along that axis. The rounded caps extend below the flat trunk base; the maximum extension is about0.238m before1mm engine margin. This is an explicit approximation, not a ground-clamped shape.

Rocks:12 models,29 original convex components retained. Each candidate hull has at most16 source vertices, so it remains inside its verified source component. This preserves inter-component voids and introduces no new geometric bridges. Numerical differences from old float32 descriptors are also reported. The directed distance from original hull to proxy is evaluated at every original vertex; point-to-triangle distances are not sampled support values. The simplified shapes leave inward gaps up to about0.121m, and every component exceeds the supplementary3cm inward review target. The original design's outward3cm rule passes geometrically, but this does not establish acceptable contact fidelity.

An optional outward-refinement experiment is retained in reports/rocks_optimized*.json. It reduces the maximum inward gap to about0.091m while keeping outward displacement under0.029m. It can affect narrow gaps and is NOT selected by build.py or the customer/engine artifacts.

Every selected part requests Godot margin0.001m. check_rock_distances.py independently checks convex distances with constrained numerical minimization; the outward acceptance budget includes that setting and1µm numerical allowance. This is geometric evidence plus a configured engine margin, not a complete physical contact certification.

## Reproduce

Use the generated disposable repository described in ../completion-work-v1/STATUS.md. Python dependencies are NumPy/SciPy/Pillow/Matplotlib already used by the project.

```sh
python quality/collider-work-v8/build.py /generated/repository
python quality/collider-work-v8/verify.py
python quality/collider-work-v8/check_rock_distances.py /generated/repository
python quality/collider-work-v8/render.py /generated/repository
python quality/lod-engine-work-v5/prepare.py /generated/repository /extracted/trailwood_lod_review --colliders quality/collider-work-v8/overrides.json
Godot_v4.7.2-stable_linux.x86_64 --headless --path quality/lod-engine-work-v5/godot --editor --import
Godot_v4.7.2-stable_linux.x86_64 --headless --path quality/lod-engine-work-v5/godot --script check.gd
python quality/sales-package-work-v7/test_package.py /generated/repository quality/collider-work-v8/overrides.json
```

The Godot check independently verifies each capsule's world endpoints/radius/height, each rock point/vertex budget and the1mm margin setting. It runs the existing84-model LOD switch and actual physics-ray checks, detects disabled-shape/margin/socket mutations and verifies that a ray above the tree capsules meets no canopy collider. A headless pass is not GPU rendering or character traversal proof.

Previews are actual exported geometry with teal collider wires. They are review overlays, not engine screenshots or marketing renders. Art and contact-fidelity decisions remain pending; source models and previous engineering reports stay reproducible.

[Tree overlays](previews/tree_sheet.png) · [Rock overlays](previews/rock_sheet.png) · [24-model review queue](review_queue.csv) · [Measured summary](reports/summary.json) · [Independent rock distances](reports/rock_distance_qp.json)
