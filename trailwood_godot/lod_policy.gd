extends RefCounted

# Hysteresis: keep current state in the 80..100 px band.
static func choose(current_lod: int, height_px: float) -> int:
	if current_lod == 0 and height_px < 80.0:
		return 1
	if current_lod == 1 and height_px > 100.0:
		return 0
	return current_lod
