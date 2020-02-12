from JP_stock_parser.base import ParserBase

class stockDataReader(ParserBase):
    def __init__(self, sn):
        ParserBase.__init__(self, sn)
        self.time_list = []

    def set_stock(self, sn=None, time_range=None):
        if sn:
            self.stock_id = sn
        if time_range:
            self.time_list = [y for y in range(time_range[0].year, time_range[1].year+1)]
        self.url = "https://kabuoji3.com/stock/{}/".format(self.stock_id)

    def get_data(self, verbose=False):
        self.result = {
            "date": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
            "adjclose": [],
            }
        if self.time_list:
            for year in self.time_list:
                if verbose:
                    print("parse data in {}".format(year))
                parse_url = self.url + "{}/".format(year)
                self.set_soup(parse_url)
                self._get_data()
        else:
            self.set_soup()
            self._get_data()

    def _get_data(self):
        self.wait()
        stockdata= self.soup.find_all("td")
        stockdata = [s.contents[0] for s in stockdata]
        stockdata = list(zip(*[iter(stockdata)]*7))
        for data in stockdata:
            self.result["date"].append(data[0])
            self.result["open"].append(self.money_convert(data[1]))
            self.result["high"].append(self.money_convert(data[2]))
            self.result["low"].append(self.money_convert(data[3]))
            self.result["close"].append(self.money_convert(data[4]))
            self.result["volume"].append(self.money_convert(data[5]))
            self.result["adjclose"].append(self.money_convert(data[6]))
                    
                    
