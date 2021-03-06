#!/usr/bin/env python

###########################################################
# Script: vos_dest_attach.py
# Author: John Vasconcelos
# Date: 04/25/2017
# Version 1.1
###########################################################

import requests
import json,yaml
import time
import sys
import vos


def check_dest_atached(did,dname):

    d_attached = False

    for svitem in sv:
        for i in svitem['destinationsId']:
            if  i == did:
                #print "Destination ID %s is already attached to Service %s\n" %(dname,svitem['name'])
                d_attached = True
    return d_attached




requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = raw_input("Enter the VOS RT Url:\n")

api_get_serv = "/vos-api/configure/v1/services"

api_get_dest = "/vos-api/configure/v1/destinations"

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}

api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}

api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}


vos_session = vos.vos_get_session()

vos_conn_test = vos_session.post(api_proto+'://'+hostname,verify=False)

if vos_conn_test.status_code != 200:
    print "Error Connecting to VOS: "
    print vos_conn_test
    sys.exit(2)

vos_serv_req = vos_session.get(api_proto+'://'+hostname+api_get_serv,headers=api_header_all,verify=False)

vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_header_json,verify=False)

sv = vos_serv_req.json()

d = vos_dest_req.json()

d_count = 0

for ditem in d:
    d_id = ditem['id']
    d_type = ditem['type']
    d_name = ditem['name']

    if not check_dest_atached(d_id,d_name):
        d_count += 1
        print "DESTID=%s DESTNAME=%s is not attached to any services!" %(d_id,d_name)
        print "\n"

print "\n %d Destinations Without Services !!" %d_count
