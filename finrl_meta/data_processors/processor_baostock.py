import baostock as bs
import pandas as pd

'''Reference: https://github.com/AI4Finance-LLC/FinRL'''

from typing import List
import numpy as np
import pandas as pd
import pytz
import yfinance as yf
try:
    import exchange_calendars as tc
except:
    print('Cannot import exchange_calendars.',
          'If you are using python>=3.7, please install it.')
    import trading_calendars as tc
    print('Use trading_calendars instead for yahoofinance processor..')
# from basic_processor import BasicProcessor
from finrl_meta.data_processors.basic_processor import BasicProcessor
from finrl_meta.data_processors.func import calc_time_zone

TIME_ZONE_SHANGHAI = 'Asia/Shanghai'  ## Hang Seng HSI, SSE, CSI
TIME_ZONE_USEASTERN = 'US/Eastern'  # Dow, Nasdaq, SP
TIME_ZONE_PARIS = 'Europe/Paris'  # CAC,
TIME_ZONE_BERLIN = 'Europe/Berlin'  # DAX, TECDAX, MDAX, SDAX
TIME_ZONE_JAKARTA = 'Asia/Jakarta'  # LQ45
TIME_ZONE_SELFDEFINED = 'Asia/Shanghai'  # If neither of the above is your time zone, you should define it, and set USE_TIME_ZONE_SELFDEFINED 1.
USE_TIME_ZONE_SELFDEFINED = 1  # 0 (default) or 1 (use the self defined)


class BaostockProcessor(BasicProcessor):
    def __init__(self, data_source: str, start_date, end_date, time_interval, **kwargs):
        super().__init__(data_source, start_date, end_date, time_interval, **kwargs)

    # 日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据
    # ["5m", "15m", "30m", "60m", "1d", "1w", "1M"]
    def download_data(self, ticker_list: List[str]):
        lg = bs.login()
        print('baostock login respond error_code:' + lg.error_code)
        print('baostock login respond  error_msg:' + lg.error_msg)

        self.time_zone = calc_time_zone(ticker_list, TIME_ZONE_SELFDEFINED, USE_TIME_ZONE_SELFDEFINED)
        self.dataframe = pd.DataFrame()
        for ticker in ticker_list:
            # All supported: "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
            rs = bs.query_history_k_data_plus(ticker,
                                              "date,code,open,high,low,close,volume",
                                              start_date=self.start_date, end_date=self.end_date,
                                              frequency=self.time_interval, adjustflag="3")

            print('baostock download_data respond error_code:' + rs.error_code)
            print('baostock download_data respond  error_msg:' + rs.error_msg)

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            df = pd.DataFrame(data_list, columns=rs.fields)
            self.dataframe = self.dataframe.append(df)
        self.dataframe = self.dataframe.sort_values(by=['date', 'code']).reset_index(drop=True)
        bs.logout()

    def clean_data(self):
        self.dataframe = self.dataframe.rename(columns={'date': 'time', 'code': 'tic'})


    def get_trading_days(self, start, end):
        lg = bs.login()
        print('baostock login respond error_code:' + lg.error_code)
        print('baostock login respond  error_msg:' + lg.error_msg)
        return bs.query_trade_dates(start_date=start, end_date=end)
        bs.logout()

