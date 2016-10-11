#!/usr/bin/env python

import re
import sys
from pymongo import MongoClient
import ast

if len(sys.argv) > 0:
 in_csv = sys.argv[1]
 customer = sys.argv[2]
else:
 print "Please provide an input file"

confirm = raw_input("Do you want to insert into the database?")

def split_rules(infile):
 csv_file = open(infile, 'r')
 linedict = {}
 ruledict = {}
 category = ""
 for each in csv_file:
  listrule = (each.strip('\r\n')).split(',')
  if re.search('[a-zA-Z]', listrule[0]) and listrule[0] != "Disabled":
   category = listrule[0]
   continue
  elif re.search('[0-9]', listrule[0]):
   srclist = []
   dstlist = []
   cpsrvclist = []
   fwtargetlist = []
   disabled = 'f'
   lineitem = listrule[0]
   description = listrule[1]
   rule_split = listrule[2:]
   (src, dst, vpn, cpsrvc, fwaction, fwtrack, fwtarget, fwtime, fwcomment) = rule_split[0:]
   if src is not "":
    srclist.append(src)
    linedict['Source'] = srclist
   if dst is not "":
    dstlist.append(dst)
    linedict['Destination'] = dstlist
   if cpsrvc is not "":
    cpsrvclist.append(cpsrvc)
    linedict['Service'] = cpsrvclist
   if fwtarget is "Any":
    linedict['Targets'] = fwtarget
   elif fwtarget is not "":
    fwtargetlist.append(fwtarget)
    linedict['Targets'] = fwtargetlist
   linedict['Category'] = category
   linedict['Disabled'] = disabled
   linedict['Description'] = description
   linedict['Rule Number'] = lineitem
   linedict['Customer'] = customer
   linedict['Action'] = fwaction
   linedict['Comments'] = re.sub('\xa0|\xc2', '', fwcomment)
  else:
   if "Disabled" in listrule[0]:
    disabled = 't'
   rule_split = listrule[2:]
   (src, dst, vpn, cpsrvc, fwaction, fwtrack, fwtarget, fwtime, fwcomment) = rule_split[0:]
   if src is not "":
    srclist.append(src)
    linedict['Source'] = srclist
   if dst is not "":
    dstlist.append(dst)
    linedict['Destination'] = dstlist
   if cpsrvc is not "":
    cpsrvclist.append(cpsrvc)
    linedict['Service']  = cpsrvclist
   if fwtarget is "Any":
    linedict['Targets'] = fwtarget
   elif fwtarget is not "":
    fwtargetlist.append(fwtarget)
    linedict['Targets'] = fwtargetlist
   linedict['Category'] = category
   linedict['Disabled'] = disabled
   linedict['Rule Number'] = lineitem
  ruledict[str(lineitem)] = str(linedict)
 for each in ruledict:
  newdict = ast.literal_eval(ruledict[each])
  mongoconnect(newdict)
 csv_file.close()

def mongoconnect(dictin):
 client = MongoClient()
 db = client.ITS.tier2fw
 #print type(dictin)
 if confirm == 'y':
  db.insert_one(dictin)
 else:
  print dictin

split_rules(in_csv)
