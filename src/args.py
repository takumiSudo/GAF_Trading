import argparse


def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--symbol', type=str, default="BTC/USD", help='symbol')
    parser.add_argument('--qty', type=int, default=0.001, help='quantity')
    parser.add_argument('--tif', type=str, default="GTC", help='Time in force')
    parser.add_argument('--side', type=str, default="BUY", help='BUY or SELL')
    parser.add_argument('--batch_sz', type=int, default=10, help='batch size for dividing the dataset into equal parts.')
    
    
    args = parser.parse_args()

    return args