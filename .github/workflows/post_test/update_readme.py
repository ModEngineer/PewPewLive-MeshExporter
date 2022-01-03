import os, re

with open(os.path.join(os.environ["GITHUB_WORKSPACE"], "README.md"),
          "r+",
          encoding="utf-8") as readmehandle:
    testResultSection = ""
    with open(
            os.path.join(os.environ["GITHUB_WORKSPACE"], ".github",
                         "workflows", "post_test", "results_table.txt"),
            "r") as tablehandle1:
        testResultSection += tablehandle1.read()
    with open(
            os.path.join(os.environ["GITHUB_WORKSPACE"], ".github",
                         "workflows", "post_test",
                         "traceback_table.txt")) as tablehandle2:
        testResultSection += "\n\nAny errors produced during tests will be displayed below:\n" + tablehandle2.read(
        )
    readme = re.compile("(<!--tablestart-->)(.*)(<!--tableend-->)",
                        re.DOTALL).sub("\\1\n" + testResultSection + "\n\\3",
                                       readmehandle.read())
    readmehandle.seek(0, 0)
    readmehandle.write(readme)
    readmehandle.truncate()
