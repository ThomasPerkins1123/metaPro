import json
import sys
import os
import subprocess
from contextlib import contextmanager

metaProjects = "/home/diffblue/thomas.perkins/metaProjects"
jsonLocation = sys.argv[0].replace("run.py", "projects.json")

projects = {}


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def getCommandOutput(command):
    out = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return out.communicate()[0].decode()


def cloneNewRepo(sshLink):
    projectName = sshLink.split("/")[1].replace(".git", "")
    if projectName in projects:
        print("project already cloned")
    else:
        with cd(metaProjects):
            projects[projectName] = {
                "sshLink": sshLink
            }
            os.system("git clone " + sshLink)

            with cd(projectName):
                subprocess.call("ls")
                if os.path.isfile("pom.xml"):
                    print("maven")
                    projects[projectName]["buildSystem"] = "maven"
                elif os.path.isfile("build.gradle"):
                    print("gradle")
                    projects[projectName]["buildSystem"] = "gradle"
                else:
                    projects[projectName]["buildSystem"] = "unknown"
                    print("unknown")

                if projects[projectName]["buildSystem"] == "maven":
                    output = getCommandOutput("mvn clean compile -B")
                    if "[INFO] BUILD SUCCESS" in output:
                        projects[projectName]["buildCommands"] = ["mvn clean compile"]
                    else:
                        projects[projectName]["buildCommands"] = []
            json.dump(projects, open(jsonLocation, 'w'))


def getProjectName():
    print(os.getcwd())
    return os.getcwd().split("/")[len(os.getcwd().split("/")) - 1]


def buildProject():
    projectName = getProjectName()
    if projectName in projects:
        for command in projects[projectName]["buildCommands"]:
            os.system(command)
    else:
        print("Project not found: " + projectName)


def deleteProject(projectName):
    if projectName in projects:
        del(projects[projectName])
        with cd(metaProjects):
            os.system("rm -rf " + projectName)
    else:
        print("Project no project found with this name")
    json.dump(projects, open(jsonLocation, 'w'))


def setField(field, value):
    projectName = getProjectName()
    print(projectName)
    if projectName in projects:
        if field == "buildCommands":
            projects[projectName]["buildCommands"] = value.split(",")
        elif field == "buildSystem":
            projects[projectName]["buildSystem"] = value
    else:
        print("Not in a metaPro project")
    json.dump(projects, open(jsonLocation, 'w'))


projects = json.load(open(jsonLocation))

i = 1
errorInParams = False
while i < len(sys.argv) and not errorInParams:
    if sys.argv[i] == "-c" or sys.argv[i] == "--clone":
        i += 1
        cloneNewRepo(sys.argv[i])
    elif sys.argv[i] == "-p":
        print(projects.keys())
    elif sys.argv[i] == "-i":
        print(projects)
    elif sys.argv[i] == "build":
        buildProject()
    elif sys.argv[i] == "-s" or sys.argv[i] == "--set":
        i += 1
        setField(sys.argv[i], sys.argv[i + 1])
        i += 1
    elif sys.argv[i] == "-d" or sys.argv[i] == "--delete":
        i += 1
        deleteProject(sys.argv[i])
    elif sys.argv[i] == "-ssssssssss" or sys.argv[i] == "--show":
        i += 1
        if sys.argv[i] == "maven":
            print("showing maven")
        else:
            print("Did not recognise `" + sys.argv[i] + "`")
            errorInParams = True
    elif sys.argv[i] == "--help" or sys.argv[i] == "-h":
        print("  gradle = for single module gradle projects")
    else:
        print("Did not recognise '" + sys.argv[i] + "'")
        errorInParams = True
    i += 1
