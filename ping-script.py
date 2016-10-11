#!/usr/bin/env python

import sys
import subprocess
from decimal import Decimal

if len(sys.argv) > 1:
 f = open(sys.argv[1], 'r')
else:
 print "Please provide input file"


for host in f:
 ping = subprocess.Popen(["ping", "-c", "3", "-W", "0.5", "-w", "3", host], stdout=subprocess.PIPE)
 results = []
 for line in ping.stdout.readlines():
  if "64 bytes" in line:
   output = ((line.split("time=")[1]).strip("\n")).split(" ")[0]
   results.append(output)
 if len(results) > 2:
  firstres, secondres, thirdres = results
  avgout = (float(firstres) + float(secondres) + float(thirdres))/3
  avgdp = round(avgout,2)
  print "Results for " + host.strip("\n") + ": " + firstres + "ms " + secondres + "ms " + thirdres + "ms - Average RTT of " + str(avgdp) + "ms"
 elif len(results) > 0:
  print "Results for " + host.strip("\n") + ": " + str(3 - len(results)) + " packets dropped"
 else:
  print "Results for " + host.strip("\n") + ": No response"
 ping.kill()
