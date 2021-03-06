#!/usr/bin/env python

###########################################################
# Script: vos_create_dest_serv.py
# Author: John Vasconcelos
# Date: 10/21/2018
# Version 1.0
###########################################################

import requests
import json,yaml
import time
import uuid
import sys
import os
import vos


if not len(sys.argv) ==  2:
    print "Usage: vos_create_dest_serv.py <file_name> !!!"
    sys.exit(2)

channel_file = sys.argv[1]

creation_log = "dest_creation.txt"

f_log = open(creation_log,'w')

requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = raw_input("Enter the VOS RT Address:\n")

api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}

api_header_dest_post = {'Content-Type':'application/json' , 'Accept':'application/json'}

api_dest_url = "/vos-api/configure/v1/destinations"

api_serv_url = "/vos-api/configure/v1/services"

vos_session = vos.vos_get_session()

def get_dest_param(dname,dpubname,dprofid):

    dest_skell =  yaml.safe_load(u'{"id":"","type":"ORIGIN","labels":[],"name":"","outputs":[{"id":"","redundancyMode":"MANDATORY","rank":1,"outputType":"ORIGIN","ipSettings":null,"originSettings":{"originOutputEndPoints":[{"id":"","labels":null,"profileName":"NG","packagingProfileType":"e_DASH","originOutputProtocol":"HTTPS","hostname":"127.0.0.1","port":80,"path":"DASH","username":"","password":"******","outputMonitor":false,"hostnameForMonitoring":"","compatibilityMode":"STANDARD","playbackUrl":null,"drm":null,"publishName":null,"backup":null,"streamsPerTcpConnection":"ONE_STREAM","redundancyMode":"NONE","outputMode":null,"enableChunkedEncoding":true,"externalKeyPublishingSettings":null},{"id":"","labels":null,"profileName":"FPS","packagingProfileType":"e_HLS","originOutputProtocol":"HTTPS","hostname":"127.0.0.1","port":80,"path":"HLS","username":"","password":"******","outputMonitor":false,"hostnameForMonitoring":"","compatibilityMode":"STANDARD","playbackUrl":null,"drm":null,"publishName":null,"backup":null,"streamsPerTcpConnection":"ONE_STREAM","redundancyMode":"NONE","outputMode":null,"enableChunkedEncoding":true,"externalKeyPublishingSettings":null},{"id":"","labels":null,"profileName":null,"packagingProfileType":"e_INTERNAL","originOutputProtocol":"HTTPS","hostname":"127.0.0.1","port":80,"path":"INTERNAL","username":"","password":"******","outputMonitor":false,"hostnameForMonitoring":"","compatibilityMode":"STANDARD","playbackUrl":null,"drm":null,"publishName":"","backup":null,"streamsPerTcpConnection":"ONE_STREAM","redundancyMode":"NONE","outputMode":"LIVE_AND_TIMESHIFT","enableChunkedEncoding":true,"externalKeyPublishingSettings":null}],"ipNetworkAddress":null},"hspSettings":null}],"destinationProfileId":"","embeddedDestinationProfile":null,"embeddedManipulationProfiles":null,"poolAddon":null,"inUse":true}')

    destid = str(uuid.uuid4())

    dest_skell['id'] = destid
    dest_skell['name'] = dname
    dest_skell['destinationProfileId'] = dprofid
    dest_skell['outputs'][0]['id'] = str(uuid.uuid4())
    dest_skell['outputs'][0]['originSettings']['originOutputEndPoints'][0]['id'] = str(uuid.uuid4())
    dest_skell['outputs'][0]['originSettings']['originOutputEndPoints'][1]['id'] = str(uuid.uuid4())
    dest_skell['outputs'][0]['originSettings']['originOutputEndPoints'][2]['id'] = str(uuid.uuid4())
    dest_skell['outputs'][0]['originSettings']['originOutputEndPoints'][2]['publishName'] = dpubname

    dest_json = json.dumps(dest_skell)

    dest_ret = [dest_json,destid]

    return dest_ret


def get_serv_param(svname,svpn,srid,svprofid,did):

    serv_skell = yaml.safe_load(u'{"id":"","name":"","programNum":0,"serviceSources":[{"sourceId":"","rank":1}],"profileId":"","embeddedProfiles":null,\
                                "destinationId":"","destinationsId":[""],"timeShiftWindow":null,"addons":null,"controlState":"OFF","redundancyMode":"OFF","rank":0.0,\
                                "processingEngineVersion":null,"processingEngine":null,"enableRollingUpgrade":false,"version":null}')

    servid = str(uuid.uuid4())
    serv_skell['id'] = servid
    serv_skell['name'] = svname
    serv_skell['programNum'] = svpn
    serv_skell['serviceSources'][0]['sourceId'] = srid
    serv_skell['profileId'] = svprofid
    serv_skell['destinationId'] = did
    serv_skell['destinationsId'][0] = did

    serv_json = json.dumps(serv_skell)

    serv_ret = [serv_json,servid]

    return serv_ret

def create_dest(param):

    vos_dest_post = vos_session.post(api_proto+'://'+hostname+api_dest_url,headers=api_header_dest_post,data=param,verify=False)

    return vos_dest_post


def create_serv(param):

    vos_serv_post = vos_session.post(api_proto+'://'+hostname+api_serv_url,headers=api_header_serv_post,data=param,verify=False)

    return vos_serv_post

# If file Exists open it.
if os.path.isfile(channel_file):
    f_in = open(channel_file,"rb")
else:
    print "File %s Does not exist !" %channel_file
    sys.exit(2)


f_log.write(",".join(("Service Name","Service ID","Dest Name","Dest ID\n")))

for line in f_in:
    cfg_data = line.strip().split(",")

    sr_name = cfg_data[0]
    sr_id = cfg_data[1]
    d_name = cfg_data[2]
    d_pub_name = cfg_data[3]
    d_prof_id = cfg_data[4]
    sv_name = cfg_data[5]
    sv_prof_id = cfg_data[6]

    src_check = vos.vos_get_source_id(sr_id,hostname,vos_session)

    srcy = yaml.safe_load(src_check.text)
    sr_pn = srcy['inputs'][0]['ipSettingsList'][0]['programNum']


    dest_check = vos.vos_get_destination_name(d_name,hostname,vos_session)

    desty = yaml.safe_load(dest_check.text)

    dest_exist = False

    if desty:
        for item in desty:
            if item['name'] == d_name:
                print "Destination %s Already Exists and will not be created !\n" % d_name
                dest_exist = True
                dest_id = item['id']

    print dest_exist

    if not dest_exist:


        dest_info = get_dest_param(d_name,d_pub_name,d_prof_id)

        dest_param = dest_info[0]

        dest_id = dest_info[1]


        print "Creating Destination with the following Params: \n\n"

        print dest_param + "\n"

        print create_dest(dest_param)

        time.sleep(3)


    srv_check = vos.vos_get_service_name(sv_name,hostname,vos_session)

    srvy = yaml.safe_load(srv_check.text)

    srv_exist = False

    if srvy:
        for item in srvy:
            if item['name'] == sv_name:
                print "Service %s Already Exists and will not be created !\n" % sv_name
                srv_exist = True


    if not srv_exist:

        print "Creating Service with the following Params: \n\n"

        serv_info = get_serv_param(sv_name,sr_pn,sr_id,sv_prof_id,dest_id)

        serv_param = serv_info[0]

        print serv_param + "\n\n"

        print create_serv(serv_param)

        time.sleep(3)

        f_log.write(",".join((sv_name,serv_info[1],d_name,dest_id+"\n")))

f_in.close()

f_log.close()
