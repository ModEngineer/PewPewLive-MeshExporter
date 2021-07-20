import bpy

#Update functions:
from ..newgui.vertexcolorimprovement import updateVertexColors


class PewPewTemporaryProperties(bpy.types.PropertyGroup):
    #newgui properties:
    editmode_vertex_color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        min=0,
        max=1,
        step=1,
        precision=6,
        size=4,
        update=updateVertexColors,
        default=(1.0, 1.0, 1.0, 1.0))


class PewPewMeshExporterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.partition(".")[0]

    editmode_vertex_color_auto_update: bpy.props.BoolProperty(
        name="Auto-update vertex colors", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "editmode_vertex_color_auto_update")


def register():
    bpy.types.WindowManager.pewpew_temporaryproperties = bpy.props.PointerProperty(
        type=PewPewTemporaryProperties)


def unregister():
    del bpy.types.WindowManager.pewpew_temporaryproperties
