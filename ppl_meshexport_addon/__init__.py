bl_info = {
    "name": "PewPew Live Mesh Exporter",
    "author": "ModEngineer",
    "blender": (2, 90, 0),
    "description": "A mesh exporter for PewPew Live",
    "version": (0, 1, 4),
    "tracker_url":
    "https://www.github.com/ModEngineer/PewPewLive-MeshExporter/issues",
    "category": "Import-Export"
}

#Player ship collision has diameter of 16 units
#Player ship model is 32 units wide
#All used libraries should be local

#Import modules
import bpy, importlib

from .exporters import exportmesh
from .newgui import vertexcolorimprovement
from .utils import properties

classes = [
    properties.PewPewMeshExporterPreferences,
    properties.PewPewTemporaryProperties,
    (properties.register, properties.unregister),
    vertexcolorimprovement.DATA_PT_vertex_color_improvement,
    vertexcolorimprovement.VertexColorOperator,
    exportmesh.ExportPPLMesh,
    (exportmesh.register, exportmesh.unregister),
]


def unregister(stop=-1):
    if stop == -1:
        stop = len(classes)
    else:
        stop += 1
    try:
        for registrationItem in reversed(classes[:stop]):
            if type(registrationItem) == tuple:
                registrationItem[1]()
            else:
                bpy.utils.unregister_class(registrationItem)
    except Exception as e:
        if stop == -1:
            raise Exception(
                "Add-on failed to unregister. To fully unregister, please save your work and restart Blender."
            ) from e
        else:
            raise Exception(
                "Addon failed to register. Automatic unregistration failed. To fully unregister, please save your work and restart Blender."
            ) from e


def register():
    importlib.reload(exportmesh)
    importlib.reload(vertexcolorimprovement)
    importlib.reload(properties)
    try:
        for index, registrationItem in enumerate(classes):
            if type(registrationItem) == tuple:
                registrationItem[0]()
            else:
                bpy.utils.register_class(registrationItem)
    except Exception as e:
        unregister(index)
        raise Exception(
            "Addon failed to register. Automatic unregistration succeeded. Please save your work and restart Blender."
        ) from e
