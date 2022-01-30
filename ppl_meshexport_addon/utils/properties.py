import bpy, bmesh

#Update functions:
from ..newgui.vertexcolorimprovement import updateVertexColors
from ..newgui.segments import preventDuplicateSegmentName, vGroupBaseNameGetter
from ..modules import pygraphutils


class PewPewSceneProperties(bpy.types.PropertyGroup):
    #newgui properties:
    if bpy.app.version > (2, 79, 0):
        editmode_vertex_color = bpy.props.FloatVectorProperty(
            name="Color",
            subtype="COLOR",
            min=0,
            max=1,
            step=1,
            precision=6,
            size=4,
            update=updateVertexColors,
            default=(1.0, 1.0, 1.0, 1.0))
    else:
        editmode_vertex_color = bpy.props.FloatVectorProperty(
            name="Color",
            subtype="COLOR",
            min=0,
            max=1,
            step=1,
            precision=6,
            size=3,
            update=updateVertexColors,
            default=(1.0, 1.0, 1.0))
    is_updating_dual_meshes = bpy.props.BoolProperty(default=False)


class SegmentProperties(bpy.types.PropertyGroup):
    segment_name = bpy.props.StringProperty(update=preventDuplicateSegmentName)
    old_segment_name = bpy.props.StringProperty()
    vgroup_base_name = bpy.props.StringProperty(get=vGroupBaseNameGetter)
    is_eulerian = bpy.props.BoolProperty(default=False)

    def as_graph(self):

        graph = {}
        vGroupNameBase = self.vgroup_base_name
        for edge in self.id_data.data.edges:
            firstVertGroups = [
                groupElement.group for groupElement in
                self.id_data.data.vertices[edge.vertices[0]].groups
                if vGroupNameBase in self.id_data.vertex_groups[
                    groupElement.group].name
            ]
            secondVertGroups = [
                groupElement.group for groupElement in
                self.id_data.data.vertices[edge.vertices[1]].groups
                if vGroupNameBase in self.id_data.vertex_groups[
                    groupElement.group].name
            ]
            if any(group in secondVertGroups for group in firstVertGroups):
                pygraphutils.add_edge(edge.vertices[0], edge.vertices[1],
                                      graph)
        return graph


def mark_dual_mesh_settings_change(self, context):
    self.settings_changed = True


class DualMeshProperties(bpy.types.PropertyGroup):
    is_dual_mesh = bpy.props.BoolProperty(default=False)
    settings_changed = bpy.props.BoolProperty(default=True)
    source = bpy.props.PointerProperty(type=bpy.types.Object,
                                       update=mark_dual_mesh_settings_change)
    use_color = bpy.props.BoolProperty(default=True,
                                       update=mark_dual_mesh_settings_change)
    exclude_seamed_edges = bpy.props.BoolProperty(
        default=False, update=mark_dual_mesh_settings_change)
    use_segments = bpy.props.BoolProperty(
        default=True, update=mark_dual_mesh_settings_change)
    apply_modifiers = bpy.props.BoolProperty(
        default=False, update=mark_dual_mesh_settings_change)
    cylinder_resolution = bpy.props.IntProperty(
        min=3, default=16, update=mark_dual_mesh_settings_change)
    cylinder_radius = bpy.props.FloatProperty(
        default=1.0, update=mark_dual_mesh_settings_change)
    shade_smooth = bpy.props.EnumProperty(
        items=[("OFF", "Off", "", 1),
               ("WITHSHARPMITERS", "With sharp miters (recommended)", "", 2),
               ("FULL", "Fully shade smooth", "", 3)],
        default="WITHSHARPMITERS",
        update=mark_dual_mesh_settings_change)


class PewPewObjectProperties(bpy.types.PropertyGroup):
    segments = bpy.props.CollectionProperty(type=SegmentProperties)
    active_segment_index = bpy.props.IntProperty(min=0)
    dual_mesh = bpy.props.PointerProperty(type=DualMeshProperties)
    last_hash = bpy.props.StringProperty(default="")


def getMeshHash(self):
    bm = bmesh.new()
    bm.from_mesh(self.id_data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    if bm.loops.layers.color.active:
        return str(
            hash((frozenset(tuple(vert.co) for vert in bm.verts),
                  frozenset((frozenset((
                      (tuple(edge.verts[0].co),
                       tuple(edge.verts[0].co.link_loops[0][bm.loops.layers.
                                                            color.active])
                       if len(edge.verts[0].co.link_loops) > 0 else None),
                      (tuple(edge.verts[1].co),
                       tuple(edge.verts[1].co.link_loops[0][bm.loops.layers.
                                                            color.active])
                       if len(edge.verts[1].co.link_loops) > 0 else None))),
                             edge.seam) for edge in bm.edges))))
    else:
        return str(
            hash((
                frozenset(tuple(vert.co) for vert in bm.verts),
                frozenset((frozenset((tuple(edge.verts[0].co),
                                      tuple(edge.verts[1].co))), edge.seam)
                          for edge in bm.edges)
                #frozenset((segment.segment_name, ) for segment in )
            )))


class PewPewMeshProperties(bpy.types.PropertyGroup):
    hash = bpy.props.StringProperty(get=getMeshHash)


class PewPewMeshExporterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.partition(".")[0]

    editmode_vertex_color_auto_update = bpy.props.BoolProperty(
        name="Auto-update vertex colors", default=True)

    # hide_segment_vgroups = bpy.props.BoolProperty(
    #     name="Hide Segment Vertex Groups (POTENTIALLY UNSTABLE)",
    #     description=
    #     "Hide vertex groups associated with segments from the vertex group list. (potentially unstable if another add-on tries to override the same piece of code)",
    #     default=False, update=hideSegmentVGroupsUpdateCallback)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "editmode_vertex_color_auto_update")
        # layout.prop(self, "hide_segment_vgroups")


def register():
    bpy.types.Scene.pewpew = bpy.props.PointerProperty(
        type=PewPewSceneProperties)
    bpy.types.Object.pewpew = bpy.props.PointerProperty(
        type=PewPewObjectProperties)
    bpy.types.Mesh.pewpew = bpy.props.PointerProperty(
        type=PewPewMeshProperties)


def unregister():
    del bpy.types.Scene.pewpew
    del bpy.types.Object.pewpew
    del bpy.types.Mesh.pewpew
