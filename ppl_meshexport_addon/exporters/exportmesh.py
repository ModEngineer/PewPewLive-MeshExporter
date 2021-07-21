import bpy
import bpy_extras
from bpy.props import BoolProperty, IntProperty, FloatProperty, StringProperty
import bmesh
from copy import deepcopy
from ..utils.common import cleanRound, clamp
from ..lua.luadataexport import toLua, stringKey
from ..utils.datatypes import hexint
import itertools


def correctIndex(exclusions, index):
    assert index not in exclusions, "Index to be corrected is in the exclusion list"
    return index - sum(
        1 for excludedIndex in exclusions if excludedIndex < index)


def serializeMesh(object, use_local, export_color, exclude_seamed_edges,
                  max_decimal_digits, multiplier):
    # Vertex Processing and init
    out = {}
    out[stringKey("vertexes")] = []
    out[stringKey("segments")] = []
    mesh = object.to_mesh()
    if not use_local:
        mesh.transform(object.matrix_world)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if export_color and bm.loops.layers.color.active:
        out[stringKey("colors")] = {}
    includedVertices = sorted(list(
        set(
            itertools.chain.from_iterable([
                list(edge.verts) for edge in bm.edges
                if not (exclude_seamed_edges and edge.seam)
            ]))),
                              key=lambda v: v.index)
    excludedVertexIndices = [
        vertex.index for vertex in bm.verts if vertex not in includedVertices
    ]
    for vertex in includedVertices:
        out[stringKey("vertexes")].append([
            cleanRound(vertex.co[0] * multiplier, max_decimal_digits),
            cleanRound(vertex.co[1] * multiplier, max_decimal_digits)
        ])
        z = cleanRound(vertex.co[2] * multiplier, max_decimal_digits)
        if z != 0:
            out[stringKey("vertexes")][-1].append(z)
        if export_color and bm.loops.layers.color.active:
            #Face vertices are ignored. I don't have the time to support multiple colors per vertex.
            vertexcolor = vertex.link_loops[0][bm.loops.layers.color.active]
            colorhex = hexint(
                (clamp(round(vertexcolor[0] * 255), 0, 255) << 24) +
                (clamp(round(vertexcolor[1] * 255), 0, 255) << 16) +
                (clamp(round(vertexcolor[2] * 255), 0, 255) << 8) +
                clamp(round(vertexcolor[3] * 255), 0, 255))
            out[stringKey("colors")][
                str(colorhex)] = out[stringKey("colors")].get(
                    str(colorhex),
                    []) + [correctIndex(excludedVertexIndices, vertex.index)]
    for edge in bm.edges:
        if not (exclude_seamed_edges and edge.seam):
            out[stringKey("segments")].append([
                correctIndex(excludedVertexIndices, edge.verts[0].index),
                correctIndex(excludedVertexIndices, edge.verts[1].index)
            ])
    # The following code is the color compressor. I have no clue how it works, but it works.
    if export_color and bm.loops.layers.color.active:
        for color in out[stringKey("colors")]:
            colorIndices = deepcopy(out[stringKey("colors")][color])
            colorIndices.sort()
            out[stringKey("colors")][color] = []
            partialRange = False
            for index, color_index in enumerate(colorIndices):
                if index + 1 < len(colorIndices):
                    if colorIndices[index + 1] == color_index + 1:
                        if partialRange:
                            out[stringKey(
                                "colors")][color][-1][1] = colorIndices[index +
                                                                        1]
                        else:
                            out[stringKey("colors")][color].append(
                                [color_index, colorIndices[index + 1]])
                            partialRange = True
                    else:
                        partialRange = False
                        out[stringKey("colors")][color].append(color_index)
                elif partialRange == True:
                    pass
                else:
                    out[stringKey("colors")][color].append(color_index)
    bm.free()
    return out


class ExportPPLMesh(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a PewPew Live mesh from scene. Vertex groups are joined into single segments spanning multiple vertices. Only visible objects can be exported."""
    bl_idname = "pewpew_live_meshexporter.exportmeshfromscene"
    bl_label = "PewPew Live (.lua)"

    filename_ext = ".lua"

    filter_glob: bpy.props.StringProperty(
        default="*.lua",
        options={"HIDDEN"},
        maxlen=511,
    )

    max_decimal_digits: IntProperty(
        name="Maximum Decimal Digits",
        description="Maximum amount of decimal digits in exported coordinates",
        default=3,
        min=0,
        soft_min=1,
    )

    multiplier: FloatProperty(
        name="Coordinate Scale Multiplier",
        description=
        "All coordinates are multiplied by this number. Set this to 32 for 1 unit to equal the width of the Alpha ship model in-game.",
        default=1.0,
        min=0.0,
        soft_min=0.1,
    )

    only_selected: BoolProperty(
        name="Only Export Selected Objects",
        description="Only export selected objects",
        default=False,
    )

    use_local: BoolProperty(
        name="Use Local Coordinates",
        description=
        "Use local coordinates instead of global coordinates when exporting",
        default=False,
    )

    exclude_seamed_edges: BoolProperty(
        name="Exclude Seams",
        description="Stop edges marked as seams from being exported",
        default=False,
    )

    export_color: BoolProperty(
        name="Export Color",
        description="Export vertex colors",
        default=False,
    )

    color_decompressor_location: StringProperty(
        name="Color Decompressor Location",
        description=
        "The location of decompresscolors.lua, including \"/dynamic/\" (without quotes)",
        default="/dynamic/utils/decompresscolors.lua",
    )

    def execute(self, context):
        out = []
        for object in context.scene.objects:
            if object.type == "MESH" and object.visible_get() and (
                (not self.only_selected) or
                (self.only_selected and object.select_get())):
                out.append(
                    serializeMesh(object, self.use_local, self.export_color,
                                  self.exclude_seamed_edges,
                                  self.max_decimal_digits, self.multiplier))

        if self.export_color:
            serialized = "meshes=require(\"" + self.color_decompressor_location + "\")(" + toLua(
                out, True) + ")"
        else:
            serialized = toLua(out, True, "meshes")
        f = open(self.filepath, 'w', encoding='utf-8')
        f.write(serialized)
        f.close()
        return {"FINISHED"}


def menu_func_export(self, context):
    self.layout.operator(ExportPPLMesh.bl_idname, text="PewPew Live (.lua)")


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
