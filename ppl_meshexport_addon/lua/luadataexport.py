from math import floor
from ..utils import datatypes as datatypes
from string import ascii_letters, digits


class stringKey(str):
    pass


def isValidLuaId(id):
    if (not id[0] in (ascii_letters + "_")):
        return False
    allowedChars = ascii_letters + digits + "_"
    for letter in id:
        if not letter in allowedChars:
            return False
    return True


def toLua(data, allowFloats, rootName=""):
    if rootName == "":
        out = ""
    else:
        out = rootName + "="
    if type(data) is dict:
        try:
            out += "{"
            for index, key in enumerate(data.keys()):
                if type(key) is stringKey and isValidLuaId(key):
                    out += key+"="+toLua(data[key], allowFloats) + \
                        [",", ""][index == (len(data)-1)]
                else:
                    out +="["+toLua(key, allowFloats)+"]="+toLua(data[key], allowFloats) + \
                        [",", ""][index == (len(data)-1)]
            out += "}"
        except Exception as e:
            raise RuntimeError(
                "Dictionary serialization failed. Current progress: " + out +
                ". Input: " + repr(data)) from e
    elif type(data) in [list, tuple]:
        try:
            out += "{"
            for index, item in enumerate(data):
                out += toLua(item, allowFloats) + [",", ""
                                                   ][index == (len(data) - 1)]
            out += "}"
        except Exception as e:
            raise RuntimeError(
                "List serialization failed. Current progress: " + out +
                ". Input: " + repr(data)) from e
    elif type(data) in [int, datatypes.hexint]:
        if allowFloats:
            out += str(data)
        else:
            out += toFxP(data)
    elif type(data) is float:
        if allowFloats:
            out += str(data)
        else:
            out += toFxP(data)
    elif type(data) is str:
        out += repr(str(data))
    else:
        raise NotImplementedError("Type '" + type(data).__name__ +
                                  "' is not supported by Lua serializer")
    return out


def toFxP(value):
    return ["-", ""][int(value >= 0)] + str(min(
        (2 << 51), floor(abs(value)))) + "." + str(
            floor((abs(value) % 1) * 4096.0)) + "fx"
