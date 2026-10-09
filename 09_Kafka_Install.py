import os
import shutil
import sys
import pwd
import subprocess as sp
import io
import re
import time
from pathlib import Path
import uuid

User = 'row64'

# Setup folder function
def SetupFolder( targetFolder ) :
    if os.path.isdir( targetFolder ) :
        print('Found ' + targetFolder)
    else :
        print('Creating ' + targetFolder)
        os.makedirs(targetFolder)
    print('  -- Applied chown for ' + User + '/' + User )
    shutil.chown( targetFolder, User, User )
    for fname in os.listdir(targetFolder):
        fPath = os.path.join( targetFolder, fname )
        shutil.chown( fPath, User, User )

def B58Encode(num):
    ALPHA = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    encoded: List[str] = []
    alpha_cnt: int = len(ALPHA)
    if num < 0:return ''
    while num >= alpha_cnt:
        mod = num % alpha_cnt
        num //= alpha_cnt
        encoded.append(ALPHA[mod])
    if num > 0:encoded.append(ALPHA[num])
    return ''.join(encoded[::-1])

def SetupJava():
    sp.call(["sudo","apt","update"])
    sp.call(["sudo","apt","install", "openjdk-17-jdk", "-y"])

def SetupLocalKafka():
    sp.call(["cd","~/Downloads"], shell=True)
    sp.call(["wget","-O","kafka_2.13-4.0.0.tgz","https://app.row64.com/DSetup/kafka_2.13-4.0.0.tgz"])
    sp.call(["sudo","tar","-xzf", "kafka_2.13-4.0.0.tgz"])
    sp.call(["sudo","mv","kafka_2.13-4.0.0", "/opt/kafka"])
    sp.call(["sudo","chown","-R", "row64:row64", "/opt/kafka"])
    randID = int(uuid.uuid4())
    clusterID = B58Encode(randID)
    print("New KAFKA_CLUSTER_ID: ",clusterID)
    sp.call(["/opt/kafka/bin/kafka-storage.sh","format","--standalone","-t",clusterID,"-c","/opt/kafka/config/server.properties"])
    
    sp.call(["sudo","chown","-R", "row64:row64", "/opt/kafka"])
    sp.call(["sudo","chmod","-R", "777", "/opt/kafka"])    

    SetupFolder("/tmp/kraft-combined-logs")
    sp.call(["sudo","chown","-R", "row64:row64", "/tmp/kraft-combined-logs"])
    sp.call(["sudo","chmod","-R", "777", "/tmp/kraft-combined-logs"])   


def SetupKafkaService():

    print("Configuring Kafka to start at boot")

    sStr = r"""#
# Localhost Kafka service For Row64 connector testing & demo
[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html
Wants=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=row64
Group=row64
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

    serviceDir = "/var/lib/kafka/share"
    Path(serviceDir).mkdir(parents=True, exist_ok=True)

    print("Created dir: ", serviceDir)

    serviceP = os.path.join(serviceDir, "kafka.service")

    print("serviceP: ", serviceP)

    textfile = open(serviceP, 'w')
    textfile.write(sStr)
    textfile.close()

    sp.call(["sudo","cp","/var/lib/kafka/share/kafka.service", "/etc/systemd/system/kafka.service"])
    
    sp.call(["sudo","systemctl","daemon-reload"])    
    sp.call(["sudo","systemctl","enable", "kafka"])  
    sp.call(["sudo","systemctl","start", "kafka"])  

def CreateTopics(inTList):

    print("Create Default Kafka Topics")
    for topic in inTList:
        print("   - Creating Topic: ",topic)
        sp.call(["/opt/kafka/bin/kafka-topics.sh","--create","--topic", topic, "--bootstrap-server", "localhost:9092"]) 
        sp.call(["/opt/kafka/bin/kafka-configs.sh","--bootstrap-server","localhost:9092","--entity-type","topics","--entity-name",topic,"--alter","--add-config","delete.retention.ms=60000"])


print("------------ Installing KAFKA ------------")

SetupJava()
SetupLocalKafka()
SetupKafkaService()