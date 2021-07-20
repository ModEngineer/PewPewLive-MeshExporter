#The registration order is stored in a separate file to make reloading it easier
from .utils import properties
from .newgui import vertexcolorimprovement
from . exporters import exportmesh
importorder = [
        properties.PewPewTemporaryProperties,
        properties.PewPewMeshExporterPreferences,
        (properties.register, properties.unregister),
        vertexcolorimprovement.DATA_PT_vertex_color_improvement,
        vertexcolorimprovement.VertexColorOperator,
        exportmesh.ExportPPLMesh,
        (exportmesh.register, exportmesh.unregister),
]