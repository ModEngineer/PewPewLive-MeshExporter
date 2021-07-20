bl_info = {
    "name": "PewPew Live Mesh Exporter",
    "author": "ModEngineer",
    "blender": (2, 90, 0),
    "description": "A mesh exporter for PewPew Live",
    "version": (0, 1, 6),
    "tracker_url":
    "https://www.github.com/ModEngineer/PewPewLive-MeshExporter/issues",
    "category": "Import-Export"
}

#Player ship collision has diameter of 16 units
#Player ship model is 32 units wide
#All used libraries should be local

#Import modules
import bpy, importlib

from . import importlist

def unregister(stop=-1):
    if stop == -1:
        stop = len(importlist.importorder)
    else:
        stop += 1
    try:
        for registrationItem in reversed(importlist.importorder[:stop]):
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
    importlib.reload(importlist)
    try:
        for index, registrationItem in enumerate(importlist.importorder):
            if type(registrationItem) == tuple:
                registrationItem[0]()
            else:
                bpy.utils.register_class(registrationItem)
    except Exception as e:
        unregister(index)
        raise Exception(
            "Addon failed to register. Automatic unregistration succeeded. Please save your work and restart Blender."
        ) from e
