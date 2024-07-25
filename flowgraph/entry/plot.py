__all__ = 'Plot',

from .entry import Entry
from pyqtgraph import PlotWidget
from debug import debug


class Plot(PlotWidget, Entry):
    def __init__(self, name=None, callback=None, default=''):
        super().__init__()
        Entry.__init__(self, name, callback, default)
        self.traces = []

    def setReadOnly(self, value):
        pass

    def setName(self, name):
        super().setName(name)
        #self.setPlaceholderText(name)

    def value(self) -> str:
        return self._value

    def setValue(self, value):
        self._value = value
        x = value.index.to_numpy()

        n = len(value.columns)

        while len(self.traces) < n:
            self.traces.append(self.plot())

        while len(self.traces) < n:
            self.removeItem(self.traces.pop())

        for trace, column in zip(self.traces, value.columns):
            y = value[column].to_numpy()
            trace.setData(x, y)

    def addCallback(self, callback):
        super().addCallback(callback)
        #self.textChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        #self.textChanged.disconnect(callback)
