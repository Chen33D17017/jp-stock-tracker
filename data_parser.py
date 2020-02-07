import urllib.request
import ssl
import os
import pandas as pd
import time
from datetime import datetime, date
import random
from bs4 import BeautifulSoup
import re
from db_model import Stock, Record, DB_manager


class stockDataReader():
    def __init__(self, sn):
        self.stock_id = sn
        self.stock_name = None
        self.url = "https://stocks.finance.yahoo.co.jp/stocks/history/?code={}.T".format(sn)
        self.start_date = None
        self.end_date = None
        self.result = None
        self.soup = None
        ssl._create_default_https_context = ssl._create_unverified_context

    def wait(self):
        time.sleep(random.randrange(3,7))
        
    def set_stock_id(self, sn):
        self.stock_id = sn
        self.url = "https://stocks.finance.yahoo.co.jp/stocks/history/?code={}.T".format(sn)
    
    def set_data_range(self, start, end, med="d"):
        self.url = "https://info.finance.yahoo.co.jp/history/?code={}.T".format(self.stock_id)
        self.url = self.url + "&sy={}&sm={}&sd={}".format(start.year, start.month, start.day)
        self.url = self.url + "&ey={}&em={}&ed={}&tm={}".format(end.year, end.month, end.day, med)

    def set_soup(self, url=None):
        if not url:
            url = self.url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read() 
        self.soup = BeautifulSoup(html, "html.parser")
        
    def get_data(self, verbose=False):
        # Initialize the result data
        self.set_soup()
        self.result = {
            "date": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
            "adjclose": [],
        }
        self._get_data()
        stock_name = self.soup.select("th.symbol")
        if stock_name:
            self.stock_name = stock_name[0].find_all("h1")[0].contents[0]

        page_now = 1
        while True:
            page_info = self.soup.select("ul.ymuiPagingBottom.clearFix")
            if page_info:
                page_info = page_info[0]
                pages = [i.contents[0] for i in page_info.find_all("a")]
                if pages:
                    pages = pages[0:-1]
                else:
                    pages = ['1']
                if pages[0] == "前へ":
                    pages = pages[1::]
                pages = list(map(int, pages))
                if page_now <= pages[-1]:
                    if verbose:
                        print("page now: {}".format(page_now))
                    pagination_url = self.url + "&p={}".format(page_now)
                    self.set_soup(url=pagination_url)
                    self._get_data()
                else:
                    break
                page_now += 1


        
    def _get_data(self):
        # requst the content
        self.wait()
        # get the stock content on table
        stock_content = self.soup.select("table.boardFin.yjSt.marB6")[0]
        table = stock_content.find_all('tr')

        for i, item in enumerate(table):
            data = [row.contents[0] for row in item.find_all('td')]
            if data:
                self.result["date"].append(date_convert(data[0]))
                self.result["open"].append(money_convert(data[1]))
                self.result["high"].append(money_convert(data[2]))
                self.result["low"].append(money_convert(data[3]))
                self.result["close"].append(money_convert(data[4]))
                self.result["volume"].append(money_convert(data[5]))
                self.result["adjclose"].append(money_convert(data[6]))

    def get_df(self):
        return pd.DataFrame.from_dict(self.result)

    def save_data2db(self):
        with DB_manager() as se:
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
        with DB_manager() as se:
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
        with DB_manager() as se:
            latest_date = se.query(Record.record_date).order_by(Record.record_date.desc()).first()[0]
        self.set_data_range(latest_date, date.today())
        self.get_data()
        self.save_data2db()
        
                    

    
def date_convert(content):
    matches = re.finditer('(\d+)', content)
    return "-".join([match.group() for match in matches])

def money_convert(content):
    str_value = "".join(content.split(","))
    return int(str_value)

        
        
        

if __name__ == '__main__':
    stock_reader = stockDataReader(1320)
    start = datetime(2019, 1, 1)
    end = datetime(2020, 2, 2)
    # stock_reader.set_data_range(start, end)
    # stock_reader.get_data()
    # stock_reader.save_data2db()

    
    
