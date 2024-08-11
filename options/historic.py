import matplotlib.pyplot as plt
from datetime import date, timedelta

from calc import *
from model import *
from csv import *
import sys
import matplotlib.pyplot as plt
import math
import numpy


snp = read_csv('SnP500.csv')
vix = read_csv('VIX.csv')

snp_dates = sorted(snp.keys())
vix_dates = sorted(vix.keys())
historic_vola = {}

vola_days = 30
for d in range(1, len(snp_dates)-vola_days):
    daily_log_returns = []
    for days in range(0, vola_days):
        daily_log_return = math.log(snp[snp_dates[d+days]]['Close']/snp[snp_dates[d+days-1]]['Close'])
        daily_log_returns.append(daily_log_return)
    mean = sum(daily_log_returns)/len(daily_log_returns)
    sigma = math.sqrt(sum([(r-mean)**2 for r in daily_log_returns])/(len(daily_log_returns)-1))
    sigma *= 100 * math.sqrt(252)
    historic_vola[snp_dates[d]] = sigma
    if snp_dates[d] < date(1990,2,1):
        print(snp_dates[d])
        #print(snp_dates[d], sigma*math.sqrt(252))
        #print(daily_log_returns)
        #print(mean)
        #print(sigma)
        #print(math.sqrt(252))
        print(sigma)


factor = 0.9
expiration = timedelta(30)
r = 0.05
profit = 0

prices = {}
profits = {}
cashflows = {}
positions = []

plot_days = 360*100
start_date = None
spread = 0.05

for today in vix_dates:
    if today not in snp_dates:
        continue
    if today < date(2000,1,1):
        continue
    if start_date == None:
        start_date = today
    if today > start_date + timedelta(days=plot_days):
        break
    # sell put option
    snp_today = snp[today]['Close']
    daily_cashflow = 0
    print(today, "S&P500", snp_today)
    for position in [Short(Put(0.9*snp_today, today + expiration)), Long(Put(0.80*snp_today, today + expiration))]:
        positions.append(position)
        price = black_scholes_put_price(snp_today,position.option.strike,30/360,r, vix[today]['Close']/100.0)
        size = 100/(0.1*snp_today)
        position.option.size = size
        if isinstance(position, Long):
            profit -= price*size*(1+spread/2)
            daily_cashflow -= price*size
            print(today, "OPEN", position, "profit", round(profit*size*-1,2))
        else:
            profit += price*size*(1-spread/2)
            daily_cashflow += price*size
            print(today, "OPEN", position, "profit", round(profit*size,2))
        prices[today] = price
    # execute expired options
    for position in positions:
        if position.option.expiration <= today:
            positions.remove(position)
            price = black_scholes_put_price(snp_today,position.option.strike,0/360,r, vix[today]['Close']/100.0)
            if isinstance(position, Short):
                put_profit = -1*price*position.option.size
            else:
                put_profit = price*position.option.size
            # put_profit = position.get_inner_value(snp_today)
            daily_cashflow += price*size
            profit += put_profit

            # if isinstance(position, Short):
            print(today, "CLOSE", position, "profit", round(put_profit,2))
    profits[today] = profit
    cashflows[today] = daily_cashflow
    print(today, "PROFIT", profit)
    print('')



r = 0.05


snp_dates = snp_dates[1:-vola_days]
vix_dates = vix_dates[1:]
# plt.plot(snp_dates[:plot_days], [historic_vola[d] for d in snp_dates[:plot_days]], 'b', vix_dates[:plot_days], [vix[d]['Close'] for d in vix_dates[:plot_days]], 'gray')
plot_col = 4
plt.subplot(plot_col,1,1)
plt.plot(snp_dates[:plot_days], [snp[d]['Close'] for d in snp_dates[:plot_days]], 'r', label='S&P500')
plt.title('S&P500')

plt.subplot(plot_col,1,2)
plt.plot(snp_dates[:plot_days], [historic_vola[d] for d in snp_dates[:plot_days]], 'b', label='Historic')
plt.plot(vix_dates[:plot_days], [vix[d]['Close'] for d in vix_dates[:plot_days]], 'r', label='VIX')
plt.legend()
plt.title('Volatilität')
plt.subplot(plot_col,1,3)

prices_dates = list(prices.keys())[:plot_days]
plt.plot(prices_dates, [prices[d] for d in prices_dates])
plt.title('Put Preise')

plt.subplot(plot_col,1,4)
profits_dates = list(profits.keys())[:plot_days]
plt.plot(profits_dates, [profits[d] for d in profits_dates])
plt.hlines(y=0,xmin=profits_dates[0],xmax=profits_dates[-1], colors=['black'])
plt.title('Gewinn/Verlust')
#plt.legend('historic', 'VIX')
#fig, ax1 = plt.subplots()
#ax1.plot(underlying_values, profit_values, 'red')
#ax2 = ax1.twinx()
#ax2.plot(underlying_values, probability_values, 'gray')
#fig.tight_layout()
plt.tight_layout()

start_date = min(cashflows.keys())
end_date = max(cashflows.keys())
cashflows[start_date] -= 3000
cashflows[end_date] += 3000

from scipy.optimize import newton

def npv(rate):
    start_date = min(cashflows.keys())
    result = 0
    for today in cashflows.keys():
        years = (today - start_date).days / 365
        result += cashflows[today]/((1+rate)**years)
    return result


irr = newton(npv, 0.1)
print(irr)

plt.show()
