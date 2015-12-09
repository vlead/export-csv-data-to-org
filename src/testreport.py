import xlrd
import os
import sys
import re
import time

filesexclude = set([".*testreport.org~", ".*statsreport.org", "README.md", ".*metafile.org", ".*stats.org", ".*testreport.org", ".*.xlsx"])
filescombinedexclude = "(" + ")|(".join(filesexclude) + ")"

filesinclude = set([".*org"])
filescombinedinclude = "(" + ")|(".join(filesinclude) + ")"

dirsexclude = set([".git", "IIT Bombay", "Amrita", "NIT Karnataka"])
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

allTestCasesLink = []

def walk_over_path(path):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not re.match(dirscombined, d)]
        files[:] = [f for f in files if not re.match(filescombinedexclude, f)]
        files[:] = [f for f in files if re.match(filescombinedinclude, f)]
        if files:
            labName = root.split("/")[-2]
            gitLabUrl = "https://github.com/Virtual-Labs/" + labName
            testCasesLink = createMetaFile(root, files, gitLabUrl)
            allTestCasesLink.extend(testCasesLink)
    createTestReport(path, labName, gitLabUrl, allTestCasesLink)
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

def createTestReport(root, labName, gitLabUrl, allTestCasesLink):
    commit_id = raw_input("Please enter commit id for lab: %s\n" %(labName))
    testReportPath = root + "/" + labName + "_" + commit_id + "_testreport.org" 
    filePointer = open(testReportPath, 'w')
    filePointer.write("* Test Report\n")
    filePointer.write("* Lab Name : %s\n" %(labName))
    filePointer.write("* GitHub URL : %s\n" %(gitLabUrl))
    filePointer.write("* Commit ID : %s\n\n" %(commit_id))
    filePointer.write("#"*160+ "\n")
    filePointer.write("S.no" + " "*14 + "Experiment Name" + " "*50  + "Test Case" + " "*42 + "Pass/Fail" + " "*8  + "Issue Link\n")
    filePointer.write("#"*160+ "\n")
    count = 1;
    for path in allTestCasesLink:
        basename = os.path.basename(path)
        sno = str(count)+ ". "; 
        expname = basename.split("_")[0];
        testcasename = "[[" + path + "][" + basename + "]]";
        passfail = " "; link = " ";

        expnamelength = len(expname); linklength = len(basename); snolength = len(sno)
        expname = expname + " "*(expnameColumnwidth - expnamelength)
        testcasename = testcasename + " "*(testcasenameColumnwidth - linklength)
        sno = sno + " "*(snoColumnwidth - snolength)
        line = sno + "  |  " + expname + "  |  " + testcasename + "  |  " + " "*13 + "  |  " + " "*3 + "\n"
        filePointer.write(line)
        filePointer.write("-"*160+ "\n")
        count+=1;
    filePointer.close()
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
    testReportPath = parentDirectory + "/" + labName + "_testreport.org"
    createTestReport(labTestCases, expToTestCasesCount, testReportPath, labName, gitLabUrl)
    return


if __name__ == "__main__":
    main(sys.argv)
