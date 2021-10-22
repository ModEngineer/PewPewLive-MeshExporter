import bpy, re
from ..modules import pygraphutils


def preventDuplicateSegmentName(self, context):
    value = self.segment_name
    if value == self.old_segment_name:
        return
    if value.isspace() or value == "":
        value = "Segment"
    existingNames = [
        segment.old_segment_name for segment in self.id_data.pewpew.segments
    ]
    if value in existingNames:
        match = re.match(
            '(.*)\.(\d{3,})', value
        )  # Regex taken from https://blender.stackexchange.com/a/15971
        base = None
        if match:
            base, num = match.groups()
        else:
            base = value
            num = 1
        while (base + "." + str(num).zfill(3)) in existingNames:
            num += 1
        value = base + "." + str(num).zfill(3)
        self.segment_name = value
    for group in self.id_data.vertex_groups:
        group.name = group.name.replace(
            "pewpew_segment_" +
            self.old_segment_name.replace("\\", "\\\\").replace("_", "\\_") +
            "_vgroup", "pewpew_segment_" +
            value.replace("\\", "\\\\").replace("_", "\\_") + "_vgroup")
    self.old_segment_name = value


def vGroupBaseNameGetter(self):
    return "pewpew_segment_" + self.segment_name.replace("\\", "\\\\").replace(
        "_", "\\_") + "_vgroup"


class MESH_UL_segments(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if not item.is_eulerian:
            layout.alert = True
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item,
                        "segment_name",
                        text="",
                        emboss=False,
                        icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SegmentAddOperator(bpy.types.Operator):
    """Adds a new segment"""
    bl_idname = "mesh.segments_add"
    bl_label = "Add New Segment"

    def execute(self, context):
        context.object.pewpew.segments.add()
        context.object.pewpew.segments[-1].segment_name = "Segment"
        context.object.pewpew.active_segment_index = len(
            context.object.pewpew.segments) - 1
        return {"FINISHED"}


class SegmentDeleteOperator(bpy.types.Operator):
    """Deletes a segment"""
    bl_idname = "mesh.segments_delete"
    bl_label = "Delete Segment"

    remove_all = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return len(context.object.pewpew.segments) > 0

    def execute(self, context):
        if self.remove_all:
            vGroupNameBases = [
                segment.vgroup_base_name
                for segment in context.object.pewpew.segments
            ]
        else:
            vGroupNameBases = [
                context.object.pewpew.segments[
                    context.object.pewpew.active_segment_index].
                vgroup_base_name
            ]

        groupsToBeRemoved = [
            group for group in context.object.vertex_groups
            for vGroupNameBase in vGroupNameBases
            if vGroupNameBase in group.name
        ]
        for group in groupsToBeRemoved:
            context.object.vertex_groups.remove(group)

        if self.remove_all:
            context.object.pewpew.segments.clear()
            context.object.pewpew.active_segment_index = 0
        else:
            context.object.pewpew.segments.remove(
                context.object.pewpew.active_segment_index)
            context.object.pewpew.active_segment_index -= 1

        return {"FINISHED"}


class SegmentSortOperator(bpy.types.Operator):
    """Sorts segments by name"""
    bl_idname = "mesh.segments_sort"
    bl_label = "Sort Segments Alphabetically"

    @classmethod
    def poll(cls, context):
        return len(context.object.pewpew.segments) > 0

    def execute(self, context):
        segmentNames = [
            segment.segment_name for segment in context.object.pewpew.segments
        ]

        sortedSegmentNames = sorted(segmentNames)

        activeSegmentName = segmentNames[
            context.object.pewpew.active_segment_index]

        for index, name in enumerate(sortedSegmentNames):
            originalIndex = -1
            for index2, item in enumerate(
                    context.object.pewpew.segments.items()):
                if item[1].segment_name == name:
                    originalIndex = index2
            context.object.pewpew.segments.move(originalIndex, index)
            if name == activeSegmentName:
                context.object.pewpew.active_segment_index = index
        return {"FINISHED"}


class SegmentMoveOperator(bpy.types.Operator):
    """Moves a segment's position in the list in the desired direction"""
    bl_idname = "mesh.segments_move"
    bl_label = "Move Segment"

    up = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return len(context.object.pewpew.segments) > 1

    def execute(self, context):
        if self.up:
            context.object.pewpew.segments.move(
                context.object.pewpew.active_segment_index,
                max(context.object.pewpew.active_segment_index - 1, 0))
            context.object.pewpew.active_segment_index = max(
                context.object.pewpew.active_segment_index - 1, 0)
        else:
            context.object.pewpew.segments.move(
                context.object.pewpew.active_segment_index,
                min(context.object.pewpew.active_segment_index + 1,
                    len(context.object.pewpew.segments) - 1))
            context.object.pewpew.active_segment_index = min(
                context.object.pewpew.active_segment_index + 1,
                len(context.object.pewpew.segments) - 1)
        return {"FINISHED"}


class SegmentAssignOperator(bpy.types.Operator):
    """Assigns selected edges to the active segment"""
    bl_idname = "mesh.segments_assign"
    bl_label = "Assign Selected Edges to Segment"

    @classmethod
    def poll(cls, context):
        return context.object.mode == "EDIT" and len(
            context.object.pewpew.segments) > 0

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        vGroupNameBase = context.object.pewpew.segments[
            context.object.pewpew.active_segment_index].vgroup_base_name
        for edge in context.object.data.edges:
            if not edge.select:
                continue
            firstVertGroups = [
                groupElement.group for groupElement in
                context.object.data.vertices[edge.vertices[0]].groups
                if re.match("pewpew_segment_.+_vgroup.*", context.object.vertex_groups[
                    groupElement.group].name)
            ]
            secondVertGroups = [
                groupElement.group for groupElement in
                context.object.data.vertices[edge.vertices[1]].groups
                if re.match("pewpew_segment_.+_vgroup.*", context.object.vertex_groups[
                    groupElement.group].name)
            ]
            if any(group in secondVertGroups for group in firstVertGroups):
                self.report({"WARNING"}, "A selected edge is already part of a segment. This edge has been dropped from this assign operation. If this edge was already part of this segment, you can safely ignore this warning.")
                continue
            newVGroup = context.object.vertex_groups.new(name=vGroupNameBase)

            newVGroup.add([edge.vertices[0], edge.vertices[1]], 1.0, "REPLACE")
        bpy.ops.object.mode_set(mode='EDIT')
        graphValidationResult = pygraphutils.validate_graph(
            context.object.pewpew.segments[
                context.object.pewpew.active_segment_index].as_graph())
        if graphValidationResult.code == 0:
            context.object.pewpew.segments[
                context.object.pewpew.active_segment_index].is_eulerian = True
        else:
            context.object.pewpew.segments[
                context.object.pewpew.active_segment_index].is_eulerian = False
        if graphValidationResult.code != -0x5 and type(
                graphValidationResult.exception) is not IndexError:
            graphValidationResult.raise_exception()
        return {"FINISHED"}


class SegmentRemoveOperator(bpy.types.Operator):
    """Removes selected edges from the active segment"""
    bl_idname = "mesh.segments_remove"
    bl_label = "Remove Selected Edges from Segment"

    @classmethod
    def poll(cls, context):
        return context.object.mode == "EDIT" and len(
            context.object.pewpew.segments) > 0

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        vGroupNameBase = context.object.pewpew.segments[
            context.object.pewpew.active_segment_index].vgroup_base_name
        groupsToRemove = set()
        for edge in context.object.data.edges:
            if not edge.select:
                continue
            groupsToRemove = groupsToRemove.union({
                context.object.vertex_groups[groupElement.group].name
                for groupElement in context.object.data.vertices[
                    edge.vertices[0]].groups if vGroupNameBase in
                context.object.vertex_groups[groupElement.group].name
            } & {
                context.object.vertex_groups[groupElement.group].name
                for groupElement in context.object.data.vertices[
                    edge.vertices[1]].groups if vGroupNameBase in
                context.object.vertex_groups[groupElement.group].name
            })
        for groupName in groupsToRemove:
            context.object.vertex_groups.remove(
                context.object.vertex_groups[groupName])
        bpy.ops.object.mode_set(mode='EDIT')
        graphValidationResult = pygraphutils.validate_graph(
            context.object.pewpew.segments[
                context.object.pewpew.active_segment_index].as_graph())
        if graphValidationResult.code == 0:
            context.object.pewpew.segments[
                context.object.pewpew.active_segment_index].is_eulerian = True
        else:
            context.object.pewpew.segments[
                context.object.pewpew.active_segment_index].is_eulerian = False
        if graphValidationResult.code != -0x5 and type(
                graphValidationResult.exception) is not IndexError:
            graphValidationResult.raise_exception()
        return {"FINISHED"}


class SegmentSelectOperator(bpy.types.Operator):
    """Selects or deselects all edges in the active segment"""
    bl_idname = "mesh.segments_select"
    bl_label = "Select/Deselect Edges of Segments"

    mode = bpy.props.BoolProperty()  #True = select, False = deselect

    @classmethod
    def poll(cls, context):
        return context.object.mode == "EDIT" and len(
            context.object.pewpew.segments) > 0

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        vGroupNameBase = context.object.pewpew.segments[
            context.object.pewpew.active_segment_index].vgroup_base_name
        vertsToDeselect = set()
        for edge in context.object.data.edges:
            firstVertGroups = [
                groupElement.group for groupElement in
                context.object.data.vertices[edge.vertices[0]].groups
                if vGroupNameBase in context.object.vertex_groups[
                    groupElement.group].name
            ]
            secondVertGroups = [
                groupElement.group for groupElement in
                context.object.data.vertices[edge.vertices[1]].groups
                if vGroupNameBase in context.object.vertex_groups[
                    groupElement.group].name
            ]
            if any(group in secondVertGroups for group in firstVertGroups):
                edge.select = self.mode
                if not self.mode:
                    vertsToDeselect.add(edge.vertices[0])
                    vertsToDeselect.add(edge.vertices[1])
        if not self.mode:
            for poly in context.object.data.polygons:
                if any(vertex in poly.vertices for vertex in vertsToDeselect):
                    poly.select = False
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class MESH_MT_segment_context_menu(bpy.types.Menu):
    bl_label = "Segment Specials"

    def draw(self, _context):
        layout = self.layout
        layout.operator("mesh.segments_sort",
                        icon="SORTALPHA",
                        text="Sort by Name")
        layout.separator()
        layout.operator("mesh.segments_delete",
                        icon="X",
                        text="Delete ALL Segments").remove_all = True


class DATA_PT_segments(bpy.types.Panel):
    bl_label = "Segments"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        row = layout.row()
        segmentExists = len(ob.pewpew.segments) > 0

        row.template_list("MESH_UL_segments",
                          "",
                          ob.pewpew,
                          "segments",
                          ob.pewpew,
                          "active_segment_index",
                          rows=(3, 5)[segmentExists])

        col = row.column(align=True)
        col.operator("mesh.segments_add", icon="ADD", text="")
        col.operator("mesh.segments_delete", icon="REMOVE",
                     text="").remove_all = False

        col.separator()

        col.menu("MESH_MT_segment_context_menu", icon="DOWNARROW_HLT", text="")

        if segmentExists:
            col.separator()
            col.operator("mesh.segments_move", icon="TRIA_UP",
                         text="").up = True
            col.operator("mesh.segments_move", icon="TRIA_DOWN",
                         text="").up = False

            if ob.mode == "EDIT":
                row = layout.row()

                sub = row.row(align=True)
                sub.operator("mesh.segments_assign", text="Assign")
                sub.operator("mesh.segments_remove", text="Remove")

                sub = row.row(align=True)
                sub.operator("mesh.segments_select", text="Select").mode = True
                sub.operator("mesh.segments_select",
                             text="Deselect").mode = False


# def MESH_UL_vgroups_draw_item_original(
#     self, _context, layout, _data, item, icon, _active_data_, _active_propname,
#     _index
# ):  # Original version of the draw_item function from MESH_UL_vgroups in properties_data_mesh.py; used if the modified version is disabled or the add-on is unregistered
#     # assert(isinstance(item, bpy.types.VertexGroup))
#     vgroup = item
#     if self.layout_type in {'DEFAULT', 'COMPACT'}:
#         layout.prop(vgroup, "name", text="", emboss=False, icon_value=icon)
#         icon = 'LOCKED' if vgroup.lock_weight else 'UNLOCKED'
#         layout.prop(vgroup, "lock_weight", text="", icon=icon, emboss=False)
#     elif self.layout_type == 'GRID':
#         layout.alignment = 'CENTER'
#         layout.label(text="", icon_value=icon)

# def MESH_UL_vgroups_draw_item_replacement(
#     self, _context, layout, _data, item, icon, _active_data_, _active_propname,
#     _index
# ):  # Modified version of the draw_item function from MESH_UL_vgroups in properties_data_mesh.py; used to hide the pewpew_segment_*_vgroup vertex groups.
#     # assert(isinstance(item, bpy.types.VertexGroup))
#     vgroup = item
#     if re.match(
#             "pewpew_segment_.+_vgroup", vgroup.name
#     ):  # Quick and dirty way to check if it is a *potential* segment. Instructions on add-on use will discourage users from naming vertex groups as such unless they know what they are doing.
#         return
#     if self.layout_type in {'DEFAULT', 'COMPACT'}:
#         layout.prop(vgroup, "name", text="", emboss=False, icon_value=icon)
#         icon = 'LOCKED' if vgroup.lock_weight else 'UNLOCKED'
#         layout.prop(vgroup, "lock_weight", text="", icon=icon, emboss=False)
#     elif self.layout_type == 'GRID':
#         layout.alignment = 'CENTER'
#         layout.label(text="", icon_value=icon)

# def hideSegmentVGroupsUpdateCallback(self, context):
#     if self.hide_segment_vgroups:
#         bpy.types.MESH_UL_vgroups.draw_item = MESH_UL_vgroups_draw_item_replacement
#     else:
#         bpy.types.MESH_UL_vgroups.draw_item = MESH_UL_vgroups_draw_item_original

# def register():
#     if bpy.context.preferences.addons[__package__.partition(".")
#                                       [0]].preferences.hide_segment_vgroups:
#         bpy.types.MESH_UL_vgroups.draw_item = MESH_UL_vgroups_draw_item_replacement

# def unregister():
#     if bpy.context.preferences.addons[__package__.partition(".")
#                                       [0]].preferences.hide_segment_vgroups:
#         bpy.types.MESH_UL_vgroups.draw_item = MESH_UL_vgroups_draw_item_original