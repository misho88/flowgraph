__all__ = 'Scatter',

from .entry import Entry
from ..backend import pyqtSignal
from pyqtgraph import PlotWidget, ScatterPlotItem
from debug import debug
from pandas import DataFrame
import numpy as np


class Scatter(PlotWidget, Entry):
    valueChanged = pyqtSignal(object)

    def __init__(self, name=None, callback=None, default=None):
        super().__init__()
        #self.enableMouse()
        Entry.__init__(self, name, callback, default)
        self.traces = []

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

        if isinstance(value, np.ndarray):
            if value.dtype == complex:
                x, y = value.real, value.imag
            else:
                x, y = value
        else:
            col, = value.columns
            x = value.index.to_numpy()
            y = value[col].to_numpy()

        n = 1
        while len(self.traces) < n:
            item = ScatterPlotItem()
            self.addItem(item)
            self.traces.append(item)

        while len(self.traces) > n:
            self.removeItem(self.traces.pop())

        for trace in self.traces:
            trace.setData(x, y)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.valueChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.valueChanged.disconnect(callback)
