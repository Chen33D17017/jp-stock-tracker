from sqlalchemy import create_engine, Column, Integer, Date, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os.path

engine = create_engine("sqlite:///data.db")
DBsession = sessionmaker(bind=engine)
Base = declarative_base()
    

class DB_manager():    
    def __enter__(self, sessionmaker=DBsession):
        self.session = sessionmaker()
        return self.session

    def __exit__(self, type, value, trace):
        self.session.commit()
        self.session.close()

class Stock(Base):

    __tablename__= "stock"
    key_id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, nullable=True, unique=True)
    name = Column(String(50), nullable=False)

    records = relationship('Record', backref="stock")

    def __repr__(self):
        return "Stock({}, {})".format(self.stock_id, self.name)

class Record(Base):
    __tablename__ = "record"
    key_id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock.stock_id'))
    record_date = Column(Date, nullable=False)
    open_value = Column(Integer, nullable=False)
    high_value = Column(Integer, nullable=False)
    low_value = Column(Integer, nullable=False)
    close_value = Column(Integer, nullable=False)
    volume_value = Column(Integer, nullable=False)
    adjclose_value = Column(Integer, nullable=False)

    def __repr__(self):
        return "{} @{}".format(self.stock.name, self.record_date)

if not os.path.isfile('data.db'):
    Base.metadata.create_all(engine)
