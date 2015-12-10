# Title: Readme file for running exporter.py
# Author: Yogesh Agrawal
# Email: yogeshiiith@gmail.com; yogesh@vlabs.ac.in

1. Description::

This python script generates test case files in "org" format from a test case sheets in "xslx" format.
It creates test case file corresponding to each test case per experiment and per lab basis.
Test case org files are saved inside experiment folder.

2. Prerequisite::
a. Test cases for each lab is already there. Name of the files should be same as the name of the git repository
   name for that lab.

b. Install dependencies:
   $ sudo apt-get install python-pip
   $ sudo pip install xlrd

3. Running the script::
Script can be executed as follows:

$ python exporter.py <absoulte path to lab folder where xlsx files are present>

Example:
$ python exporter.py '/home/centos/QA-Legacy/IIIT Hyderabad/problem-solving-iiith.xlsx' (only for one xlsx file)
$ python exporter.py '/home/centos/QA-Legacy/IIIT Hyderabad/' (for multiple xlsx files)


