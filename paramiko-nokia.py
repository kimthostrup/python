#!/usr/bin/python

import paramiko
import sys
import getpass
import time

myusername = str(raw_input("Please input your username: "))
mypassword = getpass.getpass()

print myusername

if len(sys.argv) > 1:
 connect_to = sys.argv[1]
else:
 print "Please supply a host to connect to"
 exit()

def remote_connect(hostname, conf):
      try:
       ssh = paramiko.SSHClient()
       ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       ssh.connect(hostname, username=myusername, password=mypassword, look_for_keys=False)
       print "Connected to %s" % hostname
       chan = ssh.invoke_shell()
       chan.send("\n\nenvironment no more\n\n")
       time.sleep(1)
       chan.send(conf)
       time.sleep(2)
       chan.send("logout\n")
       print chan.recv(100000)
       ssh.close()
      except paramiko.SSHException as error:
        print "%s gave error %s" % hostname, error
        sys.exit(1)

cmd = "admin display-config\n\n"
remote_connect(connect_to, cmd)
cmd = "show bof\n\n"
remote_connect(connect_to, cmd)
