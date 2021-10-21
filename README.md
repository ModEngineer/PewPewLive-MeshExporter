# \[WIP\]PewPewLive-MeshExporter
A [Blender](https://www.blender.org/) 2.79+ add-on for converting scenes into [PewPew Live](https://pewpew.live/) 3D models

### Installation Instructions:
1. Download a [release](https://github.com/ModEngineer/PewPewLive-MeshExporter/releases)
2. Open Edit > Preferences in Blender
3. Go to the Add-ons tab
4. Click "Install..."
5. Select the .zip you downloaded and click "Install Add-on"
6. Tick the checkbox next to "Import-Export: PewPew Live Mesh Exporter." If you are using a Blender version below 2.90, you may get a warning about the add-on being for a future version. While the current version of Blender will always be the priority, I will try to maintain backwards compatibility through one way or another.

### What is `decompresscolors.lua`?
This add-on losslessly compresses colors it exports, which need to be decompressed. `decompresscolors.lua` is the script used to decompress the exported colors and must be included with your PewPew Live level. It can be found [here](https://github.com/ModEngineer/PewPewLive-Code-Snippets/blob/main/mesh_utils/decompresscolors.lua).

### What are segments?
Segments are PewPew Live's version of edges. By default, each edge is exported to its own segment, but the segments panel (which should be near the vertex groups panel) can be used to merge multiple edges into a single segment.

### What are these vertex groups created by the segments?
These are used to keep track of edges. This is done because properties cannot be applied to vertices, edges, or faces and because their indices are unstable. Unless you know what you are doing, __DO NOT__ create or edit any vertex groups with a name such as `pewpew_segment_SegmentNameHere_vgroup`.

### Found a bug?
Open an [issue](https://github.com/ModEngineer/PewPewLive-MeshExporter/issues)

### Test Results <!-- The below "tablestart" and "tableend" comments must be kept in their current formats. They are used by Github Actions to automatically update the test results displayed here. -->
<!--tablestart-->
| Test | 2.90 | 2.80 | 2.79 |
| --- | --- | --- | --- |
| Add-on registration | ✅ | ✅ | ✅ |
| Vertex color operator | ✅ | ✅ | ✅ |
| Object export with local coordinates, only selected objects | ✅ | ✅ | ❌ |
| Object export without local coordinates, all objects | ✅ | ✅ | ❌ |
| Add-on unregistration | ✅ | ✅ | ✅ |
| Tests (this will show as an error if the test sotware had an error) | ✅ | ✅ | ✅ |

Any errors produced during tests will be displayed below:
Tracebacks for Blender version 2.90:
```py
```
Tracebacks for Blender version 2.80:
```py
```
Tracebacks for Blender version 2.79:
```py
Traceback (most recent call last):
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/.github/workflows/blender_tests/blender_tests.py", line 92, in <module>
    bpy.ops.pewpew_live_meshexporter.exportmeshfromscene(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test.lua"), max_decimal_digits=3, multiplier=5, only_selected=True, use_local=True, exclude_seamed_edges=True, export_color=True, color_decompressor_location="decompresscolors", use_segments=False, use_fixedpoint=False)
  File "/snap/blender/20/2.79/scripts/modules/bpy/ops.py", line 189, in __call__
    ret = op_call(self.idname_py(), None, kw)
RuntimeError: Error: Traceback (most recent call last):
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/exporters/exportmesh.py", line 232, in execute
    self.use_segments))
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/exporters/exportmesh.py", line 25, in serializeMesh
    mesh = obj.to_mesh(bpy.context.scene, False)
TypeError: Object.to_mesh(): required parameter "settings" not specified

location: /snap/blender/20/2.79/scripts/modules/bpy/ops.py:189




--------------------

Traceback (most recent call last):
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/.github/workflows/blender_tests/blender_tests.py", line 100, in <module>
    bpy.ops.pewpew_live_meshexporter.exportmeshfromscene(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests",  "test2.lua"), max_decimal_digits=3, multiplier=5, only_selected=False, use_local=False, exclude_seamed_edges=True, export_color=True, color_decompressor_location="decompresscolors", use_segments=False, use_fixedpoint=False)
  File "/snap/blender/20/2.79/scripts/modules/bpy/ops.py", line 189, in __call__
    ret = op_call(self.idname_py(), None, kw)
RuntimeError: Error: Traceback (most recent call last):
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/exporters/exportmesh.py", line 232, in execute
    self.use_segments))
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/exporters/exportmesh.py", line 25, in serializeMesh
    mesh = obj.to_mesh(bpy.context.scene, False)
TypeError: Object.to_mesh(): required parameter "settings" not specified

location: /snap/blender/20/2.79/scripts/modules/bpy/ops.py:189


```
<!--tableend-->
