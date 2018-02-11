from sqlalchemy.orm import sessionmaker , relationship
from sqlalchemy import create_engine , Column , Integer , String , ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from switchs_config_file import Switchs_IPs ,Username , Password
import telnetlib
import time
import logging
import socket

__name__ = "Vlan_Model"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base = declarative_base()
engine = create_engine('sqlite:///vlan.db', echo = True)
base.metadata.create_all(bind = engine)
import paramiko


class Vlan(base):


    __tablename__ = "vlan"

    id = Column('id',Integer,primary_key=True)
    name = Column('name', String)
    description = Column('description' , String)
    engine = create_engine('sqlite:///vlan.db', echo=True)

    def __init__(self,id=None,name=None,descriptoin=None):
        """Constructor.

        :param   id: vlan ID
        :type    id: string
        :param  name: vlan name
        :type   name : string
        :param  description: vlan description
        :type   desc : string

        """
        self.id = id
        self.name = name
        self.description = descriptoin
    def AddVlan(self):
        logger.info('adding vlan to database')
        Session = sessionmaker(bind=engine)

        session = Session()
        session.add(self)
        session.commit()
        session.close()
        logger.info('adding vlan to switches')
        for ip in Switchs_IPs:
            swicth = Switch(ip,Username,Password)

            swicth.add_vlan_to_switch(self)

    def DeleteVlan(self):
        Session = sessionmaker(bind=engine)

        session = Session()
        session.query(Vlan).filter(Vlan.id==self.id).delete()
        session.commit()
        session.close()
        logger.info('deleting vlan from switches')
        for ip in Switchs_IPs:
            swicth = Switch(ip, Username, Password)

            swicth.delete_vlan_from_switch(self)

    def get_vlans(self):
        Session = sessionmaker(bind=engine)

        session = Session()
        all = session.query(Vlan).all()
        if len(all) == 0:
            print("no vlans")
            session.close()
            return
        session.close()
        return all



    def ViewVlans(self):
        Session = sessionmaker(bind=engine)

        session = Session()
        all = session.query(Vlan).all()


        if len(all) == 0 :
            print("no vlans")
            return
        for i in all :

            print(i.id)
            print(i.name)
            print(i.description)
        session.close()

    def AddSelfToSwitches(self):

        for ip in Switchs_IPs:
            switch = Switch(ip,Username,Password)
            switch.add_vlan_to_switch(self)

    def deleteSelfFromSwitch(self):
        for ip in Switchs_IPs:
            switch = Switch(ip, Username, Password)
            switch.delete_vlan_vlan_switch(self)




def vlans_obj_comparing(db_vlans,vlans):
    switch_vlanID = []
    switch_vlanID_dict = {}
    db_vlanID = []
    for vlan in vlans:
        switch_vlanID_dict.update({vlan.id: vlan.name})
        switch_vlanID.append(vlan.id)
    for vlan in db_vlans:
        db_vlanID.append(vlan.id)

    set_new_vlan = set(switch_vlanID) ^ set(db_vlanID)

    return set_new_vlan,switch_vlanID_dict




class Switch:

    def __init__(self,ip,Username,Password):
        """Constructor.

        :param   Switchs_IPs: switches IP address
        :type    address: list of string
        :param  Username: telnet username
        :type   Username: string
        :param  Password: telnet Password
        :type       pass: string

        """
        self.ip = ip
        self.Username = Username
        self.Password = Password

    def connect_to_switch_telnet(self):

        logger.info(' Start telnet connection to : %s', self.ip)
        try:
            conn = telnetlib.Telnet(self.ip, 23, 2)
        except socket.timeout:
            print("connection time out caught.")


        conn.read_until(b"Username: ")
        conn.write(Username.encode('ascii') + b"\n")
        conn.read_until(b"Password:")
        conn.write(Password.encode("ascii") + b"\n")

        conn.write(b"en\n")
        conn.read_until(b"Password:")
        conn.write(Password.encode('ascii') + b"\n")

        conn.write(b"terminal lenth 0\n")

        return conn



    def collect_switch_vlans(self,):
        ##
        ## Return list of Vlan object of the vlans collected from the first switch in Switchs_IPs.
        ##considering all switches must have same vlan DB

        logger.info(' Start synching Vlans from : %s', Switchs_IPs[0])

        #collect the vlans in the first switch only to synch our DB
        conn = self.connect_to_switch_telnet()

        conn.write(b"show vlan | in active\n")
        conn.write(b"exit\n")

        output = conn.read_all().decode('ascii')
        output = output.splitlines()

        vlans = []

        for line in output :
            vlan = {}
            if 'active' in line and 'show vlan' not in line :
                line = line.split()
                vlan = {'id' : line[0],'name':line[1]}
                vlans.append(vlan)

        if vlans:
            logger.info(' collected vlans : %s', vlans)
            vlan_list_object = []
            for dict in vlans:
                vlanObj = Vlan(dict['id'], dict['name'], 'na')
                vlan_list_object.append(vlanObj)
                return vlan_list_object

        else :
            logger.info(' no Vlans were colleced from : %s', Switchs_IPs[0])


        return



    def add_vlan_to_switch(self,Vlan):
         logger.info(' adding Vlan to  : {}'.format(self.ip))

         conn = self.connect_to_switch_telnet()

         conn.write(b"conf t\n")
         conn.write(b"vlan {}\n".format(Vlan.id))
         time.sleep(0.1)
         conn.write(b"name {}\n".format(Vlan.name))
         conn.write(b"exit\n")

    def delete_vlan_from_switch(self, Vlan):
        logger.info(' deleting Vlan from  : {}'.format(Switchs_IPs[0]))
        for ip in Switchs_IPs:
            conn = self.connect_to_switch_telnet(self, ip)
            conn.write(b"conf t\n")
            conn.write(b"no vlan {}\n".format(Vlan.id))
            conn.write(b"exit\n")




class Synchronizer :

    switches = []
    def __init__(self,switches):
        """Constructor.

                :param   Switchs: list of switches
                :type    address: list of Switch object
                """

        self.switches = switches

    def run(self):

        for switch in self.switches :

            list_of_vlans = switch.collect_switch_vlans()

            for vlan in list_of_vlans :
                vlan.AddVlan()


        while True :
            logger.info(' checking if there is update on switches')
            db_vlans = Vlan()
            db_vlans = db_vlans.get_vlans()
            for switch in Switchs_IPs:

                vlans = switch.collect_switch_vlans()
                if len(db_vlans) < len(vlans):
                    logger.info(' vlan added on switch {} , adding corresponding vlan to DB'.format(switch.ip))
                    set_new_vlan,switch_vlanID_dict = vlans_obj_comparing(db_vlans, vlans)
                    for new in set_new_vlan:
                        new_vlan = Vlan(id=new, name=switch_vlanID_dict[new])
                        new_vlan.AddVlan()

                if len(db_vlans) > len(vlans):
                    logger.info(' vlan deleted from switch {} , deleting corresponding vlan from DB'.format(switch.ip))
                    set_deleted_vlan,switch_vlanID_dict = vlans_obj_comparing(db_vlans, vlans)
                    for deleted in set_deleted_vlan:
                        deleted_vlan = Vlan(id=deleted, name=switch_vlanID_dict[deleted])
                        deleted_vlan.DeleteVlan()


