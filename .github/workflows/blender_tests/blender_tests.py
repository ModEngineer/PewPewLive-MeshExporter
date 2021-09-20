import bpy, bmesh, mathutils, sys, os, json, traceback

sys.path.append(os.path.join(os.environ["GITHUB_WORKSPACE"], "tempmodulefolder"))

test_results = {"exitcode": 0, "tracebacks": []}

def save_test_results(results):
    with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test_results.json"), "wt", encoding="utf-8") as filehandle:
        json.dump(results, filehandle, ensure_ascii=False)
try:
    #Test add-on registration, exit if this fails
    try:
        if bpy.app.version > (2, 79, 0):
            bpy.ops.preferences.addon_enable(module="ppl_meshexport_addon")
        else:
            bpy.ops.wm.addon_enable(module="ppl_meshexport_addon")
            test_results["tracebacks"].append(None)
    except Exception:
        save_test_results({"exitcode": 0b11111, "tracebacks": [traceback.format_exc()]})
        sys.exit(0b11111)

    #Delete default objects
    for defaultobject in bpy.context.scene.objects:
        if bpy.app.version > (2, 79, 0):
            defaultobject.select_set(True)
        else:
            defaultobject.select = True
    bpy.ops.object.delete()

    #Add two different cubes
    if bpy.app.version >= (2, 90, 0):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(56, 241, 72), scale=(1, 1, 1))
    else:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.ops.mesh.primitive_cube_add(location=(5.25, 5.25, 5.25), rotation=(56, 241, 72))

    if bpy.context.scene.objects[0].location==mathutils.Vector((5.25, 5.25, 5.25)):
        currentobj = bpy.context.scene.objects[0]
    elif bpy.context.scene.objects[1].location==mathutils.Vector((5.25, 5.25, 5.25)):
        currentobj = bpy.context.scene.objects[1]
    if bpy.app.version > (2, 79, 0):
        currentobj.select_set(True)
        bpy.context.view_layer.objects.active = currentobj
    else:
        currentobj.select = True
        if bpy.app.version > (2, 79, 0):
            bpy.context.object = currentobj
        else:
            bpy.context.scene.object.active = currentobj
    bm = bmesh.new()
    bm.from_mesh(currentobj.data)
    seamVertexCoords = ([1, 1, 1], [-1, 1, 1], [-1, -1, 1])
    for edge in bm.edges:
        if [ round(coord) for coord in list(edge.verts[0].co) ] in seamVertexCoords and [ round(coord) for coord in list(edge.verts[1].co) ] in seamVertexCoords:
            edge.seam = True
    bm.to_mesh(currentobj.data)
    bpy.ops.object.mode_set(mode='EDIT')
    currentobj.data.vertex_colors.new()
    bm.free()

    #Test vertex color operator
    try:
        bpy.context.scene.pewpew_sceneproperties.editmode_vertex_color = (0.5, 0.5, 1.0, 1.0)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.set_vertex_colors()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for vert in currentobj.data.vertices:
            if [ round(coord) for coord in list(vert.co) ]==[1, -1, -1]:
                vert.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.scene.pewpew_sceneproperties.editmode_vertex_color = (1, 0.5, 0.5, 1.0)
        bpy.ops.mesh.set_vertex_colors()
        bpy.ops.mesh.select_all(action='DESELECT')
        test_results["tracebacks"].append(None)
    except Exception:
        test_results["exitcode"]+=0b10
        test_results["tracebacks"].append(traceback.format_exc())

    bpy.ops.object.mode_set(mode='OBJECT')

    #Test object export with local coordinates and only selection
    if bpy.app.version > (2, 79, 0):
        currentobj.select_set(True)
    else:
        currentobj.select = True
    try:
        bpy.ops.pewpew_live_meshexporter.exportmeshfromscene(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test.lua"), max_decimal_digits=3, multiplier=5, only_selected=True, use_local=True, exclude_seamed_edges=True, export_color=True, color_decompressor_location="decompresscolors")
        test_results["tracebacks"].append(None)
    except Exception:
        test_results["tracebacks"].append(traceback.format_exc())
        test_results["exitcode"]+=0b100
    
    #Test object export without local coordinates or only selection
    try:
        bpy.ops.pewpew_live_meshexporter.exportmeshfromscene(filepath=os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests",  "test2.lua"), max_decimal_digits=3, multiplier=5, only_selected=False, use_local=False, exclude_seamed_edges=True, export_color=True, color_decompressor_location="decompresscolors")
        test_results["tracebacks"].append(None)
    except Exception:
        test_results["tracebacks"].append(traceback.format_exc())
        test_results["exitcode"]+=0b1000

    #Test add-on unregistration
    try:
        if bpy.app.version > (2, 79, 0):
            bpy.ops.preferences.addon_disable(module="ppl_meshexport_addon")
        else:
            bpy.ops.wm.addon_disable(module="ppl_meshexport_addon")
        test_results["tracebacks"].append(None)
    except Exception:
        test_results["tracebacks"].append(traceback.format_exc())
        test_results["exitcode"]+=0b10000
    #Conclude the test
    save_test_results(test_results)
    sys.exit(int(test_results["exitcode"]))
except Exception:
    save_test_results({"exitcode": 0b111111, "tracebacks": [traceback.format_exc()]})
    print("Test failed completely.")
    sys.exit(0b111111)
