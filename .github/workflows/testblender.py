import bpy, os, bmesh

try:
    if bpy.app.version > (2, 79, 0):
        bpy.ops.preferences.addon_install(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexporter_addon.zip"))
        for object in bpy.context.scene.objects:
            object.select_set(True)
        bpy.ops.object.delete()
    else:
        bpy.ops.wm.addon_install(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexporter_addon.zip"))
        for object in bpy.context.scene.objects:
            object.select = True
        bpy.ops.object.delete()
    if bpy.app.version >= (2, 90, 0):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(0, 0, 0), scale=(1, 1, 1))
    else:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(0, 0, 0))
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
    bpy.context.window_manager.pewpew_temporaryproperties.editmode_vertex_color = (0.5, 0.5, 1.0, 0.0)
    currentobj.data.vertex_colors.new()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.set_vertex_colors()
    bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.app.version > (2, 79, 0):
        currentobj.select_set(True)
    else:
        currentobj.select = True
    bpy.ops.pewpewlive_meshexporter.exportmeshfromscene(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], "test.lua"), max_decimal_digits=3, multiplier=5, only_selected=True, use_local=True, exclude_seamed_edges=True, export_color=True)
except:
    import sys, traceback
    traceback.print_exc()
    sys.exit(1)
