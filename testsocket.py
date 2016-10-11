#!/usr/bin/python

import socket
import sys
import urllib2
import argparse
import os.path
import ssl

class MyParser(argparse.ArgumentParser):
 def error(self, message):
  sys.stderr.write('Error: %s\n' % message)
  self.print_help()
  sys.exit(2)

parse = MyParser()
parse.add_argument('-i', '--inputfile', help='Input file in the format IPADDRESS IPPROTOCOL PORT')
if len(sys.argv)==1:
 print "Error: No arguments supplied"
 parse.print_help()
 sys.exit(1)
args=parse.parse_args()

if os.path.isfile(args.inputfile):
 openfile = open(args.inputfile, 'r')
else:
 print "Error: Input File provided does not exist"
 print "\nInput file must be in the following format: -"
 print "\n IPADDRESS IPPROTOCOL PORT"
 print "\neg \n\n 8.8.8.8 udp 53\n 192.168.100.1 tcp ssh"
 sys.exit(1)

socket.setdefaulttimeout(1)

def socket_test(sockaddr, sockport, s):
 try:
  code = s.connect_ex((sockaddr,sockport))
  if code == 0:
   test_res = "Passed"
   return test_res
  else:
   test_res = "Failed"
   return test_res
  s.close()
 except Exception as e:
  test_res = "Failed"
  return test_res
 finally:
  s.close()

def http_test(httpaddr, httpport):
  try:
   response = urllib2.urlopen('http://' + httpaddr)
   html = response.read()
   test_res = "Passed"
   return test_res
  except ssl.CertificateError, e:
   print e
   test_res = "Passed"
   return test_res
  except urllib2.URLError, e:
   if "timed out" in str(e):
    test_res = "Failed"
   else:
    test_res = "Passed"
   return test_res
  except:
   test_res = "Failed"

def https_test(httpsaddr, httpsport):
  try:
   response = urllib2.urlopen('https://' + httpsaddr)
   html = response.read()
   test_res = "Passed"
   return test_res
  except ssl.CertificateError, e:
   print e
   test_res = "Passed"
   return test_res
  except urllib2.URLError, e:
   if "timed out" in str(e):
    test_res = "Failed"
   else:
    test_res = "Passed"
   return test_res
  except:
   test_res = "Failed"

def port_connect(address, port, proto):
 if port == 443:
  test_res = https_test(address, port)
  return test_res
 elif port == 80:
  test_res = http_test(address, port)
  return test_res
 elif proto == "udp":
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  test_res = socket_test(address, port, s)
  return test_res
 elif proto == "tcp":
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  test_res = socket_test(address, port, s)
  return test_res

passed = {}
failed = {}

for each in openfile:
 address = each.split(" ")[0]
 proto = each.split(" ")[1]
 port = int(each.split(" ")[2])
 testresult = port_connect(address, port, proto)
 if testresult == "Passed":
  passed[address] = (proto, port)
 elif testresult == "Failed":
  failed[address] = (proto, port)

print "\n---------------------------------------------------------"
print "| Address		| Protocol	| Port		|" 
print "---------------------------------------------------------"
for each in passed:
 print "| %s	| %s		| %s		|"  % (each, passed[each][0], passed[each][1])
print "---------------------------------------------------------"
print "| Total Passed: %s					|" % len(passed)
print "---------------------------------------------------------\n"


print "\n---------------------------------------------------------"
print "| Address        	| Protocol      | Port  	|"
print "---------------------------------------------------------"
for each in failed:
 print "| %s     	| %s            | %s    	|"  % (each, failed[each][0], failed[each][1])
print "---------------------------------------------------------"
print "| Total Failed: %s					|" % len(failed)
print "---------------------------------------------------------\n"
