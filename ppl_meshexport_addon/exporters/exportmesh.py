import bpy
import bpy_extras
from bpy.props import BoolProperty
import bmesh
from copy import deepcopy
from ..utils.common import cleanRound, clamp
from ..lua.luadataexport import toLua, stringKey
from ..utils.datatypes import hexint


def serializeMesh(object, use_local, export_color):
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
    for vertex in bm.verts:
        out[stringKey("vertexes")].append(
            [cleanRound(vertex.co[0],
                        4), cleanRound(vertex.co[1],
                                       4)])
        z = cleanRound(vertex.co[2], 4)
        if z!=0:
            out[stringKey("vertexes")][-1].append(z)
        if export_color and bm.loops.layers.color.active:
            #Face vertices are ignored. I don't have the time to support multiple colors per vertex.
            vertexcolor = vertex.link_loops[0][bm.loops.layers.color.active]
            colorhex = hexint(
                (clamp(round(vertexcolor[0] * 255), 0, 255) << 24) +
                (clamp(round(vertexcolor[1] * 255), 0, 255) << 16) +
                (clamp(round(vertexcolor[2] * 255), 0, 255) << 8) +
                clamp(round(vertexcolor[3] * 255), 0, 255))
            if colorhex in out[stringKey("colors")].keys():
                out[stringKey("colors")][colorhex].append(vertex.index + 1)
            else:
                out[stringKey("colors")][colorhex] = [vertex.index + 1]
    for edge in mesh.edges:
        out[stringKey("segments")].append(
            [edge.vertices[0], edge.vertices[1]])
    # Color compressor
    if export_color and bm.loops.layers.color.active:
        for color in out[stringKey("colors")]:
            colorIndices = deepcopy(out[stringKey("colors")][color])
            colorIndices.sort()
            out[stringKey("colors")][color] = []
            partialRange = False
            for index, color_index in enumerate(colorIndices):
                if index + 1 < len(colorIndices):
                    if colorIndices[index + 1] == colorIndices[index] + 1:
                        if partialRange:
                            out[stringKey("colors")][color][-1][1] = colorIndices[
                                index + 1]
                        else:
                            out[stringKey("colors")][color].append(
                                [colorIndices[index], colorIndices[index + 1]])
                            partialRange = True
                    else:
                        partialRange = False
                        out[stringKey("colors")][color].append(colorIndices[index])
                elif partialRange == True:
                    pass
                else:
                    out[stringKey("colors")][color].append(colorIndices[index])
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

    export_color: BoolProperty(
        name="Export Color",
        description="Export vertex colors",
        default=False,
    )

    def execute(self, context):
        out = []
        for object in context.scene.objects:
            if object.type == "MESH" and object.visible_get() and (
                (not self.only_selected) or
                (self.only_selected and object.select_get())):
                out.append(
                    serializeMesh(object, self.use_local,
                                  self.export_color))
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