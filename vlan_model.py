from sqlalchemy.orm import sessionmaker , relationship
from sqlalchemy import create_engine , Column , Integer , String , ForeignKey
from sqlalchemy.ext.declarative import declarative_base
base = declarative_base()
engine = create_engine('sqlite:///vlan.db', echo = True)
base.metadata.create_all(bind = engine)

class Vlan(base):

    __tablename__ = "vlan"

    id = Column('id',Integer,primary_key=True)
    name = Column('name', String)
    description = Column('description' , String)
    engine = create_engine('sqlite:///vlan.db', echo=True)
    def AddVlan(self,):
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