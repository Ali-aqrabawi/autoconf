from vlan_model import Vlan,Switch,Synchronizer
from switchs_config_file import Switchs_IPs ,Username , Password
import logging

from multiprocessing import Process

__name__ = "Vlan_AutoConf"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def userprompt():
    while True:


        x = input("Enter option\n" + "1. add vlan\n" + "2. view vlans\n" + "3. delete vlan\n" + "4. Synch vlans from switch\n"+ "0. Exit\n"+ " : ")

        try :
            assert int(x)
        except ValueError:
            print("please enter  a vlaid vlaue")
            return userprompt()

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

        elif int(x) == 4:
            list_of_switches_object = []
            for ip in Switchs_IPs:
                switch = Switch(ip, Username, Password)
                list_of_switches_object.append(switch)

            sync = Synchronizer(list_of_switches_object)
            sync.run()

        elif int(x) == 0 :
            exit(code=0)

        else:
            print("enter valid value please")
            print("##########################################################")


userprompt()
