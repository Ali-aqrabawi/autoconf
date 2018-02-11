from vlan_model import Vlan,Switch,Synchronizer
from switchs_config_file import Switchs_IPs ,Username , Password
import sys, select
import logging

from multiprocessing import Process

__name__ = "Vlan_AutoConf"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def userprompt():
    while True:


        x = input("Enter option\n" + "1. add vlan\n" + "2. view vlans\n" + "3. delete vlan\n" + "0. Exit\n"+ " : ")


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
            sessionVlan.ViewVlans()
            id = input("enter vlan id you want to delete : ")
            sessionVlan.DeleteVlan(id)
            print("##########################################################")

        elif int(x) == 0 :
            exit(code=0)

        else:
            print("enter valid value please")
            print("##########################################################")


#conn = paramiko.SSHClient()
#conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#conn.connect(ip, port=22, username=UN, password=PW)
#remote = conn.invoke_shell()


list_of_switches_object = []
for ip in Switchs_IPs :
    switch = Switch(ip,Username,Password)
    list_of_switches_object.append(switch)

sync = Synchronizer(list_of_switches_object)

p1 = Process(target=userprompt())
p1.start()
p2 = Process(target=sync.run())
p2.start()
p1.join()
p2.join()
