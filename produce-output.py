#!/usr/bin/python

# Import sys library to process CLI arguments
import sys

# Import file as first CLI argument
if len(sys.argv) > 1:
 file = sys.argv[1]
else:
 print "Please provide a file to parse"
 exit()

f = open(file, 'r')

# Define variables globally to use in functions
global remark
global mydict
global interfacein

# Function creates a dictionary, and populates it with the results of parsing the file passed in
def populate_mydict(inputfile):
 remark = "none"
 mydict = {}
 for line in inputfile:
  acl = line.split(" ")[1]
  if "remark" in line:
   remark = line.split("remark")[1]
  else:
   if remark in mydict:
# Currently will only work against ASA config, will look to change this so that we can find and replace with whatever
    mydict[remark].append((line.replace('access-list ' + acl + ' extended permit','').replace('host ','')))
   else:
    mydict[remark] = [acl]
 print_dict(mydict)

# Prints out dictionary
def print_dict(dictout):
 interfacein = ""
 for each in dictout:
  listlen = len(dictout[each])
  for allitems in dictout[each]:
   if allitems == "0":
    continue
   elif " " not in allitems:
    interfacein = allitems
   else: 
    print "Customer: " + each,
    print "Inbound Interface: " + interfacein
    print "Protocol: " + allitems.split(" ")[1]
    print "Source: " + allitems.split(" ")[2]
    print "Destination: " + allitems.split(" ")[3]
    if len(allitems.split(" ")) <= 5:
     print "\n"
     continue
    elif "range" in allitems:
     print "Port Range Start: " + allitems.split(" ")[5]
     print "Port Range End: " + allitems.split(" ")[6]
     print "\n"
    else:
     print "Ports: " + allitems.split(" ")[5]
     print "\n"
populate_mydict(f)
