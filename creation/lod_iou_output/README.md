# LOD silhouette verification

Exported GLB triangles; source Z-up; front +X/up +Z, side +Y/up +Z, 45-degree XY diagonal/up +Z, top X/Y; per-pair union bounds shared by both meshes; uniform scale; approximately8px padding; nearest integer triangle rasterization; no antialiasing or culling

Dark gray = shared silhouette; red = LOD0 only; green = LOD1 only.
The actual threshold result is in report.json. FAIL is retained and is not converted into an exception automatically. LOD2 has not been supplied. This test does not establish GPU quality, collider invariance, or human art approval.
