import bpy, bmesh, addon_utils, os, sys
try: 
    class SetEditModeVertexColorOperator(bpy.types.Operator):
        bl_idname="mesh.set_editmode_vertex_color"
        bl_label="Set Edit Mode Vertex Color"

        color: bpy.props.FloatVectorProperty(
            name="Color",
            subtype="COLOR",
            min=0,
            max=1,
            step=1,
            precision=6,
            size=[3, 4][int(bpy.app.version>(2, 79, 0))],
            default=[(1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)][int(bpy.app.version>(2, 79, 0))])
        def execute(self, context):
            context.scene.pewpew_sceneproperties.editmode_vertex_color = self.color
            return {'FINISHED'}
        def invoke(self, context, colour):
            self.color = colour
            return self.execute(context)
    bpy.utils.register_class(SetEditModeVertexColorOperator)
    if bpy.app.version > (2, 79, 0):
        for object in bpy.context.scene.objects:
            object.select_set(True)
        bpy.ops.object.delete()
        for mod in addon_utils.modules():
            if mod.bl_info["name"]=="PewPew Live Mesh Exporter":
                for modname, mod2 in sys.modules.items():
                    if mod2==mod:
                        bpy.ops.preferences.addon_enable(module=modname)
    else:
        for object in bpy.context.scene.objects:
            object.select = True
        bpy.ops.object.delete()
        for mod in addon_utils.modules():
            if mod.bl_info["name"]=="PewPew Live Mesh Exporter":
                for modname, mod2 in sys.modules.items():
                    if mod2==mod:
                        bpy.ops.wm.addon_enable(module=modname)
    if bpy.app.version >= (2, 90, 0):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(56, 241, 72), scale=(1, 1, 1))
    else:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(56, 241, 72))
    currentobj = bpy.context.scene.objects[0]
    if bpy.app.version > (2, 79, 0):
        currentobj.select_set(True)
    else:
        currentobj.select = True
    bm = bmesh.new()
    bm.from_mesh(currentobj.data)
    for edge in bm.edges[:2]:
        edge.seam = True
    bm.to_mesh(currentobj.data)
    bpy.ops.object.mode_set(mode='EDIT')
    currentobj.data.vertex_colors.new()
    currentobj.data.vertex_colors.active = currentobj.data.vertex_colors[0]
    currentobj.data.vertex_colors.active_index = 0
    bpy.ops.mesh.set_editmode_vertex_color((0.5, 0.5, 1.0, 1.0))
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.set_vertex_colors()
    bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.app.version > (2, 79, 0):
        currentobj.select_set(True)
    else:
        currentobj.select = True
    bpy.ops.pewpewlive_meshexporter.exportmeshfromscene(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], "test.lua"), max_decimal_digits=3, multiplier=5, only_selected=True, use_local=True, exclude_seamed_edges=True, export_color=True)
    ppl_meshexport_addon.unregister()
except:
    import sys, traceback
    traceback.print_exc()
    sys.exit(1)
