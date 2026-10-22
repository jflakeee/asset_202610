"""Render every shipped GLB into a compact actual-geometry gallery thumbnail.

This deterministic orthographic CPU renderer uses exported triangles and embedded
palette pixels. It is not an engine screenshot, generated artwork or art approval.
Run from any working directory: python web/build_gallery.py
"""
from pathlib import Path
import hashlib
import json
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'creation'))
from verify_glb import load_glb

CATEGORIES = {
    'TREE': '나무', 'ROCK': '바위', 'VEG': '덤불·풀', 'SHRUB': '덤불·풀',
    'GRASS': '덤불·풀', 'PROP': '숲 소품', 'STUMP': '숲 소품', 'LOG': '숲 소품',
    'WOOD': '목재 경계', 'STONE': '석재 경계', 'SIGN': '표지판·상자',
    'CRATE': '표지판·상자', 'PAVER': '길·계단', 'STEPS': '길·계단',
    'BENCH': '가구', 'TABLE': '가구', 'TERMINAL': '연결 부품',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(path, target):
    mesh = load_glb(path)
    p = mesh['positions'].astype(float)
    faces = mesh['indices'].reshape(-1, 3)
    assert len(faces) and np.isfinite(p).all()
    # glTF is Y-up. Project from a fixed oblique view, with per-model framing.
    direction = np.array([1.0, .72, 1.4]); direction /= np.linalg.norm(direction)
    right = np.cross(np.array([0., 1., 0.]), direction); right /= np.linalg.norm(right)
    up = np.cross(direction, right)
    xy = np.column_stack((p @ right, -(p @ up)))
    lo = xy.min(axis=0); hi = xy.max(axis=0)
    scale = 535 / max(float((hi-lo).max()), .001)
    xy = (xy-(hi+lo)/2)*scale + [320, 320]
    depth = (p @ direction)[faces].mean(axis=1)
    uv = mesh['uv'][faces[:, 0]]
    palette = np.asarray(mesh['image'].convert('RGB'))
    height, width = palette.shape[:2]
    colors = palette[np.clip((uv[:, 1]*height).astype(int), 0, height-1),
                     np.clip((uv[:, 0]*width).astype(int), 0, width-1)]
    normals = np.cross(p[faces[:, 1]]-p[faces[:, 0]], p[faces[:, 2]]-p[faces[:, 0]])
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths[:, None], 1e-12)
    light = np.array([-.4, .8, .5]); light /= np.linalg.norm(light)
    shade = .76 + .24*np.maximum(normals @ light, 0)
    colors = np.clip(colors*shade[:, None], 0, 255).astype(np.uint8)
    image = Image.new('RGB', (640, 640), '#e9eddf')
    draw = ImageDraw.Draw(image)
    for index in np.argsort(depth, kind='stable'):
        if lengths[index] < 1e-12:
            continue
        draw.polygon([tuple(point) for point in xy[faces[index]]], fill=tuple(colors[index]))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.resize((320, 320), Image.Resampling.LANCZOS).save(target, optimize=True)
    with Image.open(target) as check:
        assert check.size == (320, 320)
        assert len(check.getcolors(102400) or []) > 2, f'Blank thumbnail: {path}'
    return len(faces)


def main():
    source = ROOT / 'standalone_assets/manifest.json'
    manifest = json.loads(source.read_text())
    rows = {}
    for entry in manifest['entries']:
        path = ROOT / 'standalone_assets' / entry['file']
        assert digest(path) == entry['sha256'], f'Source hash mismatch: {path}'
        model = entry['model']
        match = re.fullmatch(r'(.+)_LOD(\d+)', model)
        asset_id, lod = (match[1], int(match[2])) if match else (model, None)
        record = rows.setdefault(model, dict(model=model, asset_id=asset_id, lod=lod,
            category=CATEGORIES.get(asset_id.split('_')[1], '기타'), themes={}))
        target = ROOT / 'web/thumbnails' / entry['theme'] / (model+'.png')
        triangles = render(path, target)
        assert triangles == entry['triangles']
        record['themes'][entry['theme']] = dict(file=str(path.relative_to(ROOT)),
            thumbnail=str(target.relative_to(ROOT)), triangles=triangles,
            glb_sha256=entry['sha256'], thumbnail_sha256=digest(target))
    assert len(rows) == 109 and len(manifest['entries']) == 327
    assert all(set(row['themes']) == {'MOSS_01', 'DRY_01', 'DUSK_01'} for row in rows.values())
    result = dict(version='1.0', unique_models=104, model_files_per_theme=109,
        thumbnail_count=327, source_manifest_sha256=digest(source),
        renderer='Actual GLB triangles and embedded palette; orthographic CPU projection, 320px',
        art_approval='PENDING', assets=sorted(rows.values(), key=lambda row: row['model']))
    (ROOT / 'web/gallery.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(status='PASS', rows=len(rows), thumbnails=327, resolution=320)))


if __name__ == '__main__':
    main()
