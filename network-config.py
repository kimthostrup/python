#!/usr/bin/env python

import paramiko
import getpass
import scp
import os
import shutil
import sqlite3
import time
from netmiko import ConnectHandler


class hpcomware_template(object):
 dtype = 'hp_comware'
 cmdin = 'display current-config'
 cfgfiles = ['startup.cfg','config.cfg']
 devpath = ''
 allfiles = False
 def __init__(self, hostname, ipaddr):
  self.hostname = hostname
  self.ipaddr = ipaddr
  self.scpconn = True
  self.netmikoconn = True
  self.paramikoconn = False

class f5_template(object):
 dtype = 'f5'
 cfgfiles = ['bigip_base.conf','bigip.conf','bigip_gtm.conf','bigip_user.conf'] 
 devpath = '/config/'
 allfiles = True
 def __init__(self, hostname, ipaddr):
  self.hostname = hostname
  self.ipaddr = ipaddr
  self.scpconn = True
  self.netmikoconn = False
  self.paramikoconn = False

class ciscoios_template(object):
 dtype = 'cisco_ios'
 cmdin = 'show running'
 cfgfiles = ['running-config']
 devpath = ''
 allfiles = True
 def __init__(self, hostname, ipaddr):
  self.hostname = hostname
  self.ipaddr = ipaddr
  self.scpconn = True
  self.netmikoconn = True
  self.paramikoconn = False

class hptp_template(object):
 dtype = 'hp_tippingpoint'
 cmdin = 'display-config running\n\n'
 cfgfiles = ['running-config']
 devpath = ''
 exitcmd = "logout\n"
 recvlngth = "2000000"
 allfiles = True
 def __init__(self, hostname, ipaddr):
  self.hostname = hostname
  self.ipaddr = ipaddr
  self.sleeptime = 10
  self.scpconn = False
  self.netmikoconn = False
  self.paramikoconn = True

if os.path.exists('errors.txt'):
 os.remove('errors.txt')

baseuser = raw_input('Please enter your username: ')
basepass = getpass.getpass()

def scp_func(devicein,destpath):
 for cfgfile in devicein.cfgfiles:
  errcnt = 0
  try:
   ssh_client = paramiko.SSHClient()
   ssh_client.load_system_host_keys()
   ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh_client.connect(devicein.ipaddr, username=baseuser, password=basepass,look_for_keys=False)    
   scp_client = scp.SCPClient(ssh_client.get_transport())
   scp_client.get("%s%s" % (devicein.devpath, cfgfile))
   shutil.copy(cfgfile, destpath)
   scp_client.close()
   worked = True
   if devicein.allfiles == False:
    break
  except Exception as e:
   if "Failed to read the source file" in str(e) and devicein.allfiles == True:
    writerror(devicein.ipaddr, e)
   elif "Failed to read the source file" in str(e) and devicein.allfiles == False:
    errcnt += 1
    if errcnt == len(devicein.cfgfiles):
     writerror(devicein.ipaddr, e)
    else:
     continue
   elif len(str(e)) > 1:
    writeerror(devicein.ipaddr, e)
   else:
    pass
   worked = False
 return worked

def connect_to_device(devicein,destpath):
 try:
  net_connect = ConnectHandler(device_type=devicein.dtype, ip=devicein.ipaddr, username=baseuser, password=basepass, verbose=True)
  if devicein.dtype == "hp_comware":
   output = net_connect.send_command(devicein.cmdin)
  elif devicein.dtype == "cisco_ios":
   output = net_connect.send_command_expect(devicein.cmdin)
  net_connect.disconnect()
  filetowrite = devicein.cfgfiles[0]
  outfile = open(filetowrite, 'a')
  outfile.write(output)
  shutil.copy(filetowrite, destpath)
  os.remove(filetowrite)
 except Exception as e:
  writeerror(devicein.ipaddr, e)

def paramiko_connect(devicein,destpath):
 try:
  ssh_client = paramiko.SSHClient()
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh_client.connect(devicein.ipaddr, username=baseuser, password=basepass, look_for_keys=False)
  chan = ssh_client.invoke_shell()
  chan.send(devicein.cmdin)
  time.sleep(devicein.sleeptime)
  chan.send(devicein.exitcmd)
  output = chan.recv(devicein.recvlngth)
  ssh_client.close()
  filetowrite = devicein.cfgfiles[0]
  outfile = open(filetowrite, 'a')
  for lines in output.split('\n'):
   outfile.write(str(lines))
   outfile.write('\n')
  shutil.copy(filetowrite, destpath)
  os.remove(filetowrite)
 except Exception as e:
  writeerror(devicein.ipaddr, e)

def writeerror(ipaddress, error):
 errorfile = open('errors.txt', 'a')
 errorfile.write("%s: %s\n" % (ipaddress, error))
 errorfile.close()


def class_connection(rowclass):
 if rowclass.scpconn == True:
  scpresult = scp_func(rowclass,destpath)
  if scpresult == False and rowclass.netmikoconn == True:
   connect_to_device(rowclass,destpath)
  for cfgs in rowclass.cfgfiles:
   if os.path.isfile(cfgs):
    os.remove(cfgs)
 elif rowclass.scpconn == False and rowclass.netmikoconn == True:
  connect_to_device(rowclass,destpath)
  for cfgs in rowclass.cfgfiles:
   if os.path.isfile(cfgs):
    os.remove(cfgs)
 elif rowclass.paramikoconn == True:
  paramiko_connect(rowclass,destpath)
  for cfgs in rowclass.cfgfiles:
   if os.path.isfile(cfgs):
    os.remove(cfgs)


conn = sqlite3.connect('hosts.db')
connc = conn.cursor()

for row in connc.execute('SELECT * FROM infrastructure'):
 hostname = str(row[0])
 ipaddr = str(row[1])
 dtype = str(row[2])
 active = str(row[3])
 destpath = "configs/%s" % hostname
 if not os.path.exists(destpath):
  os.makedirs(destpath)
 if active == "n":
  continue 
 elif "hpcomware" in dtype: 
  hpclass = hpcomware_template(hostname, ipaddr)
  rowclass = hpclass
 elif "ciscoios" in dtype:
  ciscoclass = ciscoios_template(hostname, ipaddr)
  rowclass = ciscoclass
 elif "f5bigip" in dtype:
  f5class = f5_template(hostname, ipaddr)  
  rowclass = f5class
 elif "hptp" in dtype:
  tpclass = hptp_template(hostname, ipaddr)
  rowclass = tpclass
 class_connection(rowclass)
 
conn.close()
