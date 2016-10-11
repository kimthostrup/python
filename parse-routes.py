#!/usr/bin/python

import sys
import re

if len(sys.argv) > 1:
 inputfile = sys.argv[1]
 device = sys.argv[2]
else:
 print "Please provide an input file:"

openfile = open(inputfile, 'r')
writefile = open(inputfile+"-parsed", 'w')

vrf = ""
rd = ""
route = ""
nexthop = ""
preroutelist = []

for each in openfile:
 if "Route Distinguisher" in each:
  rd = ""
  vrf = ""
  rdasn = each.split(':')[1]
  rdnn = each.split(':')[2]
  rd = (str(rdasn + ":" + rdnn)).split('\n')[0]
 elif "vpn-instance" in each:
  rd = ""
  vrf = ""
  replaced = each.replace('Total routes of vpn-instance ','')
  vrf = replaced.split(':')[0]
 elif "Network" in each:
  continue
 else:
  route_regex = re.sub('[*^>i]','', each)
  route_despace = re.sub('[ ]{2,}',' ', route_regex)
  route_split = route_despace.split(' ')
  if len(route_split) < 2:
   pass
  elif len(route_split) <= 3:
   nexthop = route_split[1]
  else:
   if "NULL" in route_split[3]:
    route = route_split[1]
    nexthop = route_split[2]
   else:
    nexthop = route_split[1]
   preroutelist.append(str(device + rd + vrf + " " + route + " " + nexthop))
   routelist = set(preroutelist)

for elements in routelist:
 writefile.write(elements + "\n")


openfile.close()
writefile.close()
