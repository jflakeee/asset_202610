# Asset quality priority — 2026-10-27

User direction: defer demo-page improvements. Prioritize original asset quality suitable for paid sale. Current assets remain prototypes; passing functional tests does not certify commercial art quality.

## Review evidence
Reviewed build_items.py, core.py and the current six-item contact sheet.
- Coin (100 triangles): relief exists only on negative Z; the displayed view reads as a blank polygon. Add a readable rim and two-sided relief, then validate multiple views.
- Chest (56 triangles): solid body and triangular lid, front-only bands/lock. Side and rear views read as a plain box. Rebuild with interior, separate lid and hinge pivot; continuous bands, corner protection and visible closure.
- Iron ore (14 triangles): single grey hull and tiny mineral piece. Create a stronger clustered silhouette and visible mineral planes on multiple faces.
- Rope (980 triangles): sixty capped beam segments for three rings. Replace redundant internal caps with a continuous tube; preserve the coil opening, winding direction, tie and loose end.
- Potion (152 triangles): opaque red body and blank label. Improve neck/shoulder silhouette, stopper fit and a readable original label motif.
- Wood (116 triangles): uniform cylinder with flat end caps. Add taper, distinct cut faces and restrained bark/cut details.

## Work order
1. Establish consistent shape language, palette and front convention (-Z); review neutral-lit front/back/side/top images.
2. Rebuild chest, coin, ore and rope before adding more item types.
3. Bring potion and wood to the same visual standard.
4. Validate and package only after visual approval; defer demo features.

## Acceptance gates
- Recognizable at 64px and 128px with no label; six-view and three-quarter inspection. Thumbnail orientation must agree with model front.
- No unintended gaps, inverted or degenerate triangles, floating details or internal duplicate faces. Deliberate separate components documented.
- Meter scale, Y-up, grounded placement and stable names; chest lid pivots correctly and opens without collisions.
- Budget is measured per asset, not a blanket triangle target. Rope should be simplified with no visible loss in winding readability.
- PBR parameters must fit wood, metal and cloth. Current exporter assigns every material metallic=0 and roughness=1; this is insufficient to judge a metal finish. Choose texture/UV strategy deliberately before claiming engine-ready PBR.
- Check GLB with a validator and import into target engines. Inspect GPU-rendered color, normals and materials; CPU fallback previews alone are insufficient.
- Supply editable source, GLB, icons, scale/pivot notes, material usage and provenance/license documentation.
- No commercial-ready label until art, topology, engine compatibility and packaging gates pass.

## Deferred
Further browser demo features, feature-count growth, additional item categories and cosmetic demo polishing.
Existing demo remains available as a functional prototype.
