import os, ast, zipfile

with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows",
                       "create_release", "version.txt"),
          "w",
          encoding="utf-8") as versionfile:
    with open(
            os.path.join(os.environ["GITHUB_WORKSPACE"],
                         "ppl_meshexport_addon", "__init__.py"),
            "r") as initpyhandle:
        versionfile.write(".".join(
            map(
                str,
                ast.literal_eval(ast.parse(
                    initpyhandle.read()).body[0].value)["version"])))

with zipfile.ZipFile(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "create_release", "ppl_meshexport_addon.zip"), mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=False) as zipfilehandle:
    for root, dirs, files in os.walk(os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon")):
        for file in files:
            if file.endswith(".py") or any(substring in file.lower() for substring in ["license", "licence", "copying"]):
                zipfilehandle.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), os.environ["GITHUB_WORKSPACE"]))