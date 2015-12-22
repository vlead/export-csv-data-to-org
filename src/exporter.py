#######################################################
# File name: exporter.py
# Author: Yogesh Agrawal
# Submission: Dec 10, 2015
# Email: yogeshiiith@gmail.com; yogesh@vlabs.ac.in
#######################################################


import xlrd
import os
import sys
import re
import time

filesexclude = set(["README.md"])
filescombined = "(" + ")|(".join(filesexclude) + ")"

dirsexclude = set([".git", "IIT Bombay", "Amrita"])
dirscombined = "(" + ")|(".join(dirsexclude) + ")"

snoColumnwidth = 5
expnameColumnwidth = 30
testcasenameColumnwidth = 50
passfailColumnwidth = 10
defectColumnwidth = 15


def main(argv):
    if len(argv) < 2:
        print "Please provide the path of the file/directory within quotes in command line!"
    else:
        path = argv[1]
        if os.path.isfile(path) and os.path.exists(path):
            single_file(path)
        elif os.path.isdir(path) and os.path.exists(path):
            walk_over_path(path)
        else:
            print "Provided target does not exists!"

def single_file(path):
    basename = os.path.basename(path)
    name, extension = os.path.splitext(basename)
    if (extension == '.xlsx'):
        process_lab_file(path, name)
    else:
        print "Program does not support the provided file format!"
    return

def walk_over_path(path):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not re.match(dirscombined, d)]
        files[:] = [f for f in files if not re.match(filescombined, f)]
        for f in files:
            name, extension = os.path.splitext(f)
            if (extension == '.xlsx'):
                path = root + "/" + f
                process_lab_file(path, name)
    return

def process_lab_file(path, labName):
    book = xlrd.open_workbook(path)
    number_of_experiments = book.nsheets
    parentDirectory = os.path.dirname(path)
    directory = parentDirectory + "/" + labName
    gitLabUrl = "https://github.com/Virtual-Labs/" + labName
    make_directory(directory)
    parentDirectory = directory
    labTestCases = []
    expToTestCasesCount = []
    for expIndex in range(number_of_experiments):
        experiment = book.sheet_by_index(expIndex)
        directory = parentDirectory + "/" + experiment.name
        gitExpUrl = gitLabUrl +  "/blob/master/test-cases/integration_test-cases" + "/" + experiment.name
        make_directory(directory)
        testCases = process_experiment(experiment, directory, gitExpUrl)
        metaFilePath = directory + "/" + experiment.name + "_metafile.org"
        createMetaFile(testCases, metaFilePath)
        labTestCases.extend(testCases)
    createTestReport(parentDirectory, labTestCases, labName, gitLabUrl)
    return

def make_directory(directory):
    if not os.path.exists(directory):
            os.makedirs(directory)
    return

def process_experiment(experiment, directory, gitExpUrl):
    totalRows = experiment.nrows
    testCases = []
    testCaseFileName = experiment.name + "_01_" +  experiment.row(1)[2].value + ".org"
    linkto =  gitExpUrl + "/" + testCaseFileName
    linkname = testCaseFileName
    referlink = "[[" + linkto + "][" + linkname + "]]"
    postConditions = False
    if (re.match('post conditions', experiment.row(0)[12].value, re.IGNORECASE)):
        postConditions = True
    for row in range(1, totalRows):
        testCaseFileName = experiment.name + "_" + str(row).zfill(2) + "_" + experiment.row(row)[2].value + ".org"
        filepath = directory + "/" + testCaseFileName
        gitTestCaseUrl = gitExpUrl + "/" + testCaseFileName
        testCases.append(gitTestCaseUrl)
        data =  org_data(experiment.row(row), row, postConditions)
        if(row > 1):
            data['preConditions'] = "* Pre/Post conditions\n  - Refer to first test case " + referlink + "\n\n"
        write_to_file(filepath, data)
    return testCases

def org_data(rowValue, rowNumber, postConditions):
    data = {}
    data['author'] = "* Author: " + rowValue[10].value + "\n"
    data['date'] = "* Date Created: " + time.strftime("%d %b %Y") + "\n"
    data['environment'] = "* Environment\n" + reorganize_data_version1(rowValue[12].value) + "\n"
    data['objective'] = "* Objective\n" + reorganize_data_version1(rowValue[6].value) + "\n"
    data['preConditions'] = "* Pre conditions\n" + reorganize_data_version2(rowValue[11].value) + "\n"
    if (postConditions):
        data['postConditions'] = "* Post conditions\n" + reorganize_data_version2(rowValue[12].value) + "\n"
        data['review_comments'] = "* Review/comments\n" + reorganize_data_version1(rowValue[15].value) + "\n"
    else:
        data['postConditions'] = "* Post conditions\n  - Nil" + "\n"
        data['review_comments'] = "* Review/comments\n" + reorganize_data_version1(rowValue[14].value) + "\n"
    if (rowNumber == 1):
        data['testSteps'] = "* Test Steps\n" + reorganize_teststeps(rowValue[7].value) + "\n"
    else:
        data['testSteps'] = "* Test Steps\n" + reorganize_data_version2(rowValue[7].value) + "\n"
    data['result'] = "* Expected result\n" + reorganize_data_version2(rowValue[8].value) + "\n"
    return data

def reorganize_data_version1(data):
    if (len(data) == 0):
        return ""
    splitData = data.split('\n')
    length = len(splitData)
    organizedData = ""
    for line in splitData:
        if(line == '\n' or line == ""):
            continue
        line = line.lstrip(" -")
        organizedData = organizedData + '  - ' + line + "\n"
    return organizedData

def reorganize_data_version2(data):
    if (len(data) == 0):
        return ""
    splitData = data.split('\n')
    length = len(splitData)
    organizedData = ""
    count = 1
    for line in splitData:
        if(line == '\n' or line == ""):
            continue
        line = line.lstrip(" -.1234567890")
        organizedData = organizedData +  '  ' + str(count) + '. ' + line + "\n"
        count+= 1
    return organizedData

def reorganize_teststeps(data):
    if (len(data) == 0):
        return ""
    splitData = data.split('\n')
    length = len(splitData)
    organizedData = ""
    splitData[0] = splitData[0].lstrip(" -")
    organizedData+= '  - ' + splitData[0] + '\n'
    count = 1
    for line in splitData[2:length-1]:
        line = line.lstrip(" -.1234567890")
        organizedData+= '  ' + str(count) + '. ' + line + "\n"
        count+=1
    return organizedData

def write_to_file(filepath, data):
    filepointer = open(filepath, 'w')
    filepointer.write(data['author'].encode("utf-8"))
    filepointer.write(data['date'].encode("utf-8"))
    filepointer.write(data['environment'].encode("utf-8"))
    filepointer.write(data['objective'].encode("utf-8"))
    filepointer.write(data['preConditions'].encode("utf-8"))
    filepointer.write(data['postConditions'].encode("utf-8"))
    filepointer.write(data['testSteps'].encode("utf-8"))
    filepointer.write(data['result'].encode("utf-8"))
    filepointer.write(data['review_comments'].encode("utf-8"))
    filepointer.write("\n")
    filepointer.close()
    return

def createMetaFile(testCases, metaFilePath):
    filePointer = open(metaFilePath, 'w')
    filePointer.write("S.no\t\tTest case link\n")
    count = 1
    for path in testCases:
        basename = os.path.basename(path)
        line = str(count) + ". " + "\t" + "[[" + path + "][" + basename + "]]" + "\n"
        filePointer.write(line)
        count+=1
    filePointer.close()
    return

def generateLine(sno, expname, testcasename, passfail, defectlink, linklength=0):
    snolength = len(sno); sno = sno + " "*(snoColumnwidth - snolength)
    expnamelength = len(expname); expname = expname + " "*(expnameColumnwidth - expnamelength)
    if (linklength==0):
        linklength = len(testcasename);
    testcasename = testcasename + " "*(testcasenameColumnwidth - linklength)
    passfaillength = len(passfail); passfail = passfail + " "*(passfailColumnwidth - passfaillength)
    defectlinklength = len(defectlink); defectlink = defectlink + " "*(defectColumnwidth - defectlinklength)

    line = "| " + sno + "  |  " + expname + "  |  " + testcasename + "  |  " + passfail + "  |  " + defectlink + " |\n"
    return line

def lineBreak():
    line  = "|" + "-"*132+ "|\n"
    return (line)


def createTestReport(parentDirectory, labTestCases, labName, gitLabUrl):
    commit_id = raw_input("Please enter commit id to generate test report for lab: %s\n" %(labName))
    testReportPath = parentDirectory + "/" + labName + "_" + commit_id + "_testreport.org"
    filePointer = open(testReportPath, 'w')
    filePointer.write("* Test Report\n")
    filePointer.write("** Lab Name : %s\n" %(labName))
    filePointer.write("** GitHub URL : %s\n" %(gitLabUrl))
    filePointer.write("** Commit ID : %s\n\n" %(commit_id))
    filePointer.write(lineBreak())

    sno = "*Sno"; expname = "Experiment Name"; testcasename = "Test Case";
    passfail = "Pass/Fail"; defectlink = "Defect Link*";
    line = generateLine(sno, expname, testcasename, passfail, defectlink)
    filePointer.write(line)
    
    filePointer.write(lineBreak())
    count = 1;
    for path in labTestCases:
        basename = os.path.basename(path)
        
        sno = str(count)+ ". "; 
        expname = basename.split("_")[0];
        testcasename = "[[" + path + "][" + basename + "]]";
        passfail = " "; defectlink = " ";

        linklength = len(basename);

        line = generateLine(sno, expname, testcasename, passfail, defectlink, linklength)
        filePointer.write(line)
        filePointer.write(lineBreak())
        count+=1; 
    filePointer.close()
    return

if __name__ == "__main__":
    main(sys.argv)
