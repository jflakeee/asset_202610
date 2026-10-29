# Canonical catalog consistency review

The84 original design IDs, corresponding GLB hashes,84 thumbnail hashes, six contact sheets and CSV metadata are checked together. Triangles, X/Y/Z dimensions, socket counts and socket names are read from actual exported GLBs. Three independent metadata mutations per model are rejected (252 controls).

Run `python quality/catalog-review-work-v6/check_catalog.py /generated/disposable/repository` after the normal rebuild/bootstrap. Requires NumPy and Pillow already used by the project. CATALOG.md is generated from checked rows and explicitly separates unique models, palette themes, LOD candidates and other expansions.

These are geometry previews, not GPU screenshots. Thumbnail art approval and final sales document/license signoff remain pending; AT15 is not complete. Existing thumbnails are reused from creation/review_media_output; this check does not regenerate or improve their visual quality.
