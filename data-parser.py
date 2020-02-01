import urllib.request
import ssl
import os
import pandas as pd
import time
from datetime import datetime, date
import random
from bs4 import BeautifulSoup
import re
from tqdm import tqdm


class stockDataReader():
    def __init__(self, sn):
        self.stock_name = sn
        self.url = f"https://stocks.finance.yahoo.co.jp/stocks/history/?code={sn}.T"
        self.start_date = None
        self.end_date = None
        self.result = None
        self.soup = None
        ssl._create_default_https_context = ssl._create_unverified_context

    def wait(self):
        time.sleep(random.randrange(3,7))
        
    def set_stock_name(self, sn):
        self.url = f"https://stocks.finance.yahoo.co.jp/stocks/history/?code={sn}.T"
    
    def set_data_range(self, start, end, med="d"):
        self.url = f"https://info.finance.yahoo.co.jp/history/?code={self.stock_name}.T"
        self.url = self.url + f"&sy={start.year}&sm={start.month}&sd={start.day}"
        self.url = self.url + f"&ey={end.year}&em={end.month}&ed={end.day}&tm={med}"

    def set_soup(self, url=None):
        if not url:
            url = self.url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read() 
        self.soup = BeautifulSoup(html, "html.parser")
        
    def get_data(self):
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
        page_info = self.soup.select("ul.ymuiPagingBottom.clearFix")
        if page_info:
            page_info = page_info[0]
            pages = [i.contents[0] for i in page_info.find_all("a")][0:-1]
            pages = list(map(int, pages))
            for page in tqdm(pages):
                print(page)
                pagination_url = self.url + f"&p={page}"
                self.set_soup(url=pagination_url)
                self._get_data()

        
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

    
def date_convert(content):
    matches = re.finditer('(\d+)', content)
    return "-".join([match.group() for match in matches])

def money_convert(content):
    str_value = "".join(content.split(","))
    return int(str_value)

        
        
        

if __name__ == '__main__':
    stock_reader = stockDataReader(1320)
    start = datetime(2019, 1, 1)
    end = datetime(2020, 1, 1)
    stock_reader.set_data_range(start, end)
    stock_reader.get_data()
    df = stock_reader.get_df()
    print(df.head(5))
    
    
