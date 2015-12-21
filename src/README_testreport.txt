# Title: Readme file for running testreport.py
# Author: Yogesh Agrawal
# Email: yogeshiiith@gmail.com; yogesh@vlabs.ac.in

1. Description::

This python program generates test report file in org format for each lab.
It also generates meta file for each experiment, containing links to test cases.

Name of the testreport file will be in "<time>_testreport.org" format. Example: "17:49:10_testreport.org"
Name of the meta file will be in <experiment-name>_metafile.org

Test report is generated in org mode as follows:
"""
* Test Report
** Lab name:
** Github URL:
** Commit ID:

<test report table>
"""

Meta file for each experiment is saved inside the experiment folder.
Test report file for each lab is saved in the directory specified in the argument passed to the program.

2. Prerequisite::
a. Test cases for each lab are already generated in org format.


3. Running the script::
Script can be executed as follows:

$ python testreport.py <absoulte path to lab folder> <path to test-report directory>

Example:
$ python testreport.py '/home/centos/QA-Legacy/IIIT Hyderabad/problem-solving-iiith' '/home/centos/test-report'


