#! /usr/local/bin/python

import boto3
from datetime import datetime, date, time, timezone
import os

from pysnmp.hlapi import *

timestamp = datetime.now(timezone.utc)
today = date.today()

AWS_ACCESS_KEY="AKIATJKFXUWRQX2BV7H5"
AWS_SECRET_KEY="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"
BUCKET_NAME = "bacs01"
BUCKET_FOLDER = "snmp" + "/" + str(today) + "/" + timestamp.strftime("%H:%M") + "/"

def poll_oid(host, mib, oid):
    result = ""

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
        CommunityData("bridges"),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(mib, oid)),
        lookupMib=True,
        lexicographicMode=False):
        if errorIndication:
            print(errorIndication)
            raise Exception(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                result += varBind.prettyPrint() + "\r\n" 
        
    return result

def run(ip):
    result = ""
    result += poll_oid(ip, "SNMPv2-MIB", "system")
    result += poll_oid(ip, "IF-MIB", "ifTable")
    result += poll_oid(ip, "IF-MIB", "ifXTable")
    result += poll_oid(ip, "IP-MIB", "ipAddrTable")
    result += poll_oid(ip, "IP-MIB", "ipNetToMediaTable")
    return result

# def write_file(filename, results):
#     f = open(filename, "w")
#     f.writelines(results)
#     f.close()
#     return f

def post_to_s3(ip, results):
    filename = ip + ".txt"
    object_name = BUCKET_FOLDER + filename
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    s3.Object(BUCKET_NAME, object_name).put(Body=results)

# def remove_file(file):
#     if os.path.exists(file.name):
#         os.remove(file.name)

IPS = [
    "18.232.126.238",
    "52.91.222.247",
    "3.80.246.218",
    "54.196.68.253",
    "3.81.98.126",
    "34.230.24.94",
    "34.202.190.144",
    "18.210.213.130",
    "54.225.10.64"
]

try:
    for ip in IPS:
        results = run(ip)
        post_to_s3(ip, results)
except Exception as e:
    print(e)
    pass
