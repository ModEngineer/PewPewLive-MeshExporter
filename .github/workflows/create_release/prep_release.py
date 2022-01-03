import os, shutil, ast

with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "create_release", "version.txt"), "w", encoding="utf-8") as versionfile:
    with open(os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon", "__init__.py"), "r") as initpyhandle:
        versionfile.write(".".join(map(str,ast.literal_eval(ast.parse(initpyhandle.read()).body[0].value)["version"])))

shutil.make_archive(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "create_release", "ppl_meshexport_addon"), "zip", os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon")
