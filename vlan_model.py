from sqlalchemy.orm import sessionmaker , relationship
from sqlalchemy import create_engine , Column , Integer , String , ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from switchs_config_file import Switchs_IPs ,Username , Password
import telnetlib
import time
import logging


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
        Session = sessionmaker(bind=engine)

        session = Session()
        session.add(self)
        session.commit()
        session.close()


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
            switch.connect_to_switch_telnet(ip)

            switch.add_vlan_to_switch(self)

    def deleteSelfFromSwitch(self):
        for ip in Switchs_IPs:
            switch = Switch(ip, Username, Password)
            switch.connect_to_switch_telnet(ip)

            switch.delete_vlan_vlan_switch(self)






class Switch:

    def __init__(self,Switchs_IPs,Username,Password):
        """Constructor.

        :param   Switchs_IPs: switches IP address
        :type    address: list of string
        :param  Username: telnet username
        :type   Username: string
        :param  Password: telnet Password
        :type       pass: string

        """
        self.Switchs_IPs = Switchs_IPs
        self.Username = Username
        self.Password = Password

    def connect_to_switch_telnet(self,ip):

        logger.info(' Start telnet connection to : %s', ip)
        conn = telnetlib.Telnet(ip)

        conn.read_until(b"Username: ")
        conn.write(Username.encode('ascii') + b"\n")
        conn.read_until(b"Password:")
        conn.write(Password.encode("ascii") + b"\n")

        conn.write(b"en\n")
        conn.read_until(b"Password:")
        conn.write(Password.encode('ascii') + b"\n")

        conn.write(b"terminal lenth 0\n")

        return conn



    def collect_switch_vlans(self):
        ##
        ## Return list of Vlan object of the vlans collected from the first switch in Switchs_IPs.
        ##considering all switches must have same vlan DB

        logger.info(' Start synching Vlans from : %s', Switchs_IPs[0])

        #collect the vlans in the first switch only to synch our DB
        conn = self.connect_to_switch_telnet(self,Switchs_IPs[0])

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
         logger.info(' adding Vlan to  : {}'.format(Switchs_IPs[0]))
         for ip in Switchs_IPs:
             conn = self.connect_to_switch_telnet(self,ip)

             conn.write(b"conf t\n")
             conn.write(b"vlan {}\n".format(Vlan.id))
             time.sleep(0.1)
             conn.write(b"name {}\n".format(Vlan.name))
             conn.write(b"exit\n")

    def delete_vlan_from_switch(self, Vlan):
        pass
