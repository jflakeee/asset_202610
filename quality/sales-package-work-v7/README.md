# Canonical customer-layout previews (internal review)

This implements the section9 full/trial file boundary. It does not authorize sales or public free distribution. `package.py --channel sales` exits2 before creating output because unresolved build gates remain. The pending LICENSE notice is not a final customer license.

Full:84 unique LOD0 models ×3 themes =252 GLBs,84 thumbnails,6 contact sheets,6 static assembly JSONs with matching preview images,3 external palettes and one sanitized editable Blender source.367 total files including manifests and documents.

Trial: exact8 design IDs, Moss only,8 GLBs and8 thumbnails.26 total files. No full-source Blender file, full-pack examples, Dry or Dusk assets. The existing low-detail91 reduced Moss candidates remain separate engineering deliverables; these layout previews intentionally contain LOD0 only and do not satisfy the final LOD shipping requirement.

Only explicit paths from the canonical JSON records and six example records are copied. CSV is derived from the JSON export inventory. Scene model paths are rewritten to the included GLBs. Research, generators, recipes, credentials, caches and backup files are not collected. Customer runtime/scripts may be added explicitly in a later native-example deliverable; this preview contains static assembly JSON, not a playable game.

Blender4.5.9 LTS reopens a separate source copy with unchanged geometry/UV/object transforms and unchanged packed-image bytes. Both the image path and its packed-file path are relative, render output is relative, and there are no linked libraries or text datablocks. Source and result SHA-256 are recorded. This path audit does not establish authorship or art quality.

## Reproduce

Start with the generated disposable repository from ../completion-work-v1/STATUS.md. Open its creation/blender_sources_output/Trailwood.blend through the audit script in official Blender4.5.9, passing the input, new output and report paths:

```sh
mkdir -p quality/sales-package-work-v7/sanitized
blender --background --python-exit-code 1 --python quality/sales-package-work-v7/audit_blend.py -- /repository/creation/blender_sources_output/Trailwood.blend /repository/quality/sales-package-work-v7/sanitized/Trailwood.blend /repository/quality/sales-package-work-v7/reports/blend_audit.json
python quality/sales-package-work-v7/test_package.py /generated/repository
python quality/sales-package-work-v7/package.py /generated/repository --out /new/empty/full-layout --subset full
python quality/sales-package-work-v7/package.py /generated/repository --out /new/empty/trial-layout --subset trial
```

The test writes two downloadable review ZIPs and a report. It checks deterministic ZIP bytes, package hashes, exact ID/theme sets, resolved assembly references, absent internal code/path leakage, filesystem/ZIP extras, mutation, missing files, symlinks, traversal, duplicate entries, malformed/retagged manifests, self-consistent manifest tampering, paid-only model contamination in trial and sales-mode refusal. Trusted plans are regenerated from canonical source records; a changed manifest cannot approve itself.

## Engineering work still open

- Section23.3 collider audit finds24 canonical model differences: all12 trees use other shapes/counts than the capsule contract and all12 rocks exceed the16-vertex proxy limit. Fidelity and3cm outward error are not established. Engine collision stability tests do not resolve these differences.
- Ship reduced models across all themes after candidate/art review; resolve77 omission decisions.
- Complete customer native Godot scenes, shared-material reimport checks and actual GPU preview images.
- Complete source/provenance signoff, final terms, human art approval and physical Android/iOS performance measurements.

See reports/ for measured evidence. No missing gate has been automatically changed to approval.

[Full layout review ZIP](full_customer_layout_review_20261029.zip) · [Exact8 trial layout review ZIP](trial_customer_layout_review_20261029.zip) · [Package checks](reports/package_validation.json) · [Editable-source audit](reports/blend_audit.json) · [Collider differences](reports/collider_contract.json)
