# Given the FMI API, retriev historical data and feed it through the Pyts library for the data to be encoded into GAF and MTF
import config as config
import requests
import pandas as pd
import json as j
from args import args_parser
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from pyts.image import GramianAngularField, MarkovTransitionField
import csv
import numpy as np
import math

class DATA:

    def __init__(self, args):
        self.args = args
        self.fmi_multi_stock_url = "https://financialmodelingprep.com/api/v3/quote/"
        self.fmi_stock_url = "https://financialmodelingprep.com/api/v3/historical-chart/30min/" 
        self.fmi_crypto_url = "https://financialmodelingprep.com/api/v3/historical-chart/5min/"
        self.symbol_list = []


    def parse_ticker_list(self, ticker_list):
        
        for i in list(ticker_list):
            self.symbol_list.append(i)

    def call_stock(self):

        stock_url = self.fmi_stock_url 
        for i in list(self.symbol_list):
            api_url = stock_url + i + "?apikey=" + config.FMI_KEY
            responce = requests.get(api_url)
            file = responce.json()

            df = pd.DataFrame(file)
            df.to_csv("src/data/%s_data.csv" % i, index=False, sep=",")


def tabulate(x, y, f):
    """Return a table of f(x, y). Useful for the Gram-like operations."""
    return np.vectorize(f)(*np.meshgrid(x, y, sparse=True))
def cos_sum(a, b):
    """To work with tabulate."""
    return(math.cos(a+b))

class GAF:

    def __init__(self):
        pass
    def __call__(self, serie):
        """Compute the Gramian Angular Field of an image"""
        # Min-Max scaling
        min_ = np.amin(serie)
        max_ = np.amax(serie)
        scaled_serie = (2*serie - max_ - min_)/(max_ - min_)

        # Floating point inaccuracy!
        scaled_serie = np.where(scaled_serie >= 1., 1., scaled_serie)
        scaled_serie = np.where(scaled_serie <= -1., -1., scaled_serie)

        # Polar encoding
        phi = np.arccos(scaled_serie)
        # Note! The computation of r is not necessary
        r = np.linspace(0, 1, len(scaled_serie))

        # GAF Computation (every term of the matrix)
        gaf = tabulate(phi, phi, cos_sum)

        return(gaf, phi, r, scaled_serie)


class timeSeries:
    """
    From getting the input for the time series, divide the dataset into batches(still need to implement)
    and from the those batches run the GAF for the output to have a 
    """
    def __init__(self, args, data_set):
        self.args = args
        self.csv = pd.read_csv(data_set)
        self.gaf = GramianAngularField()
    

    def normalize(self, x):
        l2 = np.linalg.norm(x,keepdims=True)
        l2[l2==0] = 1
        return x/l2
    
    def batch(iterable, n=1):
        """
        given a dataset, separate them into equally divided batches for the TS to be able to function
        """
        l = len(iterable)

        for ndx in range(0, l, n):
            return iterable[ndx:min(ndx + n, l)]
        
    def reshape(self, df):

        # load for Gramian Angular Summation Fields for all the time series
             
        price = df['Close'].values
        price_arr = np.array(price)
        price_arr = self.normalize(price_arr)
        price_arr = price_arr.reshape(-1, 1)

        return price_arr


    def to_gaf(self):

        """
        load data onto to timeseries as a Gramian Angular Field.

        - load the data
        - divide them into batches
        - for each batches reshape them into the required shape.
        - Run the GAf for each batch
        """
        
        df = self.csv   

        price = df['Close'].values
        price_arr = np.array(price)
        price_arr = self.normalize(price_arr)
        price_arr = price_arr.reshape(-1, 1)

        # return price_arr
        # df_batch = self.batch(lambda x : df['Close'], 10) # batch_size
        # print(df_batch.shape)

        # for batch in range(10):
        
        #     div_df = {[10]}
        #     div_df.append(self.reshape(batch))
        

        
        # need to know how the shape is after the batch.
        
        
        gramian = GAF()
        g, _, _, _ = gramian(price_arr)
        X_gaf = self.gaf.fit_transform(g)
        print(g.shape)
        print(X_gaf.shape)
        
        # Show the results for the first time series
        # plt.figure(figsize=(16, 8))
        # plt.subplot(121)
        # plt.plot(price_arr)
        # plt.title("Original", fontsize=16)
        # plt.subplot(122)
        # plt.imshow(g, cmap='rainbow', origin='lower')
        # plt.title("GAF", fontsize=16
        # plt.show()

        fig = plt.figure(figsize=(10, 5))

        grid = ImageGrid(fig, 111, nrows_ncols=(5, 10), axes_pad=0.1, share_all=True,
                 cbar_mode='single')
        for i, ax in enumerate(grid):
            im = ax.imshow(X_gaf[i], cmap='rainbow', origin='lower', vmin=-1., vmax=1.)
        grid[0].get_yaxis().set_ticks([])
        grid[0].get_xaxis().set_ticks([])
        plt.colorbar(im, cax=grid.cbar_axes[0])
        ax.cax.toggle_label(True)

        fig.suptitle("GAF", y=0.92)
        plt.show()

    def timeSeries_main(self):

        
        df = self.csv

    



def main():
    args = args_parser()
    dt = DATA(args)
    list = ["AAPL", "TSLA"]
    dt.parse_ticker_list(list)
    dt.call_stock()


    # currently the gaf is only taking in the whole dataset 
    # need to divde the datasets into batches. 
    gaf = timeSeries(args, 'src/data/AAPL.csv')
    gaf.to_gaf()
    


if __name__ == '__main__':
    main()