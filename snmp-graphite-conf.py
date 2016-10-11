#!/usr/bin/env python
# Stuart Howlette

# Import modules
import argparse
import os.path
import sys
import configparser
import jinja2


# Will print out Argparse help options out if no options are specified at the CLI
class MyParser(argparse.ArgumentParser):
 def error(self, message):
  sys.stderr.write('Error: %s\n' % message)
  self.print_help()
  sys.exit(2)

# Class to define VSX Firewalls and their required attributes
class vsx_fw(object):
 def __init__(self, fwname, vsxhost, vsid):
  self.fwname = fwname
  self.vsxhost = vsxhost
  self.vsid = vsid
 
 def getName(self):
  return self.fwname
 
 def getHost(self):
  return self.vsxhost
 
 def getVirtSys(self):
  return self.vsid

# Class to define the global configuration attributes for collectd (and potentially other processes)
class globalconfig(object):
 def __init__(self, carbonhost, carbonport, 
              carbonproto, loadplugins, 
              test1fw_ip, test2fwfw_ip, 
              snmpversion, snmpusername, 
              snmpsecuritylevel, snmpauthproto, 
              snmpprivproto, snmpauthpass, 
              snmpprivpass, statsdhost,
              statsdproto, statsdport):
  self.carbonhost = carbonhost
  self.carbonport = carbonport
  self.statsdhost = statsdhost
  self.statsdport = statsdport
  self.carbonproto = carbonproto
  self.statsdproto = statsdproto
  self.loadplugins = loadplugins
  self.test1fw_ip = test1fw_ip
  self.test2fwfw_ip = test2fwfw_ip
  self.snmpversion = snmpversion
  self.snmpusername = snmpusername
  self.snmpsecuritylevel = snmpsecuritylevel
  self.snmpauthproto = snmpauthproto
  self.snmpprivproto = snmpprivproto
  self.snmpauthpass = snmpauthpass
  self.snmpprivpass = snmpprivpass
 
 def getCarbHost(self):
  return self.carbonhost

 def getCarbPort(self):
  return self.carbonport
 
 def getCarbProto(self):
  return self.carbonproto

 def getStatsdHost(self):
  return self.statsdhost

 def getStatsdPort(self):
  return self.statsdport
 
 def getStatsdProto(self):
  return self.statsdproto

 def getPlugins(self):
  return self.loadplugins

 def getNewport(self):
  return self.test1fw_ip

 def getSlough(self):
  return self.test2fwfw_ip

 def getSNMPVer(self):
  return self.snmpversion
 
 def getSNMPUser(self):
  return self.snmpusername

 def getSNMPLev(self):
  return self.snmpsecuritylevel

 def getSNMPAuthPr(self):
  return self.snmpauthproto

 def getSNMPPrivPr(self):
  return self.snmpprivproto

 def getSNMPAuthPw(self):
  return self.snmpauthpass

 def getSNMPPrivPw(self):
  return self.snmpprivpass

# Create dictionaries to store Firewall objects and Global objects

firewall = {}
objectdict = {}

# Command line arguments, along with reference to MyParser class
parse = MyParser()
parse.add_argument('-i', '--inputfile', help='Input file in the format FWNAME VSXHOST VSID')
if len(sys.argv)==1:
 print "Error: No arguments supplied"
 parse.print_help()
 sys.exit(1)
args=parse.parse_args()

# Check that file provided actually exists, and provide a hint at how to build the file if it doesn't
if os.path.isfile(args.inputfile):
 openfile = open(args.inputfile, 'r')
else:
 print "Error: Input File provided does not exist"
 print "\nInput file must look like the following format: -"
 print "CMRFW01 TEST2FW 2"  
 print "CMRFW02 TEST1FW 5"
 sys.exit(1)


# Function to read from the settings.ini file, and assign attributes to variables based upon this
def cfg_read():
 Config = configparser.ConfigParser()
 Config.read("/opt/configbuild/settings.ini")
 carbonhost = Config.get('CARBON', 'carbonhost')
 carbonport = Config.get('CARBON', 'carbonport')
 carbonproto = Config.get('CARBON', 'carbonproto')
 statsdhost = Config.get('STATSD', 'statsdhost')
 statsdport = Config.get('STATSD', 'statsdport')
 statsdproto = Config.get('STATSD', 'statsdproto')
 loadplugins = Config.get('PLUGINS', 'loadplugins')
 test1fw_ip = Config.get('VSXHOSTS', 'test1fw_ip')
 test2fwfw_ip = Config.get('VSXHOSTS', 'test2fwfw_ip')
 snmpversion = Config.get('SNMP-SETTINGS', 'snmpversion')
 snmpusername = Config.get('SNMP-SETTINGS', 'snmpusername')
 snmpsecuritylevel = Config.get('SNMP-SETTINGS', 'snmpsecuritylevel')
 snmpauthproto = Config.get('SNMP-SETTINGS', 'snmpauthproto')
 snmpprivproto = Config.get('SNMP-SETTINGS', 'snmpprivproto')
 snmpauthpass = Config.get('SNMP-SETTINGS', 'snmpauthpass')
 snmpprivpass = Config.get('SNMP-SETTINGS', 'snmpprivpass')
 global configparams
 configparams = globalconfig(carbonhost, carbonport, 
			     carbonproto, loadplugins, 
                             test1fw_ip, test2fwfw_ip, 
                             snmpversion, snmpusername, 
			     snmpsecuritylevel, snmpauthproto, 
			     snmpprivproto, snmpauthpass, 
			     snmpprivpass, statsdhost,
                             statsdport, statsdproto)

# From the file specified, get the Name, VSX Host and Virtual System ID
# For each firewall, create an instance of the class vsx_fw, and save it in a dictionary
def cplist(inputfile):
 for each in inputfile:
  fwname, vsxhost, vsid = each.strip("\n").split(" ")[0:3]
  firewall[fwname] = vsx_fw(fwname, vsxhost, vsid)

# Run through Jinja SNMP template, using attributes assigned to objects
# Templates exist for SNMP hosts themselves, as well as collectd.conf
def jinja_snmp():
 for objects in firewall:
  templateLoader = jinja2.FileSystemLoader( searchpath="/" )
  templateEnv = jinja2.Environment( loader=templateLoader )
  TEMPLATE_FILE = "/opt/configbuild/jinja/snmp_host.jinja"
  template = templateEnv.get_template( TEMPLATE_FILE )
  if firewall[objects].getHost() == "TEST1FW":
   vsxhost_ip = configparams.getNewport()
  elif firewall[objects].getHost() == "TEST2FW":
   vsxhost_ip = configparams.getSlough()
  templateVars = {"fwname" : firewall[objects].getName() , 
       	  "vsid" : firewall[objects].getVirtSys(), 
       	  "vsxhost_ip" : vsxhost_ip, 
       	  "snmpversion" : configparams.getSNMPVer(), 
       	  "snmpusername" : configparams.getSNMPUser(),
       	  "snmpsecuritylevel" : configparams.getSNMPLev(),
       	  "snmpauthproto" : configparams.getSNMPAuthPr(),
       	  "snmpauthpass" : configparams.getSNMPAuthPw(),
       	  "snmpprivproto" : configparams.getSNMPPrivPr(),
       	  "snmpprivpass" : configparams.getSNMPPrivPw()
                }
  outputText = template.render( templateVars )
  print outputText
 print "</Plugin>\n<Include \"/etc/collectd/collectd.conf.d\">\n Filter \"*.conf\"\n</Include>"

# Non SNMP host collectd configuration
def jinja_run():
 templateLoader = jinja2.FileSystemLoader( searchpath="/" )
 templateEnv = jinja2.Environment( loader=templateLoader )
 TEMPLATE_FILE = "/opt/configbuild/jinja/globalconfig.jinja"
 template = templateEnv.get_template( TEMPLATE_FILE )
 templateVars = {"carbonhost" : configparams.getCarbHost() ,
		 "carbonport" : configparams.getCarbPort(),
		 "statsdport" : configparams.getStatsdPort(),
		 "statsdproto" : configparams.getStatsdProto(),
		 "statsdhost" : configparams.getStatsdHost(),
		 "carbonproto" : configparams.getCarbProto()
               }
 outputText = template.render( templateVars )
 print outputText 

# Run each function in order required to output the file
def main():
 Config = configparser.ConfigParser()  
 cplist(openfile) 
 cfg_read()
 jinja_run()
 jinja_snmp()

if __name__ == "__main__":
 main()
