
import xlrd
import os
import sys
import re
import time

filesexclude = set(["README.md"])
filescombined = "(" + ")|(".join(filesexclude) + ")"

dirsexclude = set([".git", "exp.*", "IIT Bombay", "Amrita"])
dirscombined = "(" + ")|(".join(dirsexclude) + ")"

expnameColumnwidth = 50
testcasenameColumnwidth = 60
snoColumnwidth = 10

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
    count = 1
    for expIndex in range(number_of_experiments):
        experiment = book.sheet_by_index(expIndex)
        if (experiment.name == "system"):
            directory = parentDirectory + "/system"
            gitExpUrl = gitLabUrl +  "/blob/master/test-cases/integration_test-cases" + "/system"
        else:
            directory = parentDirectory + "/exp" + str(count).zfill(2)
            gitExpUrl = gitLabUrl +  "/blob/master/test-cases/integration_test-cases" + "/exp" + str(count).zfill(2)
            count+=1
        make_directory(directory)
        testCases = process_experiment(experiment, directory, gitExpUrl)
        metaFilePath = directory + "/" + experiment.name + "_metafile.org"
        createMetaFile(testCases, metaFilePath)
        expToTestCasesCount.append((experiment.name, len(testCases)))
        labTestCases.extend(testCases)
    createTestReport(parentDirectory, labTestCases, expToTestCasesCount, labName, gitLabUrl)
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
    #linkto = directory + "/" + testCaseFileName
    linkname = testCaseFileName
    referlink = "[[" + linkto + "][" + linkname + "]]"
    for row in range(1, totalRows):
        testCaseFileName = experiment.name + "_" + str(row).zfill(2) + "_" + experiment.row(row)[2].value + ".org"
        filepath = directory + "/" + testCaseFileName
        gitTestCaseUrl = gitExpUrl + "/" + testCaseFileName
        testCases.append(gitTestCaseUrl)
        data =  org_data(experiment.row(row), row)
        if(row > 1):
            data['conditions'] = "* Pre/Post conditions\n  - Refer to first test case " + referlink + "\n\n"
        write_to_file(filepath, data)
    return testCases

def org_data(rowValue, rowNumber):
    data = {}
    data['author'] = "* Author: " + rowValue[10].value + "\n"
    data['date'] = "* Date Created: " + time.strftime("%d %b %Y") + "\n"
    data['environment'] = "* Environment\n" + reorganize_data_version1(rowValue[12].value) + "\n"
    data['objective'] = "* Objective\n" + reorganize_data_version1(rowValue[6].value) + "\n"
    data['conditions'] = "* Pre/Post conditions\n" + reorganize_data_version2(rowValue[11].value) + "\n"
    if (rowNumber == 1):
        data['testSteps'] = "* Test Steps\n" + reorganize_teststeps(rowValue[7].value) + "\n"
    else:
        data['testSteps'] = "* Test Steps\n" + reorganize_data_version2(rowValue[7].value) + "\n"
    data['result'] = "* Expected result\n" + reorganize_data_version2(rowValue[8].value) + "\n"
    data['review_comments'] = "* Review comments\n" + reorganize_data_version1(rowValue[14].value) + "\n"
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
    filepointer.write(data['conditions'].encode("utf-8"))
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

def createTestReport(parentDirectory, labTestCases, expToTestCasesCount, labName, gitLabUrl):
    commit_id = raw_input("Please enter commit id for lab: %s\n" %(labName))
    testReportPath = parentDirectory + "/" + labName + "_" + commit_id + "_testreport.org"
    filePointer = open(testReportPath, 'w')
    filePointer.write("* Test Report\n")
    filePointer.write("* Lab Name : %s\n" %(labName))
    filePointer.write("* GitHub URL : %s\n" %(gitLabUrl))
    filePointer.write("* Commit ID : %s\n\n" %(commit_id))
    filePointer.write("#"*160+ "\n")
    filePointer.write("S.no" + " "*14 + "Experiment Name" + " "*50  + "Test Case" + " "*42 + "Pass/Fail" + " "*8  + "Issue Link\n")
    filePointer.write("#"*160+ "\n")
    count = 1; expCount = 0; testCasesCount = 0
    for path in labTestCases:
        if testCasesCount >= expToTestCasesCount[expCount][1]:
            expCount+=1
            testCasesCount = 0
        basename = os.path.basename(path)
        sno = str(count)+ ". "; expname = expToTestCasesCount[expCount][0]; 
        testcasename = "[[" + path + "][" + basename + "]]";
        passfail = " "; link = " ";

        expnamelength = len(expname); linklength = len(basename); snolength = len(sno)
        expname = expname + " "*(expnameColumnwidth - expnamelength)
        testcasename = testcasename + " "*(testcasenameColumnwidth - linklength)
        sno = sno + " "*(snoColumnwidth - snolength)
        line = sno + "  |  " + expname + "  |  " + testcasename + "  |  " + " "*13 + "  |  " + " "*3 + "\n"
        filePointer.write(line)
        filePointer.write("-"*160+ "\n")
        count+=1; testCasesCount+=1
    filePointer.close()
    return

if __name__ == "__main__":
    main(sys.argv)
