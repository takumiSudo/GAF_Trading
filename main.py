from src.config import API_KEY, SECRET_KEY
from alpaca.trading.client import TradingClient
from alpaca.trading.models import Clock
import alpaca
import time
import datetime as dt
import pytz

from alpaca.common.rest import RESTClient
from src.util import transactions, ROC, ALGO
from src.args import args_parser

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
api = RESTClient('https://paper-api.alpaca.markets', API_KEY, SECRET_KEY, api_version = 'v2')


def marketOpen():

    """
    Checks if the us market is open // if not returns false
    """
    isOPEN = trading_client.get_clock()
    if isOPEN.is_open == True:
        print("US market open : Proceeding")
        return True
    else:
        print("US market currently not open\nnext open : {%s}" %isOPEN.next_open)
        print("UTC in Default Format : {%s}" % dt.datetime.utcnow())
        return False

    

def split_ticker():
    """
    Split ticker.txt into space separated too list; in the future neded to adjust for config
    """

    stock = []
    crypto = []


    roc = ROC(args_parser())
    tickers = open('src/TICKER/test.txt', 'r').read()
    tickers = tickers.split(" ")

    list = []
    for i in tickers:
        list.append(i)
        print(list)

    for i in list:
        print(i)
        asset = roc.if_crypto(i)
        if asset == True:
            stock.append(i)
        else: 
            crypto.append(i)

    return stock, crypto


def main():
    """
    - Init trading client;

    - IF the Market is open:

        - If trading client does not have any positions
            - Try: Buying the best ROC stock in the ticker list given by the client
            - Break

        - Else if the trading view a position for a certain stock:
            - Check the Stock's Growth via unrealized plpc
            - While (-1% <stock_growth < 2%):
                - Wait until the growth reaches either thresholds

            - Else : 
                - Cancel all positions. 

    - Return Trading Client info
    """
 
    # create two lists, where one is crypto stocks and one is normal stocks
    stock, crypto = split_ticker()

    ticker = [stock, crypto]
    # get data
    current_pos = trading_client.get_all_positions()
    args = args_parser()
    algo = ALGO(args)

    # if there are no open positions currently, then try to buy
    while len(current_pos) > 0:

        for i in ticker:
            
            if ticker[i] == 'crypto':
                algo.noPosition(crypto)

            elif ticker[i] == 'stock':
                isOPEN = marketOpen()

                if isOPEN == True:
                    algo.noPosition()
                else:
                    break

        
        # ticker_list = split_ticker()
        # t = transactions(args)

        # for i in ticker_list:

        #     # Check if the trading client has a open position for the symbol in the ticker list
        #     isSELL = t.check_if_position(i)
        #     print(isSELL)

        #     if isSELL == True:
        #         grow = t.check_growth(i)
        #         if grow == True:
        #             t.sell(i)
        #         else: 
        #             print("position for {%s} still hasn't reached either threshold" %i)
        #     else:
        #         print("since no open position on symbol {%s} - moving on." %i)
        #         continue
                


    else:

        if len(current_pos) == 0:

            # get the tickers 
                ticker_list = split_ticker()

                # start up roc
                roc  = ROC(args)
                sym2buy = roc.compare_ask_ltp(ticker_list)


                # according to the sym2buy, execute sym2buy
                t = transactions(args)
                current_pos = t.sort_orders(sym2buy)

                print("Buying the stock with best ROC")
                
            


        

    
    
if __name__ == "__main__": 
    main()
