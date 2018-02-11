from vlan_model import Vlan,Switch,Synchronizer
from switchs_config_file import Switchs_IPs ,Username , Password
import paramiko
import logging
import threading
from threading import Thread

__name__ = "Vlan_AutoConf"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






def userprompt():
    while True:

        x = input("Enter option\n" + "1. add vlan\n" + "2. view vlans\n" + " : ")

        if int(x) == 1:
            id = input("enter vlan id : ")
            name = input("enter vlan name : ")
            description = input("enter vlan descriptoin : ")
            sessionVlan = Vlan()
            sessionVlan.id = id
            sessionVlan.name = name
            sessionVlan.description = description

            sessionVlan.AddVlan()
            print("##########################################################")

        elif int(x) == 2:
            sessionVlan = Vlan()

            sessionVlan.ViewVlans()
            print("##########################################################")

        elif int(x) == 3:
            sessionVlan = Vlan()


            sessionVlan.DeleteVlan('2')
            print("##########################################################")

        else:
            print("enter valid value please")
            print("##########################################################")


list_of_switches_object = []
for ip in Switchs_IPs :
    switch = Switch(ip,Username,Password)
    list_of_switches_object.append(switch)

sync = Synchronizer(list_of_switches_object)
Thread(target = sync.run()).start()
Thread(target = userprompt()).start()















