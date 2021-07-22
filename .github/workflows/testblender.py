import bpy, random, os

try:
    if bpy.app.version > (2, 79, 0):
        bpy.ops.preferences.addon_install(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexporter_addon.zip"))
        bpy.ops.preferences.addon_enable(module="ppl_meshexporter_addon")
    else:
        bpy.ops.wm.addon_install(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexporter_addon.zip"))
        bpy.ops.wm.addon_enable(module="ppl_meshexporter_addon")
    if bpy.app.version >= (2, 90, 0):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(0, 0, 0), scale=(1, 1, 1))
    else:
        for x in range(10):
            bpy.ops.mesh.primitive_cube_add(location=cube_location[x], rotation=cube_rotation[x])
    
except:
    import sys, traceback
    traceback.print_exc()
    sys.exit(1)
