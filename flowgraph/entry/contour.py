__all__ = 'Contour',

from .entry import Entry
from ..backend import pyqtSignal
from pyqtgraph import PlotWidget, ScatterPlotItem, ImageView
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import matplotlib.pyplot as plt
from debug import debug
from pandas import DataFrame


class Contour(MatplotlibWidget, Entry):
    valueChanged = pyqtSignal(object)

    def __init__(self, name=None, callback=None, default=None):
        super().__init__()

        fig = self.getFigure()
        fig.set_size_inches(3.5, 3.5 * 3 / 4)

        #self.enableMouse()
        Entry.__init__(self, name, callback, default)

    def setReadOnly(self, value):
        pass

    def setName(self, name):
        super().setName(name)
        #self.setPlaceholderText(name)

    def value(self):
        return self._value

    def setValue(self, value):
        self.setValueSilently(value)
        self.valueChanged.emit(value)

    def setValueSilently(self, value):
        if value is None:
            return

        self._value = value

        fig = self.getFigure()
        fig.clf()
        ax = fig.add_subplot(111)

        if isinstance(value, dict):
            for k, v in value.items():
                if k == 'value':
                    X, Y, Z = v
                else:
                    getattr(ax, f'set_{k}')(v)
        else:
            X, Y, Z = value

        cntr = ax.contourf(X, Y, Z, cmap='plasma')
        plt.colorbar(cntr)

        ax.add_artist(plt.Circle((0, 0), 1, fill=False, color='gray'))

        self.canvas.draw()
        self.canvas.flush_events()

    def addCallback(self, callback):
        super().addCallback(callback)
        self.valueChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.valueChanged.disconnect(callback)

