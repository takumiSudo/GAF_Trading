import alpaca
import random
import math
import pandas as pd
import datetime as dt
import time
import os
import datetime

import src.config as config
from args import args_parser
import requests

from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.historical import CryptoHistoricalDataClient




"""
IN ORDER for the ROC to Work:

    1. Ask PRICE
    2. Last traded price
    3. ROC calculator roc = ((p(n) - p(n - 1)) / p(n - 1)) * 100
    4. List of ROCs': dict of ROC's and TICKERS and to find the highest ROC

    Other functions needed:
    - get the live data
    - parse through the ticker wanted
    - 

"""


trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)

class ROC:
    def __init__(self, args):
        self.args = args
        self.end_url = "https://paper-api.alpaca.markets" 
        self.client = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
        self.dt_now = datetime.datetime.now()
        self.MIN = 1 # set default as 30 min
        self.ticker_list = []
        

    def if_crypto(self, symbol):

        if trading_client.get_asset(symbol).asset_class == 'us_equity':
            return True
        else:
            return False


    def get_data_stock(self):

        """
        if the trade is the firstever trade done -> then get the data for 30 min and transfer into csv
        
            - get_min_data(ticker) : for all the symbols in the ticker list get the quotes from 30 min before.
            - in order to get different timeframe of data: can send through other values such as 1, 15, 60 min

            
            trying to expand into crypto
        """
        
            
                        
        request_params_old = StockBarsRequest(
                    symbol_or_symbols= self.ticker_list,
                    timeframe=TimeFrame.Minute,
                    start=self.dt_now - datetime.timedelta(days=1) - datetime.timedelta(minutes=30),
                    end= self.dt_now - datetime.timedelta(days=1) - datetime.timedelta(minutes=29)
                    )

        request_params_now = StockBarsRequest(
                    symbol_or_symbols= self.ticker_list,
                    timeframe=TimeFrame.Minute,
                    start= self.dt_now - datetime.timedelta(days=1) - datetime.timedelta(minutes=1),
                    end= self.dt_now - datetime.timedelta(days=1) ,
                    )
        


        ticker_bars_old = self.client.get_stock_bars(request_params_old)
        ticker_bars_now = self.client.get_stock_bars(request_params_now)
        o_df = ticker_bars_old.df
        n_df = ticker_bars_now.df

        return o_df, n_df

    def get_data_crypto(self):

        
        self.client = CryptoHistoricalDataClient(config.API_KEY, config.SECRET_KEY)

        request_params_old = CryptoBarsRequest(
                    symbol_or_symbols= self.ticker_list,
                    timeframe=TimeFrame.Minute,
                    start=self.dt_now - datetime.timedelta(days=1) - datetime.timedelta(minutes=30),
                    end= self.dt_now - datetime.timedelta(days=1) - datetime.timedelta(minutes=29)
                    )

        request_params_now = CryptoBarsRequest(
                    symbol_or_symbols= self.ticker_list,
                    timeframe=TimeFrame.Minute,
                    start= self.dt_now - datetime.timedelta(days=1) - datetime.timedelta(minutes=1),
                    end= self.dt_now - datetime.timedelta(days=1) ,
                    )
        
    
    
        ticker_bars_old = self.client.get_crypto_bars(request_params_old)
        ticker_bars_now = self.client.get_crypto_bars(request_params_now)
        o_df = ticker_bars_old.df
        n_df = ticker_bars_now.df
        
        return o_df, n_df


    def roc(self, old, new):
        """
        Here the old dataframe and new dataframe is merged for each of the symbols:
        
            - the res list hold the ROC values for each symbol that was calculated
        """

        # play around with dataframe to achieve the symbol with the max roc
        df = old.merge(new, how='inner', on='symbol')
        df = df.drop(['open_x','high_x', 'low_x', 'vwap_x', 'volume_x', 'trade_count_x', 'open_y','high_y', 'low_y', 'vwap_y', 'volume_y', 'trade_count_y'],axis='columns')
        df['roc'] = df["close_y"] / df["close_x"]
        max_roc = df.loc[df['roc'].idxmax()]
        

        # retrieve the name of the stock of the max_roc
        sym2buy = max_roc.name
        return sym2buy
            

    

    def compare_ask_ltp(self, ticker_list):

        """
        The scheme of ROC is to retrieve the last_traded_price (LTP) and the ask_price(ASK)
        where the LTP is the price of the symbol 30min before and the ASK price being the price right now

        Lastly, after the ROC is calculated for each symbol in the ticker list, the max value is chosen
        and sent to the trasaction side for the buy to be executed.

        For all the symbols in ticker list,

            - first retrieves both the minute through the get_data() 
                : returns old_dataframe, new_dataframe 

            - pass through the ROC to check the highest one


            output : sym2buy (the symbol with the most roc) 
        """
        
        # append all of the symbols that are included in the ticker list
        for i in list(ticker_list):
            self.ticker_list.append(i)
            
            stock = self.if_crypto(i)


        if stock == True:
                
            old, new = self.get_data_stock()
        else:
            old, new = self.get_data_crypto()
        
    
        # calculate ROC and choose max
        sym2buy = self.roc(old, new)

        return sym2buy

        
    

class transactions:
    def __init__(self, args):
        self.args = args
        self.symbol = args.symbol
        self.qty = args.qty
        self.side = args.side

    def ability_to_buy(self):

        """
        !!! need to debug the ability to buy !!!
        """
        cashBalance = trading_client.get_account().cash
        stock_price = 100.0
        # stock_price = trading_client.get_latest_trade(self.symbol).price

        # price_qty = (stock_price * self.qty) / cashBalance
        # price_qty = float(0.1)
        # if price_qty(price_qty > 1.0):
        #     raise  Exception("Sorry, Insufficient Balance")
        #     exit
        # else:
        pass

        
    def buy(self, symbol):
        """
        Send BUY request // currently just asking for the symbol and qty
        """
        
        market_order_data = MarketOrderRequest(
                                symbol = symbol, 
                                qty = self.qty, 
                                side = OrderSide.BUY,
                                time_in_force=TimeInForce.GTC
                            )
        
        market_order = trading_client.submit_order(market_order_data)
        return market_order

    def check_ret(self, symbol):
        """
        check returns of the current stock: currently set at 2%
        """
        # try: 
        #     returns = float(trading_client.get_open_position(symbol).unrealized_plpc)*100
            
        # except Exception as exception:
        #     if exception.__str__() == 'position does not exist':
            
        
            
        # if (returns >= 2):
        #    isSELL = True
        # else: 
        #     isSELL = False
        # return isSELL
        pass

    def sell(self, symbol):
        """
        Send cancel request // currently just asking for the symbol and qty
        """

        market_order = trading_client.close_position(cancel_orders=True, symbol_or_asset_id=symbol)
        return market_order


    def get_positions(self):
        positions = trading_client.get_all_positions()
        
        for position in positions:
            for property_name, value in position:
                print(f"\"{property_name}\": {value}")

        return positions


    def sort_orders(self, sym2buy):
        """
        From setting the symbol to buy to transactional stuff;

        - set the symbol for buy
        - checks the ability of the client, whether they can buy the symbol for the quantity

        """

        self.symbol == sym2buy


        self.ability_to_buy() # check if the balance has enough money to buy the stock
        cur = self.get_positions()
    
        self.buy(sym2buy)

        return cur


    def check_if_position(self, current_stock):

        """
        Check if the stock in open position got the 2% growth, so it can close the opperation
        """
        isSell = True

        stock = trading_client.get_open_position(current_stock)
        
        if stock.symbol == current_stock:
            isSell == True
        else: 
            isSell == False
        
        return isSell
        # memo 24/04 : trying to find a way for the try and except, where if the symbol exists, 
        #              operate normally but if the symbol does not exist, break and check for the next one
        #              need to learn about Exception and stuff
            

        
        
    def check_growth(self, current_stock):
        # checks returns for stock in portfolio (api.get_positions()[0].symbol)
        buy_price = float(trading_client.get_open_position(current_stock).avg_entry_price) * float(trading_client.get_open_position(current_stock).qty)
        current_price = float(trading_client.get_open_position(current_stock).current_price) * float(trading_client.get_open_position(current_stock).qty)

        growth = float(current_price / buy_price) * 100

        if (growth >= 2 or growth < 0):
           go_sign = False
        else: 
            go_sign = True
        return go_sign
        
class ALGO:
    
    def __init__(self, args):
            self.args = args
            self.Transactions = transactions(args)
            self.ROC = ROC(args)

            
    def noPosition(self, list):


        for i in list:

            # Check if the trading client has a open position for the symbol in the ticker list
            isSELL = transactions.check_if_position(i)
            print(isSELL)

            if isSELL == True:
                grow = transactions.check_growth(i)
                if grow == True:
                    transactions.sell(i)
                else: 
                    print("position for {%s} still hasn't reached either threshold" %i)
            else:
                print("since no open position on symbol {%s} - moving on." %i)
                continue

    def openPositions(self, list):

         # start up roc
        roc  = self.ROC
        sym2buy = roc.compare_ask_ltp(list)


        # according to the sym2buy, execute sym2buy
        transactions = self.Transactions
        current_pos = transactions.sort_orders(sym2buy)

        print("Buying the stock with best ROC")

def main():
    args = args_parser()
    T = transactions(args)
    T.sort_orders()


if __name__ == '__main__':
    main()