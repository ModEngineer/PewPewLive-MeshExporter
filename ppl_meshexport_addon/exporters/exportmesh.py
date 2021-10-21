import re, bpy, bpy_extras, bmesh, itertools
from bpy.props import BoolProperty, IntProperty, FloatProperty, StringProperty
from copy import deepcopy
from ..utils.common import cleanRound, clamp
from ..lua.luadataexport import toLua, stringKey
from ..utils.datatypes import hexint
from ..modules import pygraphutils


def correctIndex(exclusions, index):
    assert index not in exclusions, "Index to be corrected is in the exclusion list"
    return index - sum(
        1 for excludedIndex in exclusions if excludedIndex < index)


def serializeMesh(obj, use_local, export_color, exclude_seamed_edges,
                  max_decimal_digits, multiplier, use_segments):
    # Vertex Processing and init
    out = {}
    out[stringKey("vertexes")] = []
    out[stringKey("segments")] = []
    if bpy.app.version > (2, 79, 0):
        mesh = obj.to_mesh()
    else:
        mesh = obj.to_mesh(bpy.context.scene, False, "PREVIEW")
    if not use_local:
        mesh.transform(obj.matrix_world)
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
            colorhex = None
            if bpy.app.version > (2, 79, 0):
                colorhex = hexint(
                    (clamp(round(vertexcolor[0] * 255), 0, 255) << 24) +
                    (clamp(round(vertexcolor[1] * 255), 0, 255) << 16) +
                    (clamp(round(vertexcolor[2] * 255), 0, 255) << 8) +
                    clamp(round(vertexcolor[3] * 255), 0, 255))
            else:
                colorhex = hexint(
                    (clamp(round(vertexcolor[0] * 255), 0, 255) << 24) +
                    (clamp(round(vertexcolor[1] * 255), 0, 255) << 16) +
                    (clamp(round(vertexcolor[2] * 255), 0, 255) << 8) + 0xff)
            out[stringKey("colors")][
                str(colorhex)] = out[stringKey("colors")].get(
                    str(colorhex),
                    []) + [correctIndex(excludedVertexIndices, vertex.index)]
    # Multi-edge segment processor
    remainingEdges = set(bm.edges)
    if obj.pewpew.segments and use_segments:
        deformLayer = bm.verts.layers.deform.verify()
        for segment in obj.pewpew.segments:
            if segment.is_eulerian:
                currentSegmentGraph = {}
                segmentVGroupIndices = [
                    group.index for group in obj.vertex_groups
                    if segment.vgroup_base_name in group.name
                ]
                for edge in bm.edges:
                    assert not (
                        exclude_seamed_edges and edge.seam
                    ), "An edge in a segment must not be marked as a seam if excluding seams."
                    if any(vGroupIndex in dict(edge.verts[0][deformLayer]).keys()
                           for vGroupIndex in dict(edge.verts[1][deformLayer]).keys()
                           if vGroupIndex in segmentVGroupIndices):
                        remainingEdges.remove(edge)
                        pygraphutils.add_edge(
                            correctIndex(excludedVertexIndices,
                                         edge.verts[0].index),
                            correctIndex(excludedVertexIndices,
                                         edge.verts[1].index),
                            currentSegmentGraph)
                pygraphutils.validate_graph(
                    currentSegmentGraph).raise_exception()
                fleuryResult = pygraphutils.fleury(currentSegmentGraph)
                if fleuryResult:
                    out[stringKey("segments")].append(fleuryResult)
    # Single-edge segment processor
    for edge in remainingEdges:
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
                    elif partialRange:
                        partialRange = False
                    else:
                        out[stringKey("colors")][color].append(color_index)
                elif partialRange == True:
                    pass
                else:
                    out[stringKey("colors")][color].append(color_index)
    bm.free()
    return out


class ExportPPLMesh(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a PewPew Live mesh from scene. Only visible objects can be exported."""
    bl_idname = "pewpew_live_meshexporter.exportmeshfromscene"
    bl_label = "PewPew Live (.lua)"

    filename_ext = ".lua"

    filter_glob = StringProperty(
        default="*.lua",
        options={"HIDDEN"},
        maxlen=511,
    )

    max_decimal_digits = IntProperty(
        name="Maximum Decimal Digits",
        description="Maximum amount of decimal digits in exported coordinates",
        default=3,
        min=0,
        soft_min=1,
    )

    multiplier = FloatProperty(
        name="Coordinate Scale Multiplier",
        description=
        "All coordinates are multiplied by this number. Set this to 32 for 1 unit to equal the width of the Alpha ship model in-game.",
        default=1.0,
        min=0.0,
        soft_min=0.1,
    )

    only_selected = BoolProperty(
        name="Only Export Selected Objects",
        description="Only export selected objects",
        default=False,
    )

    use_local = BoolProperty(
        name="Use Local Coordinates",
        description=
        "Use local coordinates instead of global coordinates when exporting",
        default=False,
    )

    exclude_seamed_edges = BoolProperty(
        name="Exclude Seams",
        description="Stop edges marked as seams from being exported",
        default=False,
    )

    export_color = BoolProperty(
        name="Export Color",
        description="Export vertex colors",
        default=False,
    )

    color_decompressor_location = StringProperty(
        name="Color Decompressor Location",
        description=
        "The location of decompresscolors.lua, including \"/dynamic/\" (without quotes)",
        default="/dynamic/utils/decompresscolors.lua",
    )

    use_segments = BoolProperty(
        name="Use Segments",
        description=
        "Instead of exporting each edge as its own segment, use user-specified segments",
        default=True)

    use_fixedpoint = BoolProperty(
        name="Use FixedPoint",
        description="Use FixedPoint instead of floating point numbers",
        default=False)

    def execute(self, context):
        def object_is_visible(obj):
            if bpy.app.version > (2, 79, 0):
                return obj.visible_get()
            else:
                return obj.is_visible(bpy.context.scene)

        def object_is_selected(obj):
            if bpy.app.version > (2, 79, 0):
                return obj.select_get()
            else:
                return obj.select

        out = []
        for obj in context.scene.objects:
            if obj.type == "MESH" and object_is_visible(obj) and (
                (not self.only_selected) or
                (self.only_selected and object_is_selected(obj))):
                out.append(
                    serializeMesh(obj, self.use_local, self.export_color,
                                  self.exclude_seamed_edges,
                                  self.max_decimal_digits, self.multiplier,
                                  self.use_segments))

        if self.export_color:
            serialized = "meshes=require(\"" + self.color_decompressor_location + "\")(" + toLua(
                out, not self.use_fixedpoint) + ")"
        else:
            serialized = toLua(out, True, "meshes")
        f = open(self.filepath, 'w', encoding='utf-8')
        f.write(serialized)
        f.close()
        return {"FINISHED"}


def menu_func_export(self, context):
    self.layout.operator(ExportPPLMesh.bl_idname, text="PewPew Live (.lua)")


def register():
    if bpy.app.version > (2, 79, 0):
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    else:
        bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    if bpy.app.version > (2, 79, 0):
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    else:
        bpy.types.INFO_MT_file_export.remove(menu_func_export)