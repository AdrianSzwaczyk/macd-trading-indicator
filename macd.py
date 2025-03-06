import pandas as pd

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

def calculate_macd(data):
    ema_12 = data.ewm(span=12, adjust=False).mean()
    ema_26 = data.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

def plot_stock_values(data, file, mode):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.title('Stock values for ' + file)
    plt.xlabel('Date')
    plt.ylabel('Price [$]')
    plt.legend()
    
    formatter = ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x))
    plt.gca().yaxis.set_major_formatter(formatter)
    
    if mode == 1:
        plt.savefig('R_Images/' + file + '_stock_values.png')
    else:
        plt.savefig('Images/' + file + '_stock_values.png')
    plt.show()

def calculate_r(data):
    r_values = []
    window = 14
    for i in range(len(data)):
        if i < window:
            r_values.append(0)
            continue

        highest = max(data.iloc[i - window:i])
        lowest = min(data.iloc[i - window:i])
        close = data.iloc[i]

        r = (highest - close) / (highest - lowest) * -100
        r_values.append(r)
    
    r_data = pd.Series(r_values, index=data.index)
    return r_data


def find_crossing_points(macd_line, signal_line, rsi, data, mode):
    last_point = 'buy'
    buy_points = []
    sell_points = []
    for i in range(1, len(macd_line)):
        if (macd_line.iloc[i] > signal_line.iloc[i] and macd_line.iloc[i - 1] <= signal_line.iloc[i - 1]) \
                and last_point != 'buy':
            if (mode == 1):
                if (rsi.iloc[i] > -65):
                    buy_points.append(macd_line.index[i])
                    last_point = 'buy'
            else: 
                buy_points.append(macd_line.index[i])
                last_point = 'buy'
        elif (macd_line.iloc[i] < signal_line.iloc[i] and macd_line.iloc[i - 1] >= signal_line.iloc[i - 1]) \
                and last_point != 'sell':
            if (mode == 1):
                if (rsi.iloc[i] < -75):
                    sell_points.append(macd_line.index[i])
                    last_point = 'sell'
            else: 
                sell_points.append(macd_line.index[i])
                last_point = 'sell'
    sell_points = sell_points[:len(buy_points)]
    return buy_points, sell_points

def plot_macd(data, macd_line, signal_line, buy_points, sell_points, file, mode):
    plt.figure(figsize=(14, 7))

    plt.plot(macd_line, label='MACD Line', color='red', linewidth=0.8)
    plt.plot(signal_line, label='Signal Line', color='green', linewidth=0.8)
    for date in buy_points:
        plt.plot(date, macd_line.loc[date], marker='o', markersize=6, color='green')
    for date in sell_points:
        plt.plot(date, macd_line.loc[date], marker='o', markersize=6, color='red')
    plt.title('MACD indicator with buy/sell signals for ' + file)
    plt.xlabel('Date')
    plt.ylabel('MACD Value')
    plt.legend()
    
    formatter = ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x))
    plt.gca().yaxis.set_major_formatter(formatter)
    
    
    if mode == 1:
        plt.savefig('R_Images/' + file + '_macd_and_signal.png')
    else:
        plt.savefig('Images/' + file + '_macd_and_signal.png')
    plt.show()

    
def plot_portfolio(portfolio_values, data, file, buy_points, sell_points, mode):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, portfolio_values, label='Portfolio value', color='orange', drawstyle='steps-post')
    daily_stock_value = data['Close'] * 1000
    plt.plot(data.index, daily_stock_value, label='Value if no trades', color='grey', drawstyle='steps-post', linewidth=0.6)
    
    for date in buy_points:
        portfolio_value = portfolio_values.loc[date]
        plt.plot(date, portfolio_value, marker='o', markersize=6, color='green')
    for date in sell_points:
        portfolio_value = portfolio_values.loc[date]
        plt.plot(date, portfolio_value, marker='o', markersize=6, color='red')
        
    plt.title('Portfolio value over time for ' + file)
    plt.xlabel('Date')
    plt.ylabel('Price [$]')
    plt.legend()
    
    formatter = ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x))
    plt.gca().yaxis.set_major_formatter(formatter)
    
    if mode == 1:
        plt.savefig('R_Images/' + file + '_money.png')
    else:
        plt.savefig('Images/' + file + '_money.png')
    plt.show()


def calculate_portfolio_value(data, buy_points, sell_points):
    starting_money = 1000 * data.iloc[0, 0]
    portfolio_value = starting_money
    stock = 1000
    money = 0
    portfolio_values = []
    starting_stock = []

    for date in data.index:
        if date in buy_points:
            buy_price = data.loc[date, 'Close']
            stock = money / buy_price
            money = 0
            portfolio_value = stock * buy_price
            portfolio_values.append(portfolio_value)
        elif date in sell_points:
            sell_price = data.loc[date, 'Close']
            money = sell_price * stock
            stock = 0
            portfolio_value = money
            portfolio_values.append(portfolio_value)
        else:
            if (stock != 0):
                portfolio_value = stock * data.loc[date, 'Close']
            else:
                portfolio_value = money
            portfolio_values.append(portfolio_value)
    return pd.Series(portfolio_values, index=data.index)

def trade_stock(file, mode, plot=1):
    data = pd.read_csv('CSV/' + file + '.csv', index_col='Date', parse_dates=True, nrows=1000)

    macd_line, signal_line = calculate_macd(data['Close'])
    rsi = calculate_r(data['Close'])
    buy_points, sell_points = find_crossing_points(macd_line, signal_line, rsi, data, mode)

    portfolio_values = calculate_portfolio_value(data, buy_points, sell_points)
    
    if plot == 1:
        plot_stock_values(data, file, mode)
        plot_macd(data['Close'], macd_line, signal_line, buy_points, sell_points, file, mode)
        plot_portfolio(portfolio_values, data, file, buy_points, sell_points, mode)

    print("Stock values file: " + file)
    print(f"Starting money: {1000 * data.iloc[0, 0]:.2f} USD")
    print(f"Value after trading: {portfolio_values.iloc[-1]:.2f} USD")
    print(f"Value if no trades: {data['Close'].iloc[-1] * 1000:.2f} USD\n")

# 3 charts for every stock
# without Williams R
trade_stock('BTC', 0)
trade_stock('INTC', 0)
trade_stock('NIKE', 0)
#with Williams R
trade_stock('BTC', 1)
trade_stock('INTC', 1)
trade_stock('NIKE', 1)
