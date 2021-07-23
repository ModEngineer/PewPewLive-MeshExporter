import bpy, bmesh, addon_utils, os, importlib.util

try:
    spec = importlib.util.spec_from_file_location("ppl_meshexport_addon", os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon", "__init__.py"))
    ppl_meshexport_addon = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ppl_meshexport_addon)
    ppl_meshexport_addon.register()
    if bpy.app.version > (2, 79, 0):
        for object in bpy.context.scene.objects:
            object.select_set(True)
        bpy.ops.object.delete()
    else:
        for object in bpy.context.scene.objects:
            object.select = True
        bpy.ops.object.delete()
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
    bpy.context.scene.pewpew_sceneproperties.editmode_vertex_color = (0.5, 0.5, 1.0, 0.0)
    currentobj.data.vertex_colors.new()
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
