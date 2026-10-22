# Browser viewer dependency

Three.js 0.170.0 (MIT): https://github.com/mrdoob/three.js/tree/r170

Vendored files: three.module.js, GLTFLoader.js, OrbitControls.js, BufferGeometryUtils.js.
GLTFLoader's relative BufferGeometryUtils import was adjusted to the flat vendor directory.
The full upstream license is retained at vendor/LICENSE. This dependency license does not license the Trailwood assets.

The viewer displays original LOD0 GLBs. It does not implement Godot collision, wind shaders, automatic LOD switching or mobile performance certification.
