#The registration order is stored in a separate file to make reloading it easier
from .utils import properties
from .newgui import vertexcolorimprovement, segments, dualmesh
from .exporters import exportmesh

importorder = [
    properties.PewPewSceneProperties,
    properties.SegmentProperties,
    properties.DualMeshProperties,
    properties.PewPewObjectProperties,
    properties.PewPewMeshExporterPreferences,
    (properties.register, properties.unregister),
    segments.MESH_UL_segments,
    segments.SegmentAddOperator,
    segments.SegmentSortOperator,
    segments.SegmentDeleteOperator,
    segments.SegmentMoveOperator,
    segments.SegmentAssignOperator,
    segments.SegmentRemoveOperator,
    segments.SegmentSelectOperator,
    segments.MESH_MT_segment_context_menu,
    segments.DATA_PT_segments,
    # (segments.register, segments.unregister),
    dualmesh.CreateWireframeOperator,
    dualmesh.ApplyWireframeOperator,
    dualmesh.DATA_PT_pewpew_wireframe,
    (dualmesh.register, dualmesh.unregister),
    vertexcolorimprovement.DATA_PT_vertex_color_improvement,
    vertexcolorimprovement.VertexColorOperator,
    exportmesh.ExportPPLMesh,
    (exportmesh.register, exportmesh.unregister),
]