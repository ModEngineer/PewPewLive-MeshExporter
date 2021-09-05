# \[WIP\]PewPewLive-MeshExporter
A [Blender](https://www.blender.org/) 2.9+ plugin for converting scenes into [PewPew Live](https://pewpew.live/) 3D models

### What about 2.79?
[SKPG-Tech](https://github.com/SKPG-Tech/) maintains an [unofficial 2.79 version](https://github.com/SKPG-Tech/PewPewLive-MeshExporter). You can use that if you want to, but I have no control over it aside from sending a pull request.

### Installation Instructions:
1. Download a [release](https://github.com/ModEngineer/PewPewLive-MeshExporter/releases)
2. Open Edit > Preferences in Blender
3. Go to the Add-ons tab
4. Click "Install..."
5. Select the .zip you downloaded and click "Install Add-on"
6. Tick the checkbox next to "Import-Export: PewPew Live Mesh Exporter"

### What is `decompresscolors.lua`?
This add-on losslessly compresses colors it exports, which need to be decompressed. `decompresscolors.lua` is the script used to decompress the exported colors and must be included with your PewPew Live level. It can be found [here](https://github.com/ModEngineer/PewPewLive-Code-Snippets/blob/main/mesh_utils/decompresscolors.lua).

### Found a bug?
Open an [issue](https://github.com/ModEngineer/PewPewLive-MeshExporter/issues)

### Test Results <!-- The below "tablestart" and "tableend" comments must be kept in their current formats. They are used by Github Actions to automatically update the test results displayed here. -->
<!--tablestart-->| Test | 2.79 | 2.80 | 2.90 |
| --- | --- | --- | --- |
| Add-on registration | ❌ | ✅ | ✅ |
| Vertex color operator | ❌ | ✅ | ✅ |
| Object export with local coordinates, only selected objects | ❌ | ✅ | ✅ |
| Object export without local coordinates, all objects | ❌ | ✅ | ✅ |
| Add-on unregistration | ❌ | ✅ | ✅ |
| Tests (this will show as an error if the test sotware had an error) | ✅ | ✅ | ✅ |

Any errors produced during tests will be displayed below:
Tracebacks for Blender version 2.79:
```py
Traceback (most recent call last):
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/.github/workflows/blender_tests/blender_tests.py", line 16, in <module>
    bpy.ops.wm.addon_enable(module="ppl_meshexport_addon")
  File "/snap/blender/20/2.79/scripts/modules/bpy/ops.py", line 189, in __call__
    ret = op_call(self.idname_py(), None, kw)
RuntimeError: Error: Traceback (most recent call last):
  File "/snap/blender/20/2.79/scripts/modules/addon_utils.py", line 331, in enable
    mod = __import__(module_name)
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/__init__.py", line 19, in <module>
    from . import importlist
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/importlist.py", line 2, in <module>
    from .utils import properties
  File "/home/runner/work/PewPewLive-MeshExporter/PewPewLive-MeshExporter/tempmodulefolder/ppl_meshexport_addon/utils/properties.py", line 9
    editmode_vertex_color: bpy.props.FloatVectorProperty(
                         ^
SyntaxError: invalid syntax


```
Tracebacks for Blender version 2.80:
```py
```
Tracebacks for Blender version 2.90:
```py
```<!--tableend-->
