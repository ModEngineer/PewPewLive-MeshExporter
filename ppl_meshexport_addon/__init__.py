bl_info = {
    "name": "PewPew Live Mesh Exporter",
    "author": "ModEngineer",
    "blender": (2, 80, 0),
    "description": "A mesh exporter for PewPew Live",
    "version": (0, 5, 6),
    "tracker_url":
    "https://github.com/ModEngineer/PewPewLive-MeshExporter/issues",
    "category": "Import-Export"
}  #bl_info MUST be the first thing in the file. AST is used to parse this and get the version when publishing a release.

#Player ship collision has diameter of 16 units
#Player ship model is 32 units wide
#All used libraries should be local

#Import modules
import bpy, importlib

from . import importlist


# Function used for compatibility across Blender versions. Taken from https://github.com/CGCookie/blender-addon-updater/blob/master/addon_updater_ops.py
def make_annotations(cls):
    """Add annotation attribute to fields to avoid Blender 2.8+ warnings"""
    if not hasattr(bpy.app, "version") or bpy.app.version < (2, 80):
        return cls
    if bpy.app.version < (2, 93, 0):
        bl_props = {
            k: v
            for k, v in cls.__dict__.items() if isinstance(v, tuple)
        }
    else:
        bl_props = {
            k: v
            for k, v in cls.__dict__.items()
            if isinstance(v, bpy.props._PropertyDeferred)
        }
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


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
    if bpy.app.version == (2, 79, 0):
        bl_info["blender"] = (2, 79, 0)
    importlib.reload(importlist)
    try:
        for index, registrationItem in enumerate(importlist.importorder):
            if type(registrationItem) == tuple:
                registrationItem[0]()
            else:
                make_annotations(registrationItem)
                bpy.utils.register_class(registrationItem)
    except Exception as e:
        unregister(index)
        raise Exception(
            "Addon failed to register. Automatic unregistration succeeded. Please save your work and restart Blender."
        ) from e
