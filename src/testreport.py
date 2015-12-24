#######################################################
# File name: testreport.py
# Author: Yogesh Agrawal
# Submission: Dec 10, 2015
# Email: yogeshiiith@gmail.com; yogesh@vlabs.ac.in
#######################################################



import os
import sys
import re
import time

filesexclude = set([".*testreport.org~", ".*statsreport.org", "README.md", ".*metafile.org", ".*stats.org", ".*testreport.org", ".*.xlsx", ".*.html"])
filescombinedexclude = "(" + ")|(".join(filesexclude) + ")"

#filesinclude = set([".*org"])
#filescombinedinclude = "(" + ")|(".join(filesinclude) + ")"

dirsexclude = set([".git", "IIT Bombay", "Amrita", "NIT Karnataka"])
dirscombined = "(" + ")|(".join(dirsexclude) + ")"

snoColumnwidth = 5
expnameColumnwidth = 30
testcasenameColumnwidth = 50
passfailColumnwidth = 10
defectColumnwidth = 15
severityColumnwidth = 12
allTestCasesLink = []

def main(argv):
    if len(argv) < 2:
        print "Please provide the path of the lab directory within quotes in command line!"
    else:
        path = argv[1]
        targetDir = argv[2]
        if os.path.isdir(path) and os.path.exists(path):
            path = path.rstrip("/")
            targetDir = targetDir.rstrip("/")
            walk_over_path(path, targetDir)
        else:
            print "Provided target does not exists!"

def create_testreport_inside_project(projectName, path):
    testReportPath = path + "/testreport.org"
    linkToTestReport = "https://github.com/Virtual-Labs/test-reports/tree/master/" + projectName
    if not os.path.isfile(testReportPath):
        filePointer = open(testReportPath, 'w')
        content = "[[%s][View Test Report for %s Lab]]" %(linkToTestReport, projectName)
        filePointer.write(content)
        filePointer.close()
    return


def walk_over_path(path, targetDir):
    projectName = os.path.basename(path)
    create_testreport_inside_project(projectName, path)
    testCasesPath = path + "/test-cases/integration_test-cases/"
    for root, dirs, files in os.walk(testCasesPath):
        dirs[:] = [d for d in dirs if not re.match(dirscombined, d)]
        files[:] = [f for f in files if not re.match(filescombinedexclude, f)]
        #files[:] = [f for f in files if re.match(filescombinedinclude, f)]
        if files:
            files = sorted(files)
            labName = root.split("/")[-2]
            gitLabUrl = "https://github.com/Virtual-Labs/" + labName
            testCasesLink = createMetaFile(root, files, gitLabUrl)
            allTestCasesLink.extend(testCasesLink)
    createTestReport(projectName, labName, gitLabUrl, allTestCasesLink, targetDir)
    return

def createMetaFile(root, testCases, gitLabUrl):
    expname = testCases[0].split("_")[0]
    metaFilePath = root + "/" + expname + "_metafile.org"
    filePointer = open(metaFilePath, 'w')
    filePointer.write("S.no\t\tTest case link\n")
    count = 1
    labName = root.split("/")[-2]
    expname = root.split("/")[-1]
    gitExpUrlPartial = gitLabUrl +  "/blob/master/test-cases/integration_test-cases/" + expname
    testCasesLink = []
    for path in testCases:
        gitExpUrl = gitExpUrlPartial + "/" + path
        testCasesLink.append(gitExpUrl)
        line = str(count) + ". " + "\t" + "[[" + gitExpUrl + "][" + path + "]]" + "\n"
        filePointer.write(line)
        count+=1
    filePointer.close()
    return testCasesLink

def generateLine(sno, expname, testcasename, passfail, severity, defectlink, linklength=0):
    snolength = len(sno); sno = sno + " "*(snoColumnwidth - snolength)
    expnamelength = len(expname); expname = expname + " "*(expnameColumnwidth - expnamelength)
    if (linklength==0):
        linklength = len(testcasename); 
    testcasename = testcasename + " "*(testcasenameColumnwidth - linklength)
    passfaillength = len(passfail); passfail = passfail + " "*(passfailColumnwidth - passfaillength)
    defectlinklength = len(defectlink); defectlink = defectlink + " "*(defectColumnwidth - defectlinklength)
    severitylength = len(severity); severity = severity + " "*(severityColumnwidth - severitylength)
    line = "| " + sno + "  |  " + expname + "  |  " + testcasename + "  |  " + passfail + "  |  " + severity + " | " + defectlink + " |\n"
    return line

def lineBreak():
    line  = "|" + "-"*147+ "|\n"
    return (line)

def make_directory(directory):
    if not os.path.exists(directory):
            os.makedirs(directory)
    return

def getDateTime():
    timetuple = time.localtime()
    date = "%s-%s-%s" %(timetuple[2], timetuple[1], timetuple[0])
    currenttime = "%s:%s:%s" %(timetuple[3], timetuple[4], timetuple[5])
    return date, currenttime

def createTestReport(projectName, labName, gitLabUrl, allTestCasesLink, targetDir):
    commit_id = raw_input("Please enter commit id for lab: %s\n" %(labName))
    date, time = getDateTime()
    
    projectDirectory = targetDir + "/"  + projectName
    make_directory(projectDirectory)
    testreportDirectory = projectDirectory + "/" + "%s_%s" %(date, commit_id)
    make_directory(testreportDirectory)

    testReportPath = testreportDirectory + "/" + time + "_testreport.org" 
    filePointer = open(testReportPath, 'w')
    filePointer.write("* Test Report\n")
    filePointer.write("** Lab Name : %s\n" %(labName))
    filePointer.write("** GitHub URL : %s\n" %(gitLabUrl))
    filePointer.write("** Commit ID : %s\n\n" %(commit_id))
    filePointer.write(lineBreak())

    sno = "*Sno"; expname = "Experiment Name"; testcasename = "Test Case";
    passfail = "Pass/Fail"; severity = "Severity"; defectlink = "Defect Link*"; 

    line = generateLine(sno, expname, testcasename, passfail, severity, defectlink)

    filePointer.write(line)
    filePointer.write(lineBreak())
    count = 1;
    for path in allTestCasesLink:
        basename = os.path.basename(path)

        sno = str(count)+ ". "; 
        expname = basename.split("_")[0];
        testcasename = "[[" + path + "][" + basename + "]]";
        passfail = ""; defectlink = ""; severity = ""; 

        linklength = len(basename); 

        line = generateLine(sno, expname, testcasename, passfail, severity, defectlink, linklength)
        filePointer.write(line)
        filePointer.write(lineBreak())
        count+=1;
    filePointer.close()
    return

if __name__ == "__main__":
    main(sys.argv)
