import bpy
import bpy_extras
import bmesh
import mathutils
import json
import math
from copy import copy

def dijkstra(bm, start, end, ignored_edge = None): # Translated and modified from https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Pseudocode
    queue = copy(list(bm.verts))

    dist = {start: 0}
    prev = {}

    while queue:
        u = min(queue, key=lambda x: dist.get(x, math.inf))
        if u==end:
            path = []
            u = end
            if u in prev.keys() or u == start:
                while u:
                    path.append(u)
                    u = prev.get(u)
            return path
        queue.remove(u)

        for edge in u.link_edges:
            if edge == ignored_edge:
                continue
            v = edge.other_vert(u)
            alt = dist[u] + 1
            if alt < dist.get(v, math.inf):
                dist[v] = alt
                prev[v] = u

class ImportPPLMeshFromJSON(bpy.types.Operator,
                            bpy_extras.io_utils.ImportHelper):
    """Import a JSON dump of a PewPew Live mesh file"""
    bl_idname = "pewpew_live_meshexporter.importmeshfromjson"
    bl_label = "PewPew Live (.json)"

    filename_ext = ".json"

    def execute(self, context):
        f = open(self.filepath, 'r')
        meshes = json.load(f)
        f.close()
        for mesh in meshes:
            obj_data = bpy.data.meshes.new("pewpew-import")
            obj = bpy.data.objects.new("pewpew-import", obj_data)
            bm = bmesh.new()
            bm.from_mesh(obj_data)
            has_color = "colors" in mesh.keys()
            for i, coords in enumerate(mesh["vertexes"]):
                if len(coords)==2:
                    coords.append(0)
                vert = bm.verts.new(mathutils.Vector(coords))
                vert.index = i
            bm.verts.ensure_lookup_table()
            deform_layer = bm.verts.layers.deform.verify()
            for segment in mesh["segments"]:
                for i in range(len(segment)-1):
                    bm.edges.new((bm.verts[segment[i]], bm.verts[segment[i+1]]))
                if len(segment) > 2:
                    obj.pewpew.segments.add()
                    obj.pewpew.segments[-1].segment_name = "Segment"
                    obj.pewpew.segments[-1].is_eulerian = True
                    for i in range(len(segment)-1):
                        group = obj.vertex_groups.new(name=obj.pewpew.segments[-1].vgroup_base_name)
                        bm.verts[segment[i]][deform_layer][group.index] = 1.0
                        bm.verts[segment[i+1]][deform_layer][group.index] = 1.0
            bm.edges.index_update()
            bm.edges.ensure_lookup_table()
            for edge in bm.edges:
                if edge.link_faces:
                    continue
                path = dijkstra(bm, edge.verts[0], edge.verts[1], edge)
                if path:
                    bm.faces.new(path)
                else:
                    new_vert = bm.verts.new(((edge.verts[0].co + edge.verts[1].co) / 2) + mathutils.Vector((0, 0, 0.1)))
                    bm.faces.new((edge.verts[0], edge.verts[1], new_vert))
                    new_vert.link_edges[0].seam = True
                    new_vert.link_edges[1].seam = True
            if has_color:
                colorloop = bm.loops.layers.color.verify()
                for index, color in enumerate(mesh["colors"]):
                    for loop in bm.verts[index].link_loops:
                        loop[colorloop] = (((color & 0xff000000) >> 24) / 255,
                                           ((color & 0xff0000) >> 16) / 255,
                                           ((color & 0xff00) >> 8) / 255,
                                           (color & 0xff) / 255)
            bm.to_mesh(obj_data)
            bm.free()
            if bpy.app.version > (2, 79, 0):
                context.collection.objects.link(obj)
            else:
                context.scene.objects.link(obj)
        return {"FINISHED"}

def menu_func_import(self, context):
    self.layout.operator(ImportPPLMeshFromJSON.bl_idname,
                         text="PewPew Live (.json)")


def register():
    if bpy.app.version > (2, 79, 0):
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    else:
        bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    if bpy.app.version > (2, 79, 0):
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    else:
        bpy.types.INFO_MT_file_import.remove(menu_func_import)