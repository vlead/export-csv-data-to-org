#######################################################
# File name: statistics.py
# Author: Yogesh Agrawal
# Submission: Dec 10, 2015
# Email: yogeshiiith@gmail.com; yogesh@vlabs.ac.in
#######################################################

import os
import sys
import re
import time

filesinclude = set([".*testreport.org"])
filescombined = "(" + ")|(".join(filesinclude) + ")"

filesexclude = set([".*testreport.org~", ".*statsreport.org", ".*.html"])
filescombinedexcl = "(" + ")|(".join(filesexclude) + ")"

dirsexclude = set([".git", "IIT Bombay", "Amrita"])
dirscombined = "(" + ")|(".join(dirsexclude) + ")"

snoColumnwidth = 5
expnameColumnwidth = 30
passColumnwidth = 10
failColumnwidth = 11


def main(argv):
    if len(argv) < 2:
        print "Please provide the path of the file/directory within quotes in command line!"
    else:
        path = argv[1]
        if os.path.isfile(path):
            single_file(path)
        else:
            walk_over_path(path)

def single_file(path):
    basename = os.path.basename(path)
    basedir = os.path.dirname(path)
    name, extension = os.path.splitext(basename)
    if (re.match(".*_testreport.org", basename)):
        totalStatistics = {}
        statistics = getStatistics(path)
    else:
        print "Program does not support the provided file format!"
    return

def walk_over_path(path):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not re.match(dirscombined, d)]
        files[:] = [f for f in files if re.match(filescombined, f) and not re.match(filescombinedexcl, f)]
        for f in files:
            if (re.match(".*_testreport.org", f)):
                filePath = root + "/" + f
                statistics = getStatistics(filePath)
    return

def getStatistics(path):
    statistics = {}

    filePointer = open(path, 'r')
    filePointer.readline()
    labNameLine = filePointer.readline()
    gitLabUrlLine = filePointer.readline()
    commitIdLine = filePointer.readline()
    filePointer.readline(); filePointer.readline(); filePointer.readline(); filePointer.readline()
    for line in filePointer.readlines():
        line = line.strip("|\n")
        if re.match('--', line):
            continue
        splitData = line.split('|')
        splitData = [item.strip() for item in splitData]
        if (splitData[1] not in statistics):
            statistics[splitData[1]] = {}
            statistics[splitData[1]]['fail'] = 0
            statistics[splitData[1]]['pass'] = 0
        try:
            if(re.match('pass', splitData[3], re.IGNORECASE)):
                statistics[splitData[1]]['pass'] += 1
            elif(re.match('fail', splitData[3], re.IGNORECASE)):
                statistics[splitData[1]]['fail'] += 1
        except:
            if(re.match('pass', splitData[3], re.IGNORECASE)):
                statistics[splitData[1]] = {}
                statistics[splitData[1]]['pass'] = 1
                statistics[splitData[1]]['fail'] = 0
            elif(re.match('fail', splitData[3], re.IGNORECASE)):
                statistics[splitData[1]] = {}
                statistics[splitData[1]]['fail'] = 1
                statistics[splitData[1]]['pass'] = 0

    filePointer.close()
    dirname = os.path.dirname(path)
    commitId = commitIdLine.split(" ")[-1].strip("\n")
    labName = labNameLine.split(" ")[-1].strip("\n")
    exppath = dirname + "/" + labName + "_" + commitId + "_statsreport.org"
    write_to_file_per_lab(exppath, labNameLine, gitLabUrlLine, commitIdLine, statistics)
    return statistics

def generateLine(sno, expname, passcount, failcount):
    snolength = len(sno); sno = sno + " "*(snoColumnwidth - snolength)
    expnamelength = len(expname); expname = expname + " "*(expnameColumnwidth - expnamelength)
    passcountlength = len(passcount); passcount = passcount + " "*(passColumnwidth - passcountlength)
    failcountlength = len(failcount); failcount = failcount + " "*(failColumnwidth - failcountlength)

    line = "| " + sno + "  |  " + expname + "  |  " + passcount + "  |  " + failcount + " |\n"
    return line

def lineBreak():
    line  = "|" + "-"*73+ "|\n"
    return (line)


def write_to_file_per_lab(path, labNameLine, gitLabUrlLine, commitIdLine, data):
    filePointer = open(path, 'w')
    filePointer.write("* Statistics Report\n")
    filePointer.write(labNameLine)
    filePointer.write(gitLabUrlLine)
    filePointer.write(commitIdLine)
    filePointer.write("\n")
   
    table = lineBreak()
    table+= generateLine("*S.no", "Experiment Name", "Pass Count", "Fail Count*")
    table+= lineBreak() 
    count = 1
    passcount = 0;    failcount = 0
    for exp in data:
        sno = str(count);  passcountstr = str(data[exp]['pass']); failcountstr = str(data[exp]['fail'])
        line = generateLine(sno, exp, passcountstr, failcountstr)
        table += line + lineBreak()
        #line = str(count) + ". \t" + exp + "\t\t"  +str(data[exp]['pass']) + "\t\t" + str(data[exp]['fail']) + "\n"
        #tab.add_row([count, exp, data[exp]['pass'], data[exp]['fail']])
        passcount+=data[exp]['pass']
        failcount+=data[exp]['fail']
        count+=1

    filePointer.write("Total number of passed test cases = %s\n\n" %(passcount))
    filePointer.write("Total number of failed test cases = %s\n\n" %(failcount))
    
    filePointer.write(table)

    filePointer.close()
    return


if __name__ == "__main__":
    main(sys.argv)
