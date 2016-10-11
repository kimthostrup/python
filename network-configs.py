#!/usr/bin/env python

import paramiko
import getpass
import scp
import os
import shutil
import sqlite3
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

class f5_template(object):
 dtype = 'f5'
 cfgfiles = ['bigip_base.conf','bigip.conf','bigip_gtm.conf','bigip_user.conf'] 
 devpath = '/config/'
 allfiles = True
 def __init__(self, hostname, ipaddr):
  self.hostname = hostname
  self.ipaddr = ipaddr

class ciscoios_template(object):
 dtype = 'cisco_ios'
 cmdin = 'show running'
 cfgfiles = ['running-config']
 devpath = ''
 allfiles = False
 def __init__(self, hostname, ipaddr):
  self.hostname = hostname
  self.ipaddr = ipaddr

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
  net_connect = ConnectHandler(device_type=devicein.dtype, ip=devicein.ipaddr, username=baseuser, password=basepass, verbose=True, global_delay_factor=3)
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

def writeerror(ipaddress, error):
 errorfile = open('errors.txt', 'a')
 errorfile.write("%s: %s\n" % (ipaddress, error))
 errorfile.close()


conn = sqlite3.connect('hosts.db')
connc = conn.cursor()

for row in connc.execute('SELECT * FROM infrastructure'):
 hostname = str(row[0])
 ipaddr = str(row[1])
 dtype = str(row[2])
 destpath = "configs/%s" % hostname
 if not os.path.exists(destpath):
  os.makedirs(destpath)
 if "hpcomware" in dtype: 
  hpclass = hpcomware_template(hostname, ipaddr)
  scpresult = scp_func(hpclass,destpath)   
  if scpresult == False:
   connect_to_device(hpclass,destpath)
  if os.path.isfile('startup.cfg'):
   os.remove('startup.cfg')
  if os.path.isfile('config.cfg'):
   os.remove('config.cfg')
 elif "ciscoios" in dtype:
  ciscoclass = ciscoios_template(hostname, ipaddr)
  connect_to_device(ciscoclass,destpath)
  if os.path.isfile('running-config'):
   os.remove('running-config')
 elif "f5bigip" in dtype:
  f5class = f5_template(hostname, ipaddr)
  scp_func(f5class,destpath) 
  for f5files in f5class.cfgfiles:
   if os.path.isfile(f5files):
    os.remove(f5files)

conn.close()
