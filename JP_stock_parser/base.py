import urllib.request
import os
import pandas as pd
import time
from datetime import datetime, date
import random
from bs4 import BeautifulSoup
import re
from db_model import Stock, Record, DBManager
from abc import abstractmethod, ABCMeta


class ParserBase():
    def __init__(self, sn):
        self.stock_id = sn
        self.stock_name = None
        self.url = None
        self.start_date = None
        self.end_date = None
        self.result = None
        self.soup = None

    @abstractmethod
    def set_stock(self, sn=None, time_range=None):
        pass

    @abstractmethod
    def get_data(self, verbose=False):
        pass
        
    def set_soup(self, url=None):
        if not url:
            url = self.url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read() 
        self.soup = BeautifulSoup(html, "html.parser")


    def get_df(self):
        if not self.result:
            raise ValueErro("With None data, please use method of get_data first")
        return pd.DataFrame.from_dict(self.result)

    def save_data2db(self):
        with DBManager() as se:
            tmp = se.query(Stock).filter(Stock.stock_id==self.stock_id).first()
            if not tmp:
                new_stock = Stock(stock_id=self.stock_id, name=self.stock_name)
                se.add(new_stock)
                se.commit()
            for i, item in enumerate(self.result["date"]):
                # Check whether data exist
                record_date = datetime.strptime(item, "%Y-%m-%d").date()
                tmp = se.query(Record).filter(Record.stock_id==self.stock_id, Record.record_date==record_date).first()
                # If not exist add the record
                if not tmp:
                    new_record = Record(stock_id=self.stock_id, record_date=record_date, open_value=self.result['open'][i], high_value=self.result['high'][i], low_value=self.result['low'][i], close_value=self.result['close'][i], volume_value=self.result['volume'][i], adjclose_value=self.result['adjclose'][i])
                    se.add(new_record)
            se.commit()

    def read_DB_with_update(self, date_range=None):
        self.update_DB()
        self.read_DB(date_range=date_range)
    
    def read_DB(self, date_range=None):
        self.result = {
            "date": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
            "adjclose": [],
        }
        with DBManager() as se:
            get_data_query = se.query(Record).filter(Record.stock_id==self.stock_id)
            if date_range:
                get_data_query = get_data_query.filter(Record.record_date >= date_range[0], Record.record_date < date_range[1])
            record_list = get_data_query.all()
            for item in record_list:
                self.result['date'].append(item.record_date)
                self.result['open'].append(item.open_value)
                self.result['high'].append(item.high_value)
                self.result['low'].append(item.low_value)
                self.result['close'].append(item.close_value)
                self.result['volume'].append(item.volume_value)
                self.result['adjclose'].append(item.adjclose_value)
        return self.get_df()

    def update_DB(self):
        with DBManager() as se:
            latest_date = se.query(Record.record_date).order_by(Record.record_date.desc()).first()[0]
        self.set_data_range(latest_date, date.today())
        self.get_data()
        self.save_data2db()

    def wait(self):
        time.sleep(random.randrange(1,3))
        
    def date_convert(self, content):
        matches = re.finditer('(\d+)', content)
        return "-".join([match.group() for match in matches])

    def money_convert(self, content):
        str_value = "".join(content.split(","))
        return float(str_value)
