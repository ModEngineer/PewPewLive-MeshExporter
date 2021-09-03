import os, sys
print("Testing add-on")
exitcode = os.system("blender -b -P $GITHUB_WORKSPACE/.github/workflows/blender_tests/blender_tests.py --python-exit-code 63")
if not 0b10 & exitcode:
    os.chdir(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests"))
    if not 0b100 & exitcode:
        with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test.lua"), "r+") as filehandle:
            content = filehandle.read()
            filehandle.seek(0, 0)
            filehandle.write("local " + content + "\nreturn meshes")
            print("local " + content + "\nreturn meshes")
        if os.system("lua5.3 export_validity_test.lua 0"):
            exitcode+=0b100
    if not 0b1000 & exitcode:
        with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test2.lua"), "r+") as filehandle:
            content = filehandle.read()
            filehandle.seek(0, 0)
            filehandle.write("local " + content + "\nreturn meshes")
            print("local " + content + "\nreturn meshes")
        if os.system("lua5.3 export_validity_test.lua 1"):
            exitcode+=0b1000
with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test_results.json"), "rt", encoding="utf-8") as filehandle:
    print(filehandle.read())
sys.exit(exitcode)
