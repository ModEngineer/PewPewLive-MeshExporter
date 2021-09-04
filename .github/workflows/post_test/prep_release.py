import os, sys, shutil

sys.path.append(os.path.join(os.environ["GITHUB_WORKSPACE"], "tempmodulefolder"))

from ppl_meshexport_addon import bl_info

with open(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "post_test", "version.txt"), "w", encoding="utf-8") as versionfile:
    versionfile.write(".".join([ str(item) for item in bl_info["version"]]))

shutil.make_archive(os.path.join(os.environ["GITHUB_WORKSPACE"], ".github", "workflows", "post_test", "ppl_meshexport_addon"), "zip", os.environ["GITHUB_WORKSPACE"], "ppl_meshexport_addon")