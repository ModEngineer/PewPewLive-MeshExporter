import os, shutil, re

with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "post_test", "version.txt"), "w", encoding="utf-8") as versionfile:
    with open(os.path.join(os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon", "__init__.py"), "r") as initpyhandle:
        versionfile.write(".".join(re.search("\"version\": \((.*)\),", initpyhandle.read()).group(1).split(", ")))

shutil.make_archive(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "post_test", "ppl_meshexport_addon"), "zip", os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon")