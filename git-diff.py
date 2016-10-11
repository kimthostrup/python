#!/usr/bin/env python

import git
import os
import re
import smtplib
from email.mime.text import MIMEText

emailfrom = "netconfigs@test.com"
emailto = "stuart.howlette@test.com"

join = os.path.join

repo = git.Repo('.')
diffin = repo.head.commit.tree
diffout = repo.git.diff(diffin).split('\n')

diffdict = {}
loopback = "nothing"

for those in diffout:
 if "+++" in those:
  if "configs" in those:
   loopback = those.split('/')[2]
   diffdict[loopback] = {}
   diffdict[loopback]['added'] = []
   diffdict[loopback]['removed'] = []
  else:
   loopback = "nothing"
   diffdict[loopback] = {}
   diffdict[loopback]['added'] = []
   diffdict[loopback]['removed'] = []
 elif re.search("^\+{1}", those):
  diffdict[loopback]['added'].append(those)
 elif re.search("---", those):
  continue
 elif re.search("^\-{1}", those):
  diffdict[loopback]['removed'].append(those)
 else:
  continue

if 'nothing' in diffdict:
 del diffdict['nothing']

if os.path.exists('report.txt'):
 os.remove('report.txt')

report = open('report.txt', 'a')

for elements in diffdict:
 report.write("----------------------------------------------\n")
 report.write("These are the changes for device %s\n" % elements)
 report.write("----------------------------------------------\n\n")
 report.write("Added:\n")
 for added_el in diffdict[elements]['added']:
  report.write(re.sub('^\+', '', added_el))
  report.write("\n")
 report.write("\n")
 report.write("Removed:\n")
 for removed_el in diffdict[elements]['removed']:
  report.write(re.sub('^\-', '', removed_el))
  report.write("\n")
 report.write("----------------------------------------------\n\n")
report.close()

reportread = open('report.txt', 'rb')
errorread = open('errors.txt', 'rb')
msg = MIMEText("Errors Seen: \n\n %s \n\n %s" % (errorread.read(), reportread.read()))
reportread.close()
msg['Subject'] = "Network config backup test"
msg['From'] = emailfrom
msg['To'] = emailto

s = smtplib.SMTP('localhost')
s.sendmail(emailfrom, [emailto], msg.as_string())
s.quit()

if os.path.exists('report.txt'):
 os.remove('report.txt')
