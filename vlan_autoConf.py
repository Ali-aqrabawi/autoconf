from vlan_model import Vlan
from switchs_config_file import Switchs_IPs ,Username , Password
import paramiko
import logging

__name__ = "Vlan_AutoConf"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def Collect_vlans() :
    logger.info(' Start synching Vlans from : %s',Switchs_IPs)

    for switch in Switchs_IPs :
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(ip, port=22, username=UN, password=PW)
        remote = conn.invoke_shell()








#conn = paramiko.SSHClient()
#conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#conn.connect(ip, port=22, username=UN, password=PW)
#remote = conn.invoke_shell()













Collect_vlans()
while True :


    x = input("Enter option\n" + "1. add vlan\n" + "2. view vlans\n" + " : ")

    if int(x) == 1 :
        id = input("enter vlan id : ")
        name = input("enter vlan name : ")
        description = input("enter vlan descriptoin : ")
        sessionVlan = Vlan()
        sessionVlan.id = id
        sessionVlan.name = name
        sessionVlan.description = description

        sessionVlan.AddVlan()
        print("##########################################################")

    elif int(x) == 2 :
        sessionVlan = Vlan()

        sessionVlan.ViewVlans()
        print("##########################################################")

    else :
        print("enter valid value please")
        print("##########################################################")
