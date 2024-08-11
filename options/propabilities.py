import matplotlib.pyplot as plt
from datetime import date, timedelta

from calc import *
from model import *
import sys
import matplotlib.pyplot as plt

r = 0.05

expiration = date(2024,9,12)
expirate_days = (expiration-date.today()).days
T = expirate_days/365.0
S = 100.  # Aktueller Aktienkurs
r = 0.05 # Risikofreier Zinssatz
K = 100  # Strike-Preis
#market_price = 2.11 # Marktpreis der Option

# iv = find_implied_volatility(S, K, T, r, market_price)

iv = 0.1
delta = 0.1

positions = [
    Short(Put(80,expiration)),
    Long(Put(90,expiration)),
    Long(Put(110,expiration)),
    Short(Put(120,expiration))
    ]

    #Long(Put(round((1-delta)*S),expiration)),
    #Short(Put(round(S),expiration)),
    #Short(Put(round(S),expiration)),
    #Long(Put(round((1+delta)*S),expiration))

for position in positions:
    print("%s: %s" % (position, round(position.get_cost(S, date.today(), iv), 3)))

total_cost = sum([position.get_cost(S, date.today(),iv) for position in positions])
print("Total: %s" % total_cost)

profit_area = find_profit_area(positions, expiration, iv, iv, S)
print(f"Current price underlying f{S}")
print(f"Implizite Volatilität for {K:.1f}: {iv:.4f}")

propability_function = norm(loc=S, scale=iv*S)
profit_delta_absolute = [profit - S for profit in profit_area]
profit_delta_relative = [(profit - S)/S for profit in profit_area]
profit_delta_std = [(profit - S)/(iv*S) for profit in profit_area]
profit_propability = propability_function.cdf(profit_area[1])-propability_function.cdf(profit_area[0])
print(profit_area)
print(profit_delta_absolute)
print(profit_delta_relative)
print(profit_delta_std)
print("Gewinnwahrscheinlichkeit:", profit_propability)

def get_profit_from_underlying(underlying):
    return get_profit(positions, underlying, expiration, iv, iv, S)

underlying_values = list(range(70,130))
profit_values = [get_profit_from_underlying(underlying) for underlying in underlying_values]
probability_values = [propability_function.pdf(underlying) for underlying in underlying_values]

expected_profit = propability_function.expect(get_profit_from_underlying)
print("Erwartungswert", expected_profit)

# plt.plot(underlying_values, profit_values, 'b', underlying_values, probability_values, 'gray')
fig, ax1 = plt.subplots()
ax1.plot(underlying_values, profit_values, 'red')
ax2 = ax1.twinx()
ax2.plot(underlying_values, probability_values, 'gray')
fig.tight_layout()
plt.show()