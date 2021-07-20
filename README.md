# \[WIP\]PewPewLive-MeshExporter
A [Blender](https://www.blender.org/) 2.9x plugin for converting scenes into [PewPew Live](https://pewpew.live/) 3D models

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
