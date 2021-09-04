import os, json
jsons = {}
resultcharacters = ["\u2705", "\u274c"]
for directory in os.listdir(os.path.join(os.environ["GITHUB_WORKSPACE"], "artifacts")):
    if os.path.isdir(os.path.join(os.environ["GITHUB_WORKSPACE"], "artifacts", directory)):
        with open(os.path.join(os.environ["GITHUB_WORKSPACE"], "artifacts", directory, os.listdir(os.path.join(os.environ["GITHUB_WORKSPACE"], "artifacts", directory))[0]), "r", encoding="utf-8") as filehandle:
            jsons[directory] = json.load(filehandle)
table = "| Test |"
tablerow2 = "\n| --- |"
tracebacktable = "| Blender Version | Traceback |\n| --- | --- |"
for version in jsons:
    table+=f" {version} |"
    tablerow2+=" --- |"
    tracebacktable[version]='```' + ("\n\n--------------------\n\n".join([tb for tb in jsons[version]["tracebacks"] if type(tb)==str])) + '```'
table+=tablerow2

for index, test in enumerate(["Add-on registration", "Vertex color operator", "Object export with local coordinates, only selected objects", "Object export without local coordinates, all objects", "Add-on unregistration", "Tests (this will show as an error if the test sotware had an error)"]):
    table+=f"\n| {test} |"
    for version in jsons:
        table+=f" {resultcharacters[int(bool(jsons[version]['exitcode'] & (1<<index)))]} |"

with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "post_test", "results_table.txt"), "w", encoding="utf-8") as filehandle:
    filehandle.write(table)
with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "post_test", "traceback_table.txt"), "w", encoding="utf-8") as filehandle:
    filehandle.write(tracebacktable)