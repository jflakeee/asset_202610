"""Check the body and lid box parts at one-degree increments; hinge hardware is excluded."""
import numpy as np
from build import build

a = build()
pivot = np.array(a['hinge_pivot'])
split = a['lid_component_start']
body = [p for p in a['components'][:split] if p['name'] != 'hinge_pin']
lid = [p for p in a['components'][split:] if p['name'] != 'rivet']

def overlaps(body_part, lid_part, theta):
    body_vertices = np.array(body_part['vertices'])
    lid_vertices = np.array(lid_part['vertices'])
    c, s = np.cos(theta), np.sin(theta)
    rotation = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    lid_vertices = (lid_vertices - pivot) @ rotation.T + pivot
    axes = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1]), rotation[:, 1], rotation[:, 2]]
    return all(min((body_vertices @ axis).max(), (lid_vertices @ axis).max()) - max((body_vertices @ axis).min(), (lid_vertices @ axis).min()) > 1e-5 for axis in axes)

for degrees in range(106):
    for b in body:
        for l in lid:
            assert not overlaps(b, l, np.deg2rad(degrees)), (degrees, b['name'], l['name'])
print('PASS 0–105 degrees: body/lid box intersections; hinge pins and rivets excluded')
