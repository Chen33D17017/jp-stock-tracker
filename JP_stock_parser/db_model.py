from sqlalchemy import create_engine, Column, Integer, Date, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os.path

engine = create_engine("sqlite:///data.db")
DBsession = sessionmaker(bind=engine)
Base = declarative_base()
    

class DBManager():    
    def __enter__(self, sessionmaker=DBsession):
        self.session = sessionmaker()
        return self.session

    def __exit__(self, type, value, trace):
        self.session.commit()
        self.session.close()

class StockCategory(Base):

    __tablename__ = "stock_category"
    key_id = Column(Integer, primary_key=True)
    category_name = Column(String(30), nullable=False)

    stock = relationship('Stock', backref="stock_category")
    
    def __repr__(self):
        return "Stockcategory({}, {})".format(self.key_id, self.category_name)

        
class Stock(Base):

    __tablename__= "stock"
    key_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('stock_category.key_id'))
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
    open_value = Column(Float, nullable=False)
    high_value = Column(Float, nullable=False)
    low_value = Column(Float, nullable=False)
    close_value = Column(Float, nullable=False)
    volume_value = Column(Float, nullable=False)
    adjclose_value = Column(Float, nullable=False)

    def __repr__(self):
        return "{} @{}".format(self.stock.name, self.record_date)

if not os.path.isfile('data.db'):
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    with DBManager() as db:
        print("hello world")
