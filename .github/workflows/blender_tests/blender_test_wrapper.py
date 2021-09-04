import os, sys, json
print("Testing add-on")
os.system("blender -b -P $GITHUB_WORKSPACE/.github/workflows/blender_tests/blender_tests.py --python-exit-code 63")
if os.path.exists(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test_results.json")):
    exitcode = 0
    with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test_results.json"), "r", encoding="utf-8") as filehandle:
        exitcode = json.load(filehandle)["exitcode"]
    os.chdir(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests"))
    if not 0b100 & exitcode:
        with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test.lua"), "r+") as filehandle:
            content = filehandle.read()
            filehandle.seek(0, 0)
            filehandle.write("local " + content + "\nreturn meshes")
        if os.system("lua5.3 export_validity_test.lua 0"):
            exitcode+=0b100
    if not 0b1000 & exitcode:
        with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test2.lua"), "r+") as filehandle:
            content = filehandle.read()
            filehandle.seek(0, 0)
            filehandle.write("local " + content + "\nreturn meshes")
        if os.system("lua5.3 export_validity_test.lua 1"):
            exitcode+=0b1000
    with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test_results.json"), "r+", encoding="utf-8") as filehandle:
        content = json.load(filehandle)
        content["exitcode"] = exitcode
        filehandle.seek(0, 0)
        json.dump(content, filehandle, ensure_ascii=False)
        filehandle.truncate()
else:
    with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "blender_tests", "test_results.json"), "w", encoding="utf-8") as filehandle:
        json.dump({"exitcode": 63, "tracebacks": ["Test failed. Traceback unavailable. Please see the logs of the Github Action to diagnose the problem."]}, filehandle, ensure_ascii=False)
