from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine , Column , Integer , String ,exc ,update
from sqlalchemy.ext.declarative import declarative_base
from switchs_config_file import Switchs_IPs ,Username , Password,en_pass
from prettytable import PrettyTable
import telnetlib
import time
import logging
import socket

__name__ = "Vlan_Model"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



base = declarative_base()
engine = create_engine('sqlite:///vlan.db')
base.metadata.create_all(bind = engine)



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
        logger.debug('Vlan.AddVlan : adding vlan %s to database',self.id)
        Session = sessionmaker(bind=engine)

        session = Session()
        try :
            session.add(self)
            session.flush()

        except exc.IntegrityError:
            logger.debug('vlan already exist in the DB , VLANid is : %s', self.id)
            session.rollback()
        session.commit()

        logger.debug('Vlan.AddVlan :start adding vlan to swicthes process..')

        for ip in Switchs_IPs:
            swicth = Switch(ip,Username,Password)

            swicth.add_vlan_to_switch(self)
        session.close()

    def AddVlan_collected_from_switch(self):
        logger.debug('Vlan.AddVlan_collected_from_switch : adding vlan to database vlan id : %s', self.id)
        Session = sessionmaker(bind=engine)

        session = Session()
        try:
            session.add(self)
            session.flush()

        except exc.IntegrityError:
            logger.debug('vlan %s already exist in the DB', self.id)
            session.rollback()

        session.commit()



        session.close()

    @staticmethod
    def DeleteVlan_after_syncing_from_switch(list_of_vlan_collected_from_switch):
        logger.debug('Vlan.DeleteVlan_after_syncing_from_switch : deleting vlans from database if they were deleted from the switch')
        Session = sessionmaker(bind=engine)
        session = Session()
        ids_to_keep = []
        for vlan in list_of_vlan_collected_from_switch :


            ids_to_keep.append(vlan.id)

        session.query(Vlan).filter(~Vlan.id.in_ (ids_to_keep)).delete(synchronize_session='fetch')
        session.commit()
        session.close()



    @staticmethod
    def DeleteVlan(id):
        Session = sessionmaker(bind=engine)

        session = Session()
        vlan_to_delete = session.query(Vlan).filter(Vlan.id==id)

        if not vlan_to_delete.first():
            logger.info('vlan %s does not exist in database..',id)
            return
        vlan_to_delete.delete()

        #session.query(Vlan).filter(Vlan.id==id).delete()
        session.commit()
        session.close()
        logger.debug('Vlan.DeleteVlan : start deleting process..')



        for ip in Switchs_IPs:
            swicth = Switch(ip, Username, Password)

            swicth.delete_vlan_from_switch(id)




    @staticmethod
    def ViewVlans():

        Session = sessionmaker(bind=engine)

        session = Session()
        all = session.query(Vlan).all()
        logger.debug('Vlan.ViewVlans : DB Query = %s', all)


        if len(all) == 0 :

            print("no vlans")
            return
        ptable = PrettyTable()

        ptable.field_names = ["Vlan ID", "name", "description"]
        for i in all :
            ptable.add_row([i.id,i.name,i.description])

        print(ptable)
        session.close()

    def UpdateVlan(self):
        logger.info('start updating vlan, please wait %')

        Session = sessionmaker(bind=engine)
        session = Session()

        session.query(Vlan).filter(Vlan.id==self.id).update({"name": (self.name),"description": (self.description)})

        session.commit()

        for ip in Switchs_IPs:
            swicth = Switch(ip,Username,Password)

            swicth.add_vlan_to_switch(Vlan = self)
        session.close()


    @staticmethod
    def updateDBbulk(list_of_vlans):
        logger.debug('Vlan.updateDBbulk : start updating vlan Bulk , Vlans : %s' , list_of_vlans)
        Session = sessionmaker(bind=engine)

        session = Session()
        for vlan in list_of_vlans:
            session.add(vlan)
        session.commit()
        session.close()











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

        logger.debug('Switch.connect_to_switch_telnet :  Start telnet connection to : %s', self.ip)
        try:
            conn = telnetlib.Telnet(self.ip, 23, 5)
        except socket.timeout:
            logger.error('unable to connect to switch : connection timeout')
            return False


        conn.read_until(b"Username: ")
        conn.write(Username.encode('ascii') + b"\n")
        conn.read_until(b"Password:")
        conn.write(Password.encode("ascii") + b"\n")

        conn.write(b"en\n")
        conn.read_until(b"Password:")
        conn.write(en_pass.encode('ascii') + b"\n")
        idx, obj, response = conn.expect([b"\#"], 3)

        if idx :
            logger.error('unable to connect to switch : wrong credentials')
            return False



        conn.write(b"terminal length 0\n")

        return conn



    def collect_switch_vlans(self,):
        ##
        ## Return list of Vlan object of the vlans collected from the first switch in Switchs_IPs.
        ##considering all switches must have same vlan DB

        logger.debug('Switch.collect_switch_vlans : Start synching Vlans from : %s', Switchs_IPs[0])

        #collect the vlans in the first switch only to synch our DB
        conn = self.connect_to_switch_telnet()
        if not conn :
            return


        conn.write(b"show vlan | in active\n")
        conn.write(b"exit\n")
        time.sleep(1)

        output = conn.read_very_eager().decode('ascii')

        output = output.splitlines()

        conn.close()

        vlans = []

        for line in output :
            vlan = {}
            if 'active' in line and 'show vlan' not in line :
                line = line.split()
                vlan = {'id' : line[0],'name':line[1]}
                vlans.append(vlan)

        if vlans:

            logger.debug('Switch.collect_switch_vlans : collected vlans = %s', vlans)
            vlan_list_object = []
            for dict in vlans:
                vlanObj = Vlan(dict['id'], dict['name'], 'na')
                vlan_list_object.append(vlanObj)
            return vlan_list_object


        else :
            logger.error(' no Vlans were colleced from : %s , please try again', Switchs_IPs[0])
            return None


        return



    def add_vlan_to_switch(self,Vlan):
         logger.debug(' Switch.add_vlan_to_switch : adding Vlan to  : {}'.format(self.ip))

         conn = self.connect_to_switch_telnet()

         conn.write(b"conf t\n")
         logger.debug('Switch.add_vlan_to_switch : sleep for 0.1 sec')
         time.sleep(0.1)
         comand = 'vlan {}\n'.format(Vlan.id)

         conn.write(comand.encode('ascii'))
         time.sleep(0.1)
         comand = 'name {}\n'.format(Vlan.name)
         conn.write(comand.encode('ascii'))
         conn.write(b"exit\n")
         time.sleep(1)

         #needed because telnetlib apply the command after conn.read_all()
         try:
             out = conn.read_all()
             logger.debug('Switch.add_vlan_to_switch : read_all() to apply configuration to switch')

         except :
             pass
         conn.close()





    def delete_vlan_from_switch(self, id):
        logger.debug('Switch.delete_vlan_from_switch : deleting Vlan {} from  : {}'.format(id,self.ip))

        conn = self.connect_to_switch_telnet()
        if not conn :
            return
        comand = "no vlan {}\n".format(id)
        conn.write(b"conf t\n")
        conn.write(comand.encode('ascii'))
        conn.write(b"exit\n")

        try:
            out = conn.read_all()

        except:
            pass
        conn.close()





class Synchronizer :

    switches = []
    def __init__(self,switches):
        """Constructor.

                :param   Switchs: list of switches
                :type    address: list of Switch object
                """

        self.switches = switches

    def firstVlansynch(self):


        list_of_vlans = self.switch[0].collect_switch_vlans()

        Vlan.updateDBbulk(list_of_vlans)

    def run(self):

        try :
            self.firstVlansynch()

        except :
            pass

        logger.debug('Synchronizer.run : start Synchronizing vlans from switch to DB')
        for switch in self.switches:

            vlans = switch.collect_switch_vlans()

            if not vlans :
                return

            Vlan.DeleteVlan_after_syncing_from_switch(vlans)

            #adding the vlans from the switch to teh DB
            for vlan in vlans:
                vlan.AddVlan_collected_from_switch()






            time.sleep(3)
