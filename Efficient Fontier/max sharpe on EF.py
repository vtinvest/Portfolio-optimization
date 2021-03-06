import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier
import datetime as dt


# 1 get dataa
ticker = ['tsla', 'goog', 'aapl']
today = dt.date.today()

df = pd.DataFrame()
for t in ticker:
    df[t] = yf.download(t, start="2021-01-01", end=today)['Adj Close']

(df / df.iloc[0] * 100).plot(figsize=(10, 5))
logreturns = np.log(df / df.shift(1))
logmean = logreturns.mean()
logmeanyr = logreturns.mean() * 250
cov = logreturns.cov() * 250
corr = logreturns.corr()
num_ticker = len(ticker)
arr = np.random.random(num_ticker)
weights = np.random.random(num_ticker)
weights /= np.sum(weights)
sum_weights = sum(weights)

# 2 monte carlo
pfolio_returns = []
pfolio_volatilities = []
sharpe_ratio = []

for x in range(10000):
    weights = np.random.random(num_ticker)
    weights /= np.sum(weights)

    pfolio_returns.append(np.sum(weights * logreturns.mean()) * 250)
    pfolio_volatilities.append(np.sqrt(np.dot(weights.T, np.dot(logreturns.cov() * 250, weights))))

pfolio_returns = np.array(pfolio_returns)
pfolio_volatilities = np.array(pfolio_volatilities)
portfolio = pd.DataFrame({'Return': pfolio_returns, 'Volatility': pfolio_volatilities})

# 3 portfolio mean returns
mu = np.sum(weights * logreturns.mean()) * 250
# 4 portfolio volatility
std = np.dot(weights.T, np.dot(logreturns.cov() * 250, weights)) ** 0.5

# 5 Optimize for maximal Sharpe rati
sharpe_ratio = pfolio_returns / pfolio_volatilities
portfolio.plot(x='Volatility', y='Return', kind='scatter', figsize=(9, 5));
plt.xlabel('Expected Volatility')
plt.ylabel('Expected Return')
plt.show()


mu = expected_returns.mean_historical_return(df)
S = risk_models.sample_cov(df)
ef = EfficientFrontier(mu, S)
raw_weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()

ef.save_weights_to_file("weights2.csv")  # saves to file
ef.portfolio_performance(verbose=True)
print(cleaned_weights)
