from JP_stock_parser.base import ParserBase

class stockDataReader(ParserBase):
    def __init__(self, sn):
        ParserBase.__init__(self, sn)
        
    def set_stock(self, sn=None, time_range=None):
        if sn:
            self.stock_id = sn
        if time_range:
            start, end = time_range[0], time_range[1]
            self.url = "https://info.finance.yahoo.co.jp/history/?code={}.T".format(self.stock_id)
            self.url = self.url + "&sy={}&sm={}&sd={}".format(start.year, start.month, start.day)
            self.url = self.url + "&ey={}&em={}&ed={}&tm=d".format(end.year, end.month, end.day)
        else:
            self.url = "https://stocks.finance.yahoo.co.jp/stocks/history/?code={}.T".format(sn)

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
            # if get the page information
            if page_info:
                page_info = page_info[0]
                pages = [i.contents[0] for i in page_info.find_all("a")]
                # if exist other page
                if pages:
                    # get rid of 次へ (if not in last page)
                    if pages[-1] == "次へ":
                        pages = pages[0:-1]
                    # if in the final page
                    else:
                        break
                else:
                    # if only have one page
                    pages = ['1']
                if pages[0] == "前へ":
                    # get rid of 前へ
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
                try:
                    self.result["date"].append(self.date_convert(data[0]))
                    self.result["open"].append(self.money_convert(data[1]))
                    self.result["high"].append(self.money_convert(data[2]))
                    self.result["low"].append(self.money_convert(data[3]))
                    self.result["close"].append(self.money_convert(data[4]))
                    self.result["volume"].append(self.money_convert(data[5]))
                    self.result["adjclose"].append(self.money_convert(data[6]))
                except ValueError:
                    continue
    
    
