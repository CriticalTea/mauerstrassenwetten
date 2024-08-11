import matplotlib.pyplot as plt
from datetime import date, timedelta

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt

r = 0.05

from scipy.optimize import fsolve

import numpy as np
from scipy.stats import norm

def get_profit(positions, underlying, expiration_new, iv, iv_new, S):
    profit = 0
    for position in positions:
        profit += position.get_price(underlying, expiration_new, iv_new) - position.get_cost(S, date.today(), iv)
    return profit

def find_profit_area(positions, expiration_new, iv, iv_new, S):
    def objective_function(underlying):
        return get_profit(positions, underlying, expiration_new, iv, iv_new, S)

    initial_guess = 0.2
    
    low = fsolve(objective_function, S*0.9)[0]
    high = fsolve(objective_function, S*1.1)[0]
    return [low, high]


def black_scholes_call_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

def black_scholes_put_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

def find_implied_volatility(S, K, T, r, market_price):
    # Zielfunktion: Unterschied zwischen Black-Scholes-Preis und Marktpreis
    def objective_function(sigma):
        return black_scholes_call_price(S, K, T, r, sigma) - market_price

    # Initialer Volatilitätsschätzwert
    initial_guess = 0.2
    
    # Finden der impliziten Volatilität
    implied_vol = fsolve(objective_function, initial_guess)[0]
    return implied_vol
