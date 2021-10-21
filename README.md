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
| Object export with local coordinates, only selected objects | ✅ | ✅ | ✅ |
| Object export without local coordinates, all objects | ✅ | ✅ | ✅ |
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
```
<!--tableend-->
