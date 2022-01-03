import bpy, bmesh, itertools, mathutils
from ..modules import pygraphutils
from ..exporters.exportmesh import correctIndex
from math import pi, sqrt
from collections import OrderedDict


@bpy.app.handlers.persistent
def update_dual_meshes(scene):
    if scene.pewpew.is_updating_dual_meshes:
        scene.pewpew.is_updating_dual_meshes = False
        return
    scene.pewpew.is_updating_dual_meshes = True

    def create_circle(initialvec, axisvec, steps):
        rotationmatrix = mathutils.Matrix.Rotation((2 * pi) / steps, 3,
                                                   axisvec)
        for x in range(steps):
            yield initialvec.copy()
            initialvec.rotate(rotationmatrix)

    def distance(vec1, vec2):
        diff = vec2 - vec1
        return sqrt(sum(diff * diff))

    def object_is_visible(obj, context):
        if bpy.app.version > (2, 79, 0):
            return obj.visible_get()
        else:
            return obj.is_visible(context.scene)

    for obj in scene.objects:
        if not (object_is_visible(obj, bpy.context)
                and obj.pewpew.dual_mesh.is_dual_mesh):
            continue
        source = obj.pewpew.dual_mesh.source
        newbm = bmesh.new()
        if bpy.app.version > (2, 79, 0):
            if obj.pewpew.dual_mesh.apply_modifiers:
                mesh = source.evaluated_get(
                    bpy.context.evaluated_depsgraph_get()).to_mesh()
            else:
                mesh = source.to_mesh()
        else:
            mesh = source.to_mesh(bpy.context.scene,
                                  obj.pewpew.dual_mesh.apply_modifiers,
                                  "RENDER")
        mesh.transform(source.matrix_world)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        includedVertices = sorted(list(
            set(
                itertools.chain.from_iterable([
                    list(edge.verts) for edge in bm.edges
                    if not (obj.pewpew.dual_mesh.exclude_seamed_edges
                            and edge.seam)
                ]))),
                                  key=lambda v: v.index)
        excludedVertexIndices = [
            vertex.index for vertex in bm.verts
            if vertex not in includedVertices
        ]
        if obj.pewpew.dual_mesh.use_color and bm.loops.layers.color.active:
            colorloop = newbm.loops.layers.color.verify()
        if obj.pewpew.dual_mesh.shade_smooth == "WITHSHARPMITERS":
            miteredgelist = []
            capfacelist = []
        remainingEdges = set(bm.edges)
        if source.pewpew.segments and obj.pewpew.dual_mesh.use_segments:
            deformLayer = bm.verts.layers.deform.verify()
            for segment in source.pewpew.segments:
                if segment.is_eulerian:
                    currentSegmentGraph = {}
                    segmentVGroupIndices = [
                        group.index for group in source.vertex_groups
                        if segment.vgroup_base_name in group.name
                    ]
                    for edge in bm.edges:
                        if any(vGroupIndex in dict(edge.verts[0]
                                                   [deformLayer]).keys()
                               for vGroupIndex in dict(edge.verts[1]
                                                       [deformLayer]).keys()
                               if vGroupIndex in segmentVGroupIndices):
                            assert not (
                                obj.pewpew.dual_mesh.exclude_seamed_edges
                                and edge.seam
                            ), "An edge in a segment must not be marked as a seam if excluding seams."
                            remainingEdges.remove(edge)
                            pygraphutils.add_edge(
                                correctIndex(excludedVertexIndices,
                                             edge.verts[0].index),
                                correctIndex(excludedVertexIndices,
                                             edge.verts[1].index),
                                currentSegmentGraph)
                    pygraphutils.validate_graph(
                        currentSegmentGraph).raise_exception()
                    fleuryResult = pygraphutils.fleury(currentSegmentGraph)
                    islooped = fleuryResult[0] == fleuryResult[-1]
                    if islooped:
                        fleuryResult.append(fleuryResult[1])
                    pointlistlist = []
                    if obj.pewpew.dual_mesh.use_color and bm.loops.layers.color.active:
                        colorlist = []
                    for index in range(len(fleuryResult) - 2):
                        pointlist = []
                        c1vec = bm.verts[fleuryResult[
                            index + 1]].co - bm.verts[fleuryResult[index]].co
                        c2vec = bm.verts[fleuryResult[
                            index + 1]].co - bm.verts[fleuryResult[index +
                                                                   2]].co
                        if obj.pewpew.dual_mesh.use_color and bm.loops.layers.color.active:
                            colorlist.append(
                                bm.verts[fleuryResult[index + 1]].link_loops[0]
                                [bm.loops.layers.color.active])
                        pvec1 = c1vec.normalized() + c2vec.normalized()
                        pvec2 = c1vec.cross(c2vec)
                        planenormal = pvec1.cross(pvec2)
                        if pvec2 == mathutils.Vector((0, 0, 0)):
                            pvec2 = c1vec.orthogonal()
                        if planenormal == mathutils.Vector((0, 0, 0)):
                            planenormal = c1vec

                        orthovec = pvec2.normalized(
                        ) * obj.pewpew.dual_mesh.cylinder_radius

                        planenormaltimesplanepoint = sum(
                            planenormal * bm.verts[fleuryResult[index + 1]].co)
                        tmultiplier = sum(planenormal * c1vec)

                        for point in create_circle(
                                orthovec.copy(), c1vec,
                                obj.pewpew.dual_mesh.cylinder_resolution):
                            point += bm.verts[fleuryResult[index + 1]].co
                            planenormaltimeslinepoint = sum(planenormal *
                                                            point)
                            t = (planenormaltimesplanepoint -
                                 planenormaltimeslinepoint) / tmultiplier
                            pointlist.append(point + t * c1vec)
                        pointlistlist.append(pointlist)
                    if not islooped:
                        startCylinderVec = bm.verts[
                            fleuryResult[0]].co - bm.verts[fleuryResult[1]].co
                        pointlistlist.insert(0, [
                            vec + bm.verts[fleuryResult[0]].co
                            for vec in create_circle(
                                startCylinderVec.orthogonal().normalized() *
                                obj.pewpew.dual_mesh.cylinder_radius,
                                startCylinderVec,
                                obj.pewpew.dual_mesh.cylinder_resolution)
                        ])
                        endCylinderVec = bm.verts[fleuryResult[
                            -1]].co - bm.verts[fleuryResult[-2]].co
                        pointlistlist.append([
                            vec + bm.verts[fleuryResult[-1]].co
                            for vec in create_circle(
                                endCylinderVec.orthogonal().normalized() *
                                obj.pewpew.dual_mesh.cylinder_radius,
                                endCylinderVec,
                                obj.pewpew.dual_mesh.cylinder_resolution)
                        ])
                        if obj.pewpew.dual_mesh.use_color and bm.loops.layers.color.active:
                            colorlist.insert(
                                0, bm.verts[fleuryResult[0]].link_loops[0][
                                    bm.loops.layers.color.active])
                            colorlist.append(
                                bm.verts[fleuryResult[-1]].link_loops[0][
                                    bm.loops.layers.color.active])
                    vertlistlist = []
                    for pointlist in pointlistlist:
                        vertlist = []
                        for point in pointlist:
                            vertlist.append(newbm.verts.new(point))
                        vertlistlist.append(vertlist)

                    edgelistlist = []
                    for vertlist in vertlistlist:
                        edgelist = []
                        for index in range(-1, len(vertlist) - 1):
                            edgelist.append(
                                newbm.edges.new(
                                    (vertlist[index], vertlist[index + 1])))
                        edgelistlist.append(edgelist)

                    if obj.pewpew.dual_mesh.shade_smooth == "WITHSHARPMITERS":
                        miteredgelist += list(
                            itertools.chain.from_iterable(edgelistlist))

                    if not islooped:
                        if obj.pewpew.dual_mesh.shade_smooth == "WITHSHARPMITERS":
                            capfacelist.append(newbm.faces.new(
                                vertlistlist[0]))
                            capfacelist.append(
                                newbm.faces.new(vertlistlist[-1]))
                        else:
                            newbm.faces.new(vertlistlist[0])
                            newbm.faces.new(vertlistlist[-1])

                    for index in range(-int(islooped), len(edgelistlist) - 1):
                        bmesh.ops.bridge_loops(newbm,
                                               edges=edgelistlist[index] +
                                               edgelistlist[index + 1])
                    if obj.pewpew.dual_mesh.use_color and bm.loops.layers.color.active:
                        for vertlist, color in zip(vertlistlist, colorlist):
                            print(color)
                            for vert in vertlist:
                                for loops in vert.link_loops:
                                    loops[colorloop] = color
        for edge in remainingEdges:
            if not (obj.pewpew.dual_mesh.exclude_seamed_edges and edge.seam):
                d1vec = edge.verts[0].co - edge.verts[1].co
                d2vec = edge.verts[1].co - edge.verts[0].co

                c1verts = []
                for point in create_circle(
                        d1vec.orthogonal().normalized() *
                        obj.pewpew.dual_mesh.cylinder_radius, d1vec,
                        obj.pewpew.dual_mesh.cylinder_resolution):
                    c1verts.append(newbm.verts.new(point + edge.verts[0].co))
                c2verts = []
                for point in create_circle(
                        d2vec.orthogonal().normalized() *
                        obj.pewpew.dual_mesh.cylinder_radius, d2vec,
                        obj.pewpew.dual_mesh.cylinder_resolution):
                    c2verts.append(newbm.verts.new(point + edge.verts[1].co))

                edgelist = []
                for index in range(-1, len(c1verts) - 1):
                    edgelist.append(
                        newbm.edges.new((c1verts[index], c1verts[index + 1])))

                for index in range(-1, len(c2verts) - 1):
                    edgelist.append(
                        newbm.edges.new((c2verts[index], c2verts[index + 1])))

                if obj.pewpew.dual_mesh.shade_smooth == "WITHSHARPMITERS":
                    miteredgelist += edgelist
                    capfacelist.append(newbm.faces.new(c1verts))
                    capfacelist.append(newbm.faces.new(c2verts))
                else:
                    newbm.faces.new(c1verts)
                    newbm.faces.new(c2verts)

                bmesh.ops.bridge_loops(newbm, edges=edgelist)

                if obj.pewpew.dual_mesh.use_color and bm.loops.layers.color.active:
                    for vert in c1verts:
                        for loops in vert.link_loops:
                            loops[colorloop] = edge.verts[0].link_loops[0][
                                bm.loops.layers.color.active]
                    for vert in c2verts:
                        for loops in vert.link_loops:
                            loops[colorloop] = edge.verts[1].link_loops[0][
                                bm.loops.layers.color.active]

        if obj.pewpew.dual_mesh.shade_smooth != "OFF":
            for face in newbm.faces:
                if obj.pewpew.dual_mesh.shade_smooth == "WITHSHARPMITERS" and face in capfacelist:
                    continue
                face.smooth = True
            for edge in newbm.edges:
                if obj.pewpew.dual_mesh.shade_smooth == "WITHSHARPMITERS" and edge in miteredgelist:
                    continue
                edge.smooth = True

        newbm.to_mesh(obj.data)
        bm.free()
        newbm.free()


class CreateWireframeOperator(bpy.types.Operator):
    """Creates a new PewPew-style wireframe object for the selected object"""
    bl_idname = "mesh.create_pewpew_wireframe"
    bl_label = "Create PewPew Wireframe"

    use_color = bpy.props.BoolProperty(default=True, name="Use Color")
    exclude_seamed_edges = bpy.props.BoolProperty(default=False,
                                                  name="Exclude Seamed Edges")
    use_segments = bpy.props.BoolProperty(default=True, name="Use Segments")
    apply_modifiers = bpy.props.BoolProperty(default=False,
                                             name="Apply Modifiers")
    cylinder_resolution = bpy.props.IntProperty(min=3,
                                                default=16,
                                                name="Cylinder Resolution")
    cylinder_radius = bpy.props.FloatProperty(default=1.0,
                                              name="Cylinder Radius")
    shade_smooth = bpy.props.EnumProperty(items=[
        ("OFF", "Off", "", 1),
        ("WITHSHARPMITERS", "With sharp miters (recommended)", "", 2),
        ("FULL", "Fully shade smooth", "", 3)
    ],
                                          default="WITHSHARPMITERS",
                                          name="Shade Smooth")

    def execute(self, context):
        me = bpy.data.meshes.new(context.object.name + "-pewpew-wireframe")
        ob = bpy.data.objects.new(context.object.name + "-pewpew-wireframe",
                                  me)

        context.object.pewpew.dual_mesh.has_target = True
        ob.pewpew.dual_mesh.is_dual_mesh = True
        ob.pewpew.dual_mesh.source = context.object

        ob.pewpew.dual_mesh.use_color = self.use_color
        ob.pewpew.dual_mesh.exclude_seamed_edges = self.exclude_seamed_edges
        ob.pewpew.dual_mesh.use_segments = self.use_segments
        ob.pewpew.dual_mesh.apply_modifiers = self.apply_modifiers
        ob.pewpew.dual_mesh.cylinder_resolution = self.cylinder_resolution
        ob.pewpew.dual_mesh.cylinder_radius = self.cylinder_radius
        ob.pewpew.dual_mesh.shade_smooth = self.shade_smooth

        if bpy.app.version > (2, 79, 0):
            bpy.context.collection.objects.link(ob)
        else:
            bpy.context.scene.objects.link(ob)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class ApplyWireframeOperator(bpy.types.Operator):
    """Applies the PewPew wireframe to the dual-mesh"""
    bl_idname = "mesh.apply_pewpew_wireframe"
    bl_label = "Apply PewPew Wireframe"

    @classmethod
    def poll(cls, context):
        return context.object.pewpew.dual_mesh.is_dual_mesh

    def execute(self, context):
        context.object.pewpew.dual_mesh.is_dual_mesh = False
        return {"FINISHED"}


class DATA_PT_pewpew_wireframe(bpy.types.Panel):
    bl_label = "PewPew Wireframe"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        if context.object.pewpew.dual_mesh.is_dual_mesh:
            layout.prop(context.object.pewpew.dual_mesh,
                        "source",
                        text="Source Mesh")
            layout.prop(context.object.pewpew.dual_mesh,
                        "use_color",
                        text="Use Color")
            layout.prop(context.object.pewpew.dual_mesh,
                        "exclude_seamed_edges",
                        text="Exclude Seamed Edges")
            layout.prop(context.object.pewpew.dual_mesh,
                        "use_segments",
                        text="Use Segments")
            layout.prop(context.object.pewpew.dual_mesh,
                        "apply_modifiers",
                        text="Apply Modifiers")
            layout.prop(context.object.pewpew.dual_mesh,
                        "cylinder_resolution",
                        text="Cylinder Resolution")
            layout.prop(context.object.pewpew.dual_mesh,
                        "cylinder_radius",
                        text="Cylinder Radius")
            layout.prop(context.object.pewpew.dual_mesh,
                        "shade_smooth",
                        text="Shade Smooth")
            layout.operator("mesh.apply_pewpew_wireframe",
                            text="Apply PewPew Wireframe")
        else:
            layout.operator("mesh.create_pewpew_wireframe")


def register():
    bpy.app.handlers.depsgraph_update_pre.append(update_dual_meshes)
    bpy.app.handlers.frame_change_pre.append(update_dual_meshes)


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(update_dual_meshes)
    bpy.app.handlers.frame_change_pre.remove(update_dual_meshes)
