# \[WIP\]PewPewLive-MeshExporter
A [Blender](https://www.blender.org/) 3.3+ add-on for converting scenes into [PewPew Live](https://pewpew.live/) 3D models

### Using Blender 2.79-3.2?
The last release that supports your Blender version is [v0.6.1-r2](https://github.com/ModEngineer/PewPewLive-MeshExporter/releases/tag/v0.6.1-r2). This version will not be maintained, and files saved with newer versions will be incompatible with this version.

### Installation Instructions:
1. Download a [release](https://github.com/ModEngineer/PewPewLive-MeshExporter/releases)
2. Open Edit > Preferences in Blender
3. Go to the Add-ons tab
4. Click "Install..."
5. Select the .zip you downloaded and click "Install Add-on"
6. Tick the checkbox next to "Import-Export: PewPew Live Mesh Exporter." If you are using a Blender version below 2.90, you may get a warning about the add-on being for a future version. While the current version of Blender will always be the priority, I will try to maintain backwards compatibility through one way or another.

### What is `decompress_meshes.lua`?
This add-on compresses meshes that it exports, which need to be decompressed. `decompress_meshes.lua` is the script used to decompress the exported meshes and must be included in your PewPew Live level. It can be found [here](https://github.com/ModEngineer/PewPewLive-Code-Snippets/blob/main/utils/mesh/decompress_meshes.lua).

### What are segments?
Segments are PewPew Live's version of edges. By default, each edge is exported to its own segment, but the segments panel (which should be near the vertex groups panel) can be used to merge multiple edges into a single segment.

### What are these vertex groups created by the segments?
These are used to keep track of edges. This is done because properties cannot be applied to vertices, edges, or faces and because their indices are unstable. Unless you know what you are doing, __DO NOT__ create or edit any vertex groups with a name such as `pewpew_segment_SegmentNameHere_vgroup`.

### Found a bug?
Open an [issue](https://github.com/ModEngineer/PewPewLive-MeshExporter/issues)

<!--### Test Results (no longer updated, writing tests for newer versions is becoming too complicated)--> <!-- The below "tablestart" and "tableend" comments must be kept in their current formats. They are used by Github Actions to automatically update the test results displayed here. -->
<!--tablestart-->
<!--tableend-->
