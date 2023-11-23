import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


today = datetime.today().strftime('%Y-%m-%d')
tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')


def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][-1]

data = yf.download('BTC-USD', start='2022-01-01', end=tomorrow, interval='1d')

window = 7

data['Max'] = data.iloc[argrelextrema(data['Close'].values, np.greater_equal, order=window)[0]]['Close']
data['Min'] = data.iloc[argrelextrema(data['Close'].values, np.less_equal, order=window)[0]]['Close']

current_price = get_current_price('BTC-USD')

data['EMA_200'] = data['Close'].ewm(span=200).mean()

data['Fakeout'] = np.nan

for i in range(2, len(data) - 2):
    if data['Close'].iloc[i - 1] < data['Max'].iloc[i - 2]:
        if data['High'].iloc[i] > data['Max'].iloc[i - 2] and data['Close'].iloc[i] < data['Max'].iloc[i - 2]:
            data.at[data.index[i], 'Fakeout'] = data['High'].iloc[i]

plt.figure(figsize=(15,7))
plt.plot(data.index, data['Close'], label='Kapanış Fiyatları', color='blue')
plt.plot(data.index, data['EMA_200'], label='EMA 200', color='orange')

for i in range(len(data['Max'])):
    if not np.isnan(data['Max'].iloc[i]) and data['Max'].iloc[i] > current_price:
        plt.hlines(y=data['Max'].iloc[i], xmin=data.index[i], xmax=data.index[-1], colors='red')

for i in range(len(data['Min'])):
    if not np.isnan(data['Min'].iloc[i]) and data['Min'].iloc[i] < current_price:
        plt.hlines(y=data['Min'].iloc[i], xmin=data.index[i], xmax=data.index[-1], colors='green')

plt.scatter(data.index, data['Fakeout'], color='black', label='Fake Fitilleri')
plt.title('Bitcoin Support, Resistance, EMA 200 & Fakes')
plt.xlabel('date')
plt.ylabel('price')
plt.legend()
plt.grid()
plt.show()

latest_resistance = data['Max'][data['Max']>current_price]
if len(latest_resistance) > 0:
    nearest_resistance = min(latest_resistance)
    print(f"Nearest resistance: {nearest_resistance}")
else:
    print("Nearest resistance could not find.")

latest_support = data['Min'][data['Min']<current_price]
if len(latest_support) > 0:
    nearest_support = max(latest_support)
    print(f"Nearest support: {nearest_support}")
else:
    print("Nearest support could not find.")

current_price = get_current_price('BTC-USD')
print(f"Price: {current_price}")
