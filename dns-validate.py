#!/usr/bin/python

import dns.resolver
import dns.reversename
import argparse
import os.path
import sys

class MyParser(argparse.ArgumentParser):
 def error(self, message):
  sys.stderr.write('Error: %s\n' % message)
  self.print_help()
  sys.exit(2)

parse = MyParser()
parse.add_argument('-i', '--inputfile', help='Input file in the format IPADDRESS IPPROTOCOL PORT')
parse.add_argument('-n', '--noreverse', action='store_true', help='No printing of reverse records evaluation')
parse.add_argument('-t', '--totals', action='store_true', help='Only print the totals, nothing else')
if len(sys.argv)==1:
 print "Error: No arguments supplied"
 parse.print_help()
 sys.exit(1)
args=parse.parse_args()

if os.path.isfile(args.inputfile):
 openfile = open(args.inputfile, 'r')
else:
 print "Error: Input File provided does not exist"
 print "\nInput file must look like the following format: -"
 print "example.com. example.com IN SOA"  
 print "example.com. NS a.iana-servers.net."    
 print "example.com. NS b.iana-servers.net."   
 print "example.com. www A 93.184.216.34"
 sys.exit(1)

passeda = 0
faileda = 0
passedptr = 0
failedptr = 0

def dns_query(hostname, recordtype, nstest):
 myResolver = dns.resolver.Resolver()
 if nstest:
  myResolver.nameservers = [nstest]
 try:
  myAnswers = myResolver.query(hostname, recordtype)
  reversed = "None"
  for rdata in myAnswers:
   resolved = str(rdata)
   if recordtype == "A":
    try:
     resolved2 = resolved
     rev_res = dns.reversename.from_address(resolved2)
     myReverse = myResolver.query(rev_res, "PTR")
     for thedata in myReverse:
      reversed = str(thedata)
    except:
      reversed = "Nope"
   else:
    reversed = "Nope"
   return resolved, reversed
 except:
  rdata = "No Record"
  return "No Record", "Nope"

domain_dict = {}

for each in openfile:
 if "SOA" in each:
  soa_pre = str(each).strip("\n").split(" ")
  soa_domain = soa_pre[0]
  soa_record, nope = dns_query(soa_domain, "SOA", "")
  if args.totals == False:
   print "\nSOA Record: \n%s \n\nResource Records: \n" % (soa_record)
  nslist = []
  nslist2 = []
  alist = []
 elif "NS" in each:
  ns_pre = str(each).strip("\n").split(" ")
  ipaddr, nope = dns_query(ns_pre[2], "A", "")
  nslist.append(ipaddr)
 elif "CNAME" in each:
  continue
 elif "A":
  a_pre = str(each).strip("\n").split(" ")
  astring = "%s.%s %s" % (a_pre[1], a_pre[0], a_pre[3])
  alist = astring.split(" ")
  for ns_test in nslist:
   resolvedto, reversedto = dns_query(alist[0], "A", ns_test)
   if str(alist[1]) in str(resolvedto):
    if args.totals == False:
     print "Success! %s resolves correctly to %s on Name Server %s" % (alist[0], alist[1], ns_test)
    passeda += 1
   else:
    if args.totals == False:
     print "Failure! %s does not resolve correctly to %s on Name Server %s" % (alist[0], alist[1], ns_test)
    faileda += 1
   if args.noreverse == True:
    continue
   elif "Nope" in reversedto:
    if args.totals == False:
     print "Failure! %s has no reverse record" % (alist[1])
    failedptr += 1
   else:
    if args.totals == False:
     print "%s has a reverse record of %s" % (alist[1], reversedto)
    passedptr += 1


print "Passed A: %s, Failed A: %s, Passed PTR: %s, Failed PTR: %s" % (passeda, faileda, passedptr, failedptr)
