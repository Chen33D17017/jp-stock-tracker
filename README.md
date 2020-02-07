## Description
This repository provide an simple python script to parse the Janapnese stock data from Yahoo Fianance Japan, also it can store the data on your local machine with database like Sqlite, MySql or other DBMS supported by Sqlalchemy. 

## Requirement
- Python3
- Install requirements(pandas and Beautifulsoup)

By changing the engine setting on db_model.py you can use other type of database (default with sqlite on data.db file)

## How to use it

After instance the stockDataReader with number of your stock on data_parser.py. Setting the date range you want to parse the data by using method of get\_data, after that you can get the dataframe on pandas by using method of get\_df. For example:

```Python
from data_parser import stockDataReader

# Assign the stock 
stock_reader = stockDataReader(1320)

# Assign date
start = datetime(2019, 1, 1)
end = datetime(2020, 2, 2)
stock_reader.set_data_range(start, end)

# Get the dataframe of stock data
stock_reader.get_data()
result = stock_reader.get_df()

```

Use set\_stock\_id method to get another stock data in the same instance

```python
stock_reader.set_stock_id(1321)

stock_reader.get_data()
result = stock_reader.get_df()
```
Finally, save the data into local database

```python
stock_reader.save_data2db()

```

To read the data from database use read_DB or read_DB_with_update method

```python
stock_reader.save2db()

stock_reader.read_DB_with_update()
```

A simple senario is provided with jupyter notebook on example.ipynb.
