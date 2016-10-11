#!/usr/bin/python

import requests
import json
from netmiko import ConnectHandler
import getpass

myusername = raw_input('Please enter your username: ')
mypassword = getpass.getpass()

def ripepull(routefamily):
 index = 0
 payload = {'source': 'ripe', 'inverse-attribute': 'origin', 'type-filter': routefamily, 'query-string': 'AS49182'}
 try:
  r = requests.get('http://rest.db.ripe.net/search.json', params=payload)
  routejson = json.loads(r.text)
 except:
  print "API Call to the RIPE Database failed"
 for elements in routejson['objects']['object']:
  for those in elements['attributes']['attribute']:
   if "route" in those['name']:
    index += 10
    route = those['value']
    if routefamily=="route":
     family = "IPv4"
    elif routefamily=="route6":
     family = "IPv6"
    route = those['value']
    prefix_build(route, family, index)

def prefix_build(inroute, infamily, inindex):
 if infamily=="IPv4":
  v4routes.append(inroute)
  ipaddr = inroute.split('/')[0]
  prefixlen = inroute.split('/')[1]
  conf.append("ip prefix-list EGRESS index %s permit %s %s" % (inindex, ipaddr, prefixlen))
 if infamily=="IPv6":
  v6routes.append(inroute)
  ipaddr = inroute.split('/')[0]
  prefixlen = inroute.split('/')[1]
  conf.append("ipv6 prefix-list EGRESS index %s permit %s %s" % (inindex, ipaddr, prefixlen))
 
def hp_connect_to_device(dtype,dip,prefixlist,v4routelist,v6routelist):
 net_connect = ConnectHandler(device_type=dtype, ip=dip, username=myusername, password=mypassword)
 try: 
  net_connect.send_command("sys\n")
  for pfxlst in prefixlist:
   net_connect.send_command(pfxlst)
  net_connect.send_command('bgp 65000')
  net_connect.send_command('address-family ipv4 unicast')
  for routes in v4routelist:
   pfxip = routes.split('/')[0]
   pfxlen = routes.split('/')[1]
   net_connect.send_command('aggregate %s %s detail-suppressed' % (pfxip, pfxlen))
  net_connect.send_command('address-family ipv6 unicast')
  for routes in v6routelist:
   pfxip = routes.split('/')[0]
   pfxlen = routes.split('/')[1]
   net_connect.send_command('aggregate %s %s detail-suppressed' % (pfxip, pfxlen))
  net_connect.send_command('save f')
  net_connect.disconnect()
 except:
  print "Failed to connect to device"

def main():
 hosts = {'hp_comware': '192.168.253.30'}
 global conf
 conf = []
 global v4routes
 v4routes = []
 global v6routes
 v6routes = []
 ripepull("route")
 ripepull("route6")
 for them in hosts:
  if "hp_comware" in them: 
   dtype, dip = them, hosts[them]
   hp_connect_to_device(dtype,dip,conf,v4routes,v6routes)
  

if __name__ == "__main__":
 main()

