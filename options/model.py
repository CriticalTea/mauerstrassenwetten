import matplotlib.pyplot as plt
from datetime import date, timedelta

from calc import *
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt

class Put:
    def __init__(self, strike, expiration, size=1):
        self.strike = strike
        self.expiration = expiration
        self.size = size

    def get_inner_value(self, underlying):
        return self.size*(self.strike-underlying)

    def get_price(self, underlying, expiration, iv):
        years = (self.expiration-expiration).days/365.0
        return self.size*black_scholes_put_price(underlying, self.strike, years, r, iv)

    def __str__(self):
        return "%sx Put %s (%s)" % (round(self.size, 3), round(self.strike,3), self.expiration)

class Call:
    def __init__(self, strike, expiration, size=1):
        self.strike = strike
        self.expiration = expiration
        self.size = size

    def get_inner_value(self, underlying):
        return self.size*(underlying-self.strike)

    def get_price(self, underlying, expiration, iv):
        years = (self.expiration-expiration).days/365.0
        return self.size*black_scholes_call_price(underlying, self.strike, years, r, iv)

    def __str__(self):
        return "%sx Call %s (%s)" % (round(self.size,3), round(self.strike,3), self.expiration)

class Long:
    def __init__(self, option):
        self.option = option

    def get_inner_value(self, underlying):
        inner_value = self.option.get_inner_value(underlying)
        if (inner_value < 0):
            return 0
        return inner_value

    def get_price(self, underlying, expiration, iv):
        price = self.option.get_price(underlying, expiration, iv)
        if price > 0:
            return price
        else:
            return 0

    def get_cost(self, underlying, expiration, iv):
        return self.option.get_price(underlying, expiration, iv)

    def __str__(self):
        return "Long %s" % self.option

class Short:
    def __init__(self, option):
        self.option = option

    def get_inner_value(self, underlying):
        inner_value = self.option.get_inner_value(underlying)
        if (inner_value < 0):
            return 0
        return -1*inner_value
    
    def get_price(self, underlying, expiration, iv):
        price = self.option.get_price(underlying, expiration, iv)
        if price > 0:
            return -1*price
        else:
            return 0

    def get_cost(self, underlying, expiration, iv):
        return -1*self.option.get_price(underlying, expiration, iv)

    def __str__(self):
        return "Short %s" % self.option

class Scenario:
    def __init__(self, expiration, iv_factor, S, r, T):
        self.expiration = expiration
        self.iv_factor = iv_factor
        self.S = S
        self.r = r
        self.T = T
    