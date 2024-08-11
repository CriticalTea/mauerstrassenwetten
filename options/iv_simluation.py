import matplotlib.pyplot as plt
from datetime import date, timedelta

from calc import *
from model import *
from ui import *
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt

r = 0.05

expiration = date(2024,12,20)
expirate_days = (expiration-date.today()).days
# T = expirate_days/365.0
# S = 206.74  # Aktueller Aktienkurs
# r = 0.05 # Risikofreier Zinssatz
K = 200  # Strike-Preis
market_price = 17.9 # Marktpreis der Option
scenario = Scenario(expiration, iv_factor=1, S=206.74, r=0.05, T=expirate_days/365.0)

iv = find_implied_volatility(scenario.S, K, scenario.T, scenario.r, market_price)
scenario.iv = iv

delta = 0.1

print(f"Implizite Volatilität for {K:.1f}: {iv:.4f}")

positions = [
    Long(Put(round((1-delta)*scenario.S),expiration)),
    Short(Put(round(scenario.S),expiration)),
    Short(Put(round(scenario.S),expiration)),
    Long(Put(round((1+delta)*scenario.S),expiration))
    ]


# TODO: different volas for put/call
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow(positions, scenario)
    mainWin.show()
    sys.exit(app.exec_())