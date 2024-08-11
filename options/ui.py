import matplotlib.pyplot as plt
from datetime import date, timedelta

from calc import *
from model import *
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt

delta = 0.1

class PlotCanvas(FigureCanvas):
    def __init__(self, positions, scenario, parent=None, width=5, height=4, dpi=100):
        self.positions = positions
        self.scenario = scenario
        self.underlying_values = list(range(round((1-3*delta)*scenario.S),round((1+3*delta)*scenario.S)))
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = fig
        super(PlotCanvas, self).__init__(fig)
        self.setParent(parent)
        self.axes = {}
        number_of_plots = len(positions)+1
        position_index = 1
        for position_index in range(0, len(positions)):
            self.axes[positions[position_index]] = self.fig.add_subplot(number_of_plots,1,position_index+1)
        self.axes[len(positions)] = self.fig.add_subplot(number_of_plots,1,len(positions)+1)
        self.plot()

    def plot_position(self, position):
            color = 'blue'
            plt = self.axes[position]
            plt.clear()
            plt.axhline(0, color='black', lw=1)
            plt.axvline(x=self.scenario.S, color='black',lw=1)
            plt.set_title(position)
            values = [ position.get_price(underlying, self.scenario.expiration, self.scenario.iv) for underlying in self.underlying_values]
            plt.plot(self.underlying_values,values,color)

    def plot_positions(self, positions):
        color = 'blue'
        plt = self.axes[len(positions)]
        plt.clear()
        values = [ get_profit(positions, underlying, self.scenario.expiration, iv = self.scenario.iv, iv_new=self.scenario.iv_factor * self.scenario.iv, S = self.scenario.S) for underlying in self.underlying_values]
        plt.plot(self.underlying_values,values, color)
        plt.axhline(0, color='black', lw=1)
        plt.axvline(x=self.scenario.S, color='black',lw=1)
        plt.set_title('Vola Factor = %s' % self.scenario.iv_factor)
        #plt.axhline(total_cost, color='green')
        plt.axhline(0, color='black', lw=1)
        plt.axvline(x=self.scenario.S, color='black',lw=1)
        self.figure.tight_layout()

    def plot(self):
        
        for position in self.positions:
            self.plot_position(position)
                
        self.plot_positions(self.positions)
        self.draw()

        #data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        #self.axes.plot(data, 'r-')  # 'r-' bedeutet rote Linie
        #self.axes.set_title('Simple Line Plot')
        #self.draw()

class MainWindow(QMainWindow):
    def __init__(self, positions, scenario):
        super().__init__()
        self.positions = positions
        self.scenario = scenario
        self.setWindowTitle("PyQt5 Line Plot Example")
        self.setGeometry(100, 100, 1600, 1200)

        # Haupt-Widget und Layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Erstellen des Plot-Widgets und Hinzufügen zum Layout
        self.plot_canvas = PlotCanvas(positions, scenario, main_widget,width=5, height=4)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.plot_canvas)

        # Erstellen des Sliders
        self.label_iv = QLabel()
        layout.addWidget(self.label_iv)
        self.update_iv_factor(100)

        self.slider_iv = QSlider(Qt.Horizontal, self)
        self.slider_iv.setMinimum(0)
        self.slider_iv.setMaximum(200)
        self.slider_iv.setValue(100)
        self.slider_iv.setTickPosition(QSlider.TicksBelow)
        self.slider_iv.setTickInterval(1)
        self.slider_iv.valueChanged.connect(self.update_iv_factor)
        self.slider_iv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.slider_iv)

        # Erstellen des Sliders
        self.label = QLabel()
        layout.addWidget(self.label)
        self.update_expiration(0)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(expirate_days)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_expiration)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.slider)
    
    def update_iv_factor(self, value):
        self.scenario.iv_factor = value / 100.0
        self.label_iv.setText(f"IV factor: {value}%")
        self.plot_canvas.plot()

    def update_expiration(self, value):
        expirate_days = value
        self.scenario.expiration = date.today()+timedelta(days=expirate_days)
        self.label.setText(f"Expiration Days: {value}, Expiration Date: {self.scenario.expiration}")
        self.plot_canvas.plot()