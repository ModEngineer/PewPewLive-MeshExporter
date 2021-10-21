import bpy
import bmesh


def updateVertexColors(self, context):
    if context.preferences.addons[__package__.partition(
            ".")[0]].preferences.editmode_vertex_color_auto_update:
        bpy.ops.mesh.set_vertex_colors()
    return


class VertexColorOperator(bpy.types.Operator):
    bl_idname = "mesh.set_vertex_colors"
    bl_label = "Set Vertex Colors"

    def execute(self, context):

        bm = bmesh.from_edit_mesh(context.object.data)
        vertices = bm.verts
        colorloop = bm.loops.layers.color.verify()
        for vertex in vertices:
            if vertex.select and not vertex.hide:
                for loops in vertex.link_loops:
                    loops[
                        colorloop] = context.scene.pewpew.editmode_vertex_color
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        return {"FINISHED"}


class DATA_PT_vertex_color_improvement(bpy.types.Panel):
    bl_parent_id = "DATA_PT_vertex_colors"
    bl_label = "Current Vertices"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == "MESH"
                and context.object.mode == "EDIT")

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.pewpew,
                    "editmode_vertex_color",
                    text="Vertex colors")
        layout.prop(context.preferences.addons[__package__.partition(".")
                                               [0]].preferences,
                    "editmode_vertex_color_auto_update",
                    text="Auto-update vertex colors")
        layout.operator("mesh.set_vertex_colors", text="Update vertex colors")
