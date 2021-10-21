import bpy

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


class PewPewObjectProperties(bpy.types.PropertyGroup):
    segments = bpy.props.CollectionProperty(type=SegmentProperties)
    active_segment_index = bpy.props.IntProperty(min=0)


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


def unregister():
    del bpy.types.Scene.pewpew
    del bpy.types.Object.pewpew