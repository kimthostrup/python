#!/usr/bin/python

import sys
import netaddr
import uuid
import psycopg2

if len(sys.argv) > 1:
 inputfile = sys.argv[1]
 firewall = sys.argv[2]
 interface = sys.argv[2]
else:
 print "Please provide file to process, firewall name and interface: \n\neg. asa-parser.py file1 nicefirewall inside"


rulebase = open(inputfile, 'r')

def get_endpoints(eps):
 host, port = "any", "any"
 if eps[0] == "host":
  host = eps[1]
  eps = eps[2:]
 elif eps[0] == "any" or eps[0] =="any4": 
  eps = eps[1:]
 elif "object" in eps[0]:
  host = eps[1]
  eps = eps[2:] 
 else:
  host = str(netaddr.IPNetwork(eps[0] + "/" + eps[1]))
  eps = eps[2:]
 if eps and eps[0] == 'eq':
  port = eps[1]
  eps = eps[2:]
 elif eps and eps[0] == 'range':
  port = eps[1] + "-" + eps[2]
  eps = eps[3:]
 return host.strip("\n"), port.strip("\n"), eps

def database_insert():
 conn_string = "host='localhost' dbname='its' user='psycop' password='ies2oogaiZauPhoo'"
 conn = psycopg2.connect(conn_string)
 cursor = conn.cursor()
 cursor.execute("INSERT INTO mc1tier1 VALUES('" + str(uuid.uuid4()) + "','" + firewall  + "','" +  interface + "','" + aclName + "','" +  action + "','" +  protocol + "','" +  sourceIP + "','" + sourcePort + "','" + destIP + "','" + destPort + "');")
 conn.commit()
 conn.close()

def database_check():
 conn_string = "host='localhost' dbname='its' user='psycop' password='ies2oogaiZauPhoo'"
 conn = psycopg2.connect(conn_string)
 cursor = conn.cursor()
 cursor.execute("SELECT * FROM mc1tier1 WHERE aclname='" + aclName + "' AND action='" + action + "' AND proto='" + protocol + "' AND saddr='" + sourceIP + "' AND sports='" + sourcePort + "' AND daddr='" + destIP + "' AND dports='" + destPort + "';")
 records = cursor.fetchall()
 print records
 if len(records) < 1:
  print "Database insertion failed"

for eachline in rulebase.readlines():
 parts = eachline.split(" ")
 if "remark" in parts:
  continue
 else:
  _, aclName, _, action, protocol = parts[:5]
 endpoints = parts[5:]
 sourceIP, sourcePort, endpoints = get_endpoints(endpoints)
 destIP, destPort, endpoints = get_endpoints(endpoints)
 if sourceIP == "any" or sourceIP == "any4":
  sourceIP = "0.0.0.0/0"
 if destIP == "any" or destIP == "any4":
  destIP = "0.0.0.0/0"
 #print uuid.uuid4(), aclName, action, protocol, sourceIP, sourcePort, destIP, destPort
 database_insert()
 database_check()
