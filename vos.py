#!/usr/bin/env python

"""
###########################################################
# Script: vos.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC. 
#       USE IT AT YOUR OWN RISK !!!!
#
# PLEASE DO NOT MODIFY THIS SCRIPT ! FOR ANY NEW FEATURES
# OR ISSUES PLEASE SEND A MESSAGE TO: 
# John Vasconcelos @ john.vasconcelos@harmonicinc.com
#
# Author: John Vasconcelos
# Date: 08/25/2017
# Version 1.3
# Tested with VOS Build 1.3.3.X
###########################################################
"""

import requests
import json
import yaml
import getpass
import subprocess
import sys
import argparse
import uuid
import re
import datetime
import urllib
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def log_write(l_type,l_msg,l_file):

    log_file = open(l_file,'a')

    print l_msg + '\n'
    
    now = datetime.datetime.now()
    
    t_now = now.strftime("%m-%d-%Y %H:%M:%S - ")

    log_file.write(t_now + l_type + ' - ' + l_msg + '\n')

    log_file.close()


def check_request(code,uri=""):
    
    if not code == 200: 
        print "Error on Request: " + uri 
        print "Exited with HTTP CODE: " + str(code)
        sys.exit(2)

def api_request(req_method,uri,header,session="",param=""):
    """This function is used to perform API requests and return the full requests object

    Args:
        method - can be get,post,put,delete
        uri - the API url to be used
        header - The header to be used
        session - session to be used for the request. Default is " which will request"
        param - Parameters for post and put methods.

    Returns:
        req - Function returns the full response of the Request object
    """
    req =""

    if req_method == "get":
        try:
            req = session.get(uri,headers=header,verify=False)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
    elif req_method == "post":
        try:
            req = session.post(uri,headers=header,data=param,verify=False)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
    elif req_method == "put":
        try:
            req = session.put(uri,headers=header,data=param,verify=False)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
    elif req_method == "delete":
        try:
            req = session.delete(uri,headers=header,verify=False)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
    else:
        print "Method %s is not a valid method please use: get,post,put,or delete!" %method

    return req            


def vos_get_session(user="",passwd=""):
    
    if not user:
        user = raw_input("Enter the Username for VOS:\n")
    
    if not passwd:    
        passwd = getpass.getpass("Enter the Password:\n")

    vos_session = requests.Session()
    vos_session.auth = (user,passwd)

    return vos_session    

def is_valid_uuid(uuidtocheck):
    
    UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

    if UUID_PATTERN.match(uuidtocheck):
        return True
    else:
        return False


def mesos_get_agents(mmaster,api_proto="http",port="5050"):
  
    req_uri = api_proto+'://'+mmaster+':'+port+'/api/v1'

    curlm = "curl -v --header \"Content-Type\":\"application/json\" --header \"Accept\":\"application/json\" -X POST -d '{\"type\":\"GET_AGENTS\"}' " + req_uri

    curl_get_agents = subprocess.Popen(curlm, stdout=subprocess.PIPE, shell=True)
    
    (output,err) = curl_get_agents.communicate()

    vos_agents = json.loads(output)

    return vos_agents['get_agents']['agents']


def mesos_get_tasks(mmaster,api_proto="http",port="5050"):
  
    req_uri = api_proto+'://'+mmaster+':'+port+'/api/v1'

    curlm = "curl -v --header \"Content-Type\":\"application/json\" --header \"Accept\":\"application/json\" -X POST -d '{\"type\":\"GET_TASKS\"}' " + req_uri

    curl_get_tasks = subprocess.Popen(curlm, stdout=subprocess.PIPE, shell=True)
    
    (output,err) = curl_get_tasks.communicate()

    vos_tasks = json.loads(output)

    return vos_tasks['get_tasks']['tasks']


def mesos_get_agent_name(agents,agentid):
    
    agentname = ""
    for agent in agents:
        if agent['agent_info']['id']['value'] == agentid:
            agentname = agent['agent_info']['hostname']

    return agentname


def vos_get_provision(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/configure/v1/provision"    
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get_serv

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req.json()


def vos_get_notifications(state,result_count,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    if not state:
        api_url = "/vos-api/notification/v1/notifications?result_count=" + str(result_count)
    else:
        api_url = "/vos-api/notification/v1/notifications?state=%s&result_count=%s" %(state,result_count)

    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_url

    req = api_request("get",uri,api_header,session)
    
    #Checks if the Request was successful
    if req:
        if not (req.status_code == 200 or req.status_code == 403): 
            print "Error on Request: " + uri 
            print "Exited with HTTP CODE: " + str(req.status_code)
    
        if req.status_code == 403:
            print "Authentication failed for: " + uri

    return req


def vos_get_image_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/configure/v1/images"    
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_add_image(param,vosrt,session="",proto="https"):
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/images"

    ret = session.post(uri,headers=api_header,data=param,verify=False)

    new_img = ret.json()

    if ret.status_code == 200:

        print "Image URL %s with ID %s created with the following Params:\n" %(new_img['url'] , new_img['id'])
        print param
        print "\n"

    else:
        print "Error creating service with Error: %s" %ret
    
    return ret 


def vos_get_source_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/configure/v1/sources"    
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_get_source_name(srcname,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    srcname = urllib.quote_plus(srcname)
    api_get = "/vos-api/configure/v1/sources"+"?name="+srcname    
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_get_source_id(srcid,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/configure/v1/sources/"+ srcid  
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_source_delete(srcid,vosrt,session="",proto="https"):
  
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/sources/" + srcid

    ret = session.delete(uri,headers=api_header,verify=False)

    print "Deleting Source ID: %s \n" %srcid
    
    return ret  

def vos_get_drmsys_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/scrambling/v1/drm/systems"     
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req


def vos_get_drm_settings(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/scrambling/v1/drm/settings"     
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req


def vos_mod_drm_settings(param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header_put = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/scrambling/v1/drm/settings"

    ret = session.put(uri,headers=api_header_put,data=param,verify=False)


    return ret


def vos_get_drmsys_id(drmid,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/scrambling/v1/drm/systems/" + drmid     
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    if req.status_code == 404:
        print "DRM System with ID:%s was not found." %drmid
    else:
        #Checks if the Request was successful
        check_request(req.status_code,uri)    

    return req

def vos_drmsys_add(param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/scrambling/v1/drm/systems"

    ret = session.post(uri,headers=api_header,data=param,verify=False)

    new_srv = ret.json()

    if ret.status_code == 200:

        print "Service %s with ID %s created with the following Params:\n" %(new_srv['name'] , new_srv['id'])
        print param
        print "\n"

    else:
        print "Error creating Service with Error: %s" %ret
    
    return ret 

def vos_mod_drm_system(drmid,param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/scrambling/v1/drm/systems/" + drmid

    ret = session.put(uri,headers=api_header,data=param,verify=False)


    if ret.status_code == 200:

        print "DRM System with ID %s changed with the following Params:\n" %drmid
        print param
        print "\n"

    else:
        print "Error Changing DRM System with Error: %s" %ret
    
    return ret


def vos_get_user_name(usrname,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()
    
    usrname = urllib.quote_plus(usrname)
    api_get = "/vos-api/user/v1/users" + '?username=' + usrname
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)
    
    return req

def vos_get_user_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/user/v1/users"
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)
    
    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_add_user(param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/user/v1/users"

    ret = session.post(uri,headers=api_header,data=param,verify=False)

    new_user = ret.json()

    if ret.status_code == 200:

        print "User %s with username %s created with the following Params:\n" %(new_user['name'] , new_user['username'])
        print param
        print "\n"

    else:
        print "Error creating User with Error: %s" %ret
    
    return ret

def vos_get_destination_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/configure/v1/destinations"    
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req


def vos_get_destination_name(dstname,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    dstname = urllib.quote_plus(dstname)
    api_get = "/vos-api/configure/v1/destinations"+"?name="+dstname    
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_get_destination_id(dstid,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/configure/v1/destinations/"+ dstid  
    
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_add_destination(param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/destinations"

    ret = session.post(uri,headers=api_header,data=param,verify=False)

    new_dest = ret.json()

    if ret.status_code == 200:

        print "Destination %s with ID %s created with the following Params:\n" %(new_dest['name'] , new_dest['id'])
        print param
        print "\n"

    else:
        print "Error creating Destination with Error: %s" %ret
    
    return ret

def vos_destination_delete(dstid,vosrt,session="",proto="https"):
  
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/destinations/" + dstid

    ret = session.delete(uri,headers=api_header,verify=False)

    print "Deleting Destination ID: %s \n" %dstid
    
    return ret  

def vos_get_service_id(servid,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get_serv = "/vos-api/configure/v1/services/" + servid
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get_serv

    req = session.get(uri,headers=api_header,verify=False)
    
    #Checks if the Request was successful
    #check_request(req.status_code,uri)

    return req


def vos_get_service_name(servname,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    servname = urllib.quote_plus(servname)
    api_get_serv = "/vos-api/configure/v1/services" + '?serviceName=' + servname
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get_serv

    req = session.get(uri,headers=api_header,verify=False)
    
    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_get_service_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get_serv = "/vos-api/configure/v1/services"
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get_serv

    req = session.get(uri,headers=api_header,verify=False)
    
    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req


def vos_mod_service(servid,param,vosrt,session="",proto="https",upgrade=False):
    
    if not session:
        session = vos_get_session()

    api_header_put = {'Content-Type':'application/json' , 'Accept':'*/*'}

    if upgrade:
        uri = proto+'://'+vosrt+"/vos-api/configure/v1/services/" + servid + "?upgradeToLatestEngine=true"
    else:
        uri = proto+'://'+vosrt+"/vos-api/configure/v1/services/" + servid

    ret = session.put(uri,headers=api_header_put,data=param,verify=False)

    print "Changing service %s with the following Params:\n" %servid
    
    print param 

    print "\n"

    return ret

def vos_service_delete(servid,vosrt,session="",proto="https"):
  
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/services/" + servid + "?force=True"

    ret = session.delete(uri,headers=api_header,verify=False)

    print "Deleting service ID: %s \n" %servid
    
    return ret      

def vos_service_add(param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/services"

    ret = session.post(uri,headers=api_header,data=param,verify=False)

    new_srv = ret.json()

    if ret.status_code == 200:

        print "Service %s with ID %s created with the following Params:\n" %(new_srv['name'] , new_srv['id'])
        print param
        print "\n"

    else:
        print "Error creating Service with Error: %s" %ret
    
    return ret 

def vos_add_source(param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/sources"

    ret = session.post(uri,headers=api_header,data=param,verify=False)

    new_source = ret.json()

    if ret.status_code == 200:

        print "Source %s with ID %s created with the following Params:\n" %(new_source['name'] , new_source['id'])
        print param
        print "\n"

    else:
        print "Error creating Source with Error: %s" %ret
    
    return ret


def vos_mod_source(srcid,param,vosrt,session="",proto="https"):
    
    if not session:
        session = vos_get_session()

    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

    uri = proto+'://'+vosrt+"/vos-api/configure/v1/sources/" + srcid

    ret = session.put(uri,headers=api_header,data=param,verify=False)

    new_source = ret.json()

    if ret.status_code == 200:

        print "Source %s with ID %s changed with the following Params:\n" %(new_source['name'] , new_source['id'])
        print param
        print "\n"

    else:
        print "Error creating service with Error: %s" %ret
    
    return ret


def vos_service_offline(service,vosrt,session="",proto="https"):
  
    if not session:
        session = vos_get_session()

    if is_valid_uuid(service):
        srv_get = vos_get_service_id(service,vosrt,session)
    else:
        srv_get = vos_get_service_name(service,vosrt,session)
       
    srv_mod = yaml.safe_load(srv_get.text)

    srv_mod[0]['controlState'] = "OFF"

    param = json.dumps(srv_mod[0])

    ret = vos_mod_service(srv_mod[0]['id'],param,vosrt,session)

    return ret


def vos_service_online(service,vosrt,session="",proto="https",upgrade=False):
  
    if not session:
        session = vos_get_session()

    if is_valid_uuid(service):
        srv_get = vos_get_service_id(service,vosrt,session)
    else:
        srv_get = vos_get_service_name(service,vosrt,session)
       
    srv_mod = yaml.safe_load(srv_get.text)

    srv_mod[0]['controlState'] = "ACTIVATED"

    param = json.dumps(srv_mod[0])

    ret = vos_mod_service(srv_mod[0]['id'],param,vosrt,session,proto,upgrade)

    return ret


def vos_get_clgrp_id_from_name(clname,vosrt,session="",proto="https"):

    cl_grp_id = ""
    
    cl_list = vos_get_cl_list(vosrt,session,proto)

    for cl in cl_list:
        if clname == cl['clname']:
            cl_grp_id = cl['clgroup']

    return cl_grp_id


def vos_get_cl_list(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get_cl = "/vos-api/uplink-hub/v1/uplinks"
    api_get_clgroup = "/vos-api/uplink-hub/v1/uplinkGroups"
    api_get_stat = "/vos-api/uplink-hub/v1/uplinkStatus"
    api_header = {'user-agent':'Accept:application/json'}

    uri_cl = proto+'://'+vosrt+api_get_cl

    uri_clgrp = proto+'://'+vosrt+api_get_clgroup

    uri_stat = proto+'://'+vosrt+api_get_stat

    req_cl = api_request("get",uri_cl,api_header,session)

    req_clgrp = api_request("get",uri_clgrp,api_header,session)

    req_stat = api_request("get",uri_stat,api_header,session)

    cl_list = []
    
    #Checks if the Request was successful
    check_request(req_cl.status_code,uri_cl)

    check_request(req_stat.status_code,uri_stat)

    for cl in req_cl.json():

        clid = cl['id']
        clname = cl['name']
        clip = cl['ipAddress']
        clgrpid = ""
        clstate = ""
        clrate = ""

        for stat in req_stat.json():
            if clid == stat['id']:
                clstate = stat['uplinkState']
                if not clstate == "LOST":
                    clrate = stat['uplinkStatistic']['uplinkOutputStatisticList']

        for clgrp in req_clgrp.json():
            if clid == clgrp['uplinkIds'][0]:
                clgrpid = clgrp['id']

        cl_list.append({'clgroup':clgrpid , 'clid':clid , 'clname':clname , 'clip':clip , 'clstate':clstate , 'clrate':clrate})


    return cl_list

#Returns List of Services Running on Ingest Nodes
def get_ingest_services(tasks,agents):

    in_services = []

    for task in tasks:

        tname = task['name']
        ahostname = ""

        if "stream-processing-" in tname:
            agentid = task['agent_id']['value']
            agentip = task['statuses'][0]['container_status']['network_infos'][0]['ip_addresses'][0]['ip_address']

            # Get Service Name without trailing information.
            tname_s = tname.split("stream-processing-")
            servname = tname_s[1][:-2]

            ahostname = mesos_get_agent_name(agents,agentid)

            in_services.append({'node':ahostname , 'nodeip':agentip , 'nodeid':agentid , 'service':servname})
    return in_services

#Returns List of Nodes Running LIO
def get_egress_lio_tasks(tasks,agents,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_get = "/vos-api/live-ingest-origin/v1/origin-tasks"
    api_header = {'user-agent':'Accept: */*'}

    uri = proto+'://'+vosrt+api_get

    req = session.get(uri,headers=api_header,verify=False)
    
    #Checks if the Request was successful
    
    check_request(req.status_code,uri)

    lio_nodes = []

    for lio in req.json():

        taskid = lio['originTaskId']
        taskname = lio['originTaskName']
        liopoints = lio['numAssociatedIngestPoints']
        usedstormb = lio['usedStorageInMB']
        groupid = lio['groupId']
        noderole = "Primary" if lio['groupMemberIndex'] == 0 else "Backup"
        originstate = lio['state']
        agentip = ""
        ahostname = ""

        for task in tasks:
            if taskid in task['name']:
                agentid = task['agent_id']['value']
                agentip = task['statuses'][0]['container_status']['network_infos'][0]['ip_addresses'][0]['ip_address']
    
                ahostname = mesos_get_agent_name(agents,agentid)
    
        lio_nodes.append({'node':ahostname , 'nodeip':agentip , 'groupid':groupid, 'noderole':noderole ,'liopoints': liopoints , 'state':originstate})

    return lio_nodes

#Returns List of Nodes Running MDS
def get_egress_mds_tasks(tasks,agents):

    mds_tasks = []

    for task in tasks:

        tname = task['name']
        ahostname = ""

        if "origin-engine.media-delivery-server" in tname:
            agentid = task['agent_id']['value']
            agentip = task['statuses'][0]['container_status']['network_infos'][0]['ip_addresses'][0]['ip_address']

            ahostname = mesos_get_agent_name(agents,agentid)

            mds_tasks.append({'node':ahostname , 'nodeip':agentip , 'Type':"UOE", 'TaskName':tname})
           
    return mds_tasks

def vos_get_live_ingest(tasks,agents,vosrt,session="",proto="https"):
     
    api_get_ingest_point = "/vos-api/live-ingest-origin/v1/ingest-point"
    api_header = {'user-agent':'Accept: */*'}
    uri = proto+'://'+vosrt+api_get_ingest_point
    
    #List of Dictionaries containing the lio Info
    # Dict = {'servname':lio_servname , 'servid':lio_servid , 'package':lio_pkge , 'node':lio_node , 'nodeip':lio_nodeip , 'state':lio_state}
    lio_info = [] 
    if not session:
        session = vos_get_session()

    resp_get_ingest = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(resp_get_ingest.status_code,uri)

    for lio in resp_get_ingest.json():
        
        lio_desc = lio['description'].split(":")
        lio_id = lio['id']     
        lio_nodeip = ""
        lio_node = ""
        lio_state = ""

        #Retrieve Service ID 
        lio_servid = lio_desc[1].strip().split(",")[0]
        lio_pkge =  lio_desc[2].strip()       

        serv = vos_get_service_id(lio_servid,vosrt,session,proto)
        
        if serv.status_code == 200:

            lio_servname = serv.json()['name']
    
            for endpoint in lio['endPoints']:
                lio_state = endpoint['state']
                for task in tasks:
                    if task['name'] == "live-ingest-origin-task-" + endpoint['hostUuid']:
                        lio_nodeip = task['statuses'][0]['container_status']['network_infos'][0]['ip_addresses'][0]['ip_address']
                        lio_node = mesos_get_agent_name(agents,task['agent_id']['value'])
                lio_info.append({'servname':lio_servname , 'servid':lio_servid , 'lioid':lio_id ,'package':lio_pkge , 'node':lio_node , 'nodeip':lio_nodeip , 'state':lio_state})     
        else:
            print serv.text

    return lio_info


# List of FIPs used for a specific CL
def get_fip_ip(session,clip,proto="https"):
    '''
    Usage: get_fip_ip(session,clip,proto="https")
    '''

    api_header = {'user-agent':'Accept: */*'}
    api_get_feederTask = "/vos-api/uplink/v1/feederTask"
    uri = proto+'://'+clip+api_get_feederTask

    resp = session.get(uri,headers=api_header,verify=False)

    #Checks if the Request was successful
    check_request(resp.status_code,uri)

    fip_list = []
    
    for fip in resp.json():
        
        fip_list.append(fip['outputAddress'])        

    return fip_list

def vos_get_dest_all(vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_url = "/vos-api/configure/v1/destinations"
    api_header = {'user-agent':'Accept:application/json'}

    uri = proto+'://'+vosrt+api_url

    req = api_request("get",uri,api_header,session)
    
    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req

def vos_get_dest_id(did,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_url = "/vos-api/configure/v1/destinations/" + did
    api_header = {'user-agent':'Accept:application/json'}

    uri = proto+'://'+vosrt+api_url

    req = api_request("get",uri,api_header,session)
    
    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req


def vos_mod_dest(did,param,vosrt,session="",proto="https"):

    if not session:
        session = vos_get_session()

    api_url = "/vos-api/configure/v1/destinations/" + did
    api_header = {'Content-Type':'application/json' , 'Accept':'application/json'}

    uri = proto+'://'+vosrt+api_url

    req = api_request("put",uri,api_header,session,param)
    
    #Checks if the Request was successful
    check_request(req.status_code,uri)

    return req