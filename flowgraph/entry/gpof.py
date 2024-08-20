__all__ = 'Gpof',

from .entry import Entry
from ..backend import pyqtSignal
from pyqtgraph import PlotWidget
from debug import debug
from pandas import DataFrame

import numpy as np


def pencil(x, width=None, copy=False, writeable=False):
    assert x.ndim == 1, "input must be 1-D"
    if width is None:
        width = len(x) // 2

    height = len(x) - width + 1
    stride, = x.strides
    p = np.lib.stride_tricks.as_strided(
        x=x,
        shape=(height, width),
        strides=(stride, stride),
        writeable=writeable,
    )
    return p.copy() if copy else p


def gpof(y, n_poles=None, width=None):
    if width is None:
        width = len(y) // 2
    if n_poles is None:
        n_poles = width
    if n_poles > width:
        raise ValueError(f'need {n_poles=} <= {width=}')

    Y = pencil(y, width=width)
    Y0, Y1 = (Y[i:i + width] for i in (0, 1))
    U, σ, VH = np.linalg.svd(Y0, full_matrices=False)
    U, σ, VH = U[:, :n_poles], σ[:n_poles], VH[:n_poles, :]

    sysmat = (U.conj() / σ).T @ Y1 @ VH.conj().T
    poles = np.linalg.eigvals(sysmat)
    idx = np.angle(poles).argsort()
    return poles[idx]


class Gpof(PlotWidget, Entry):
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
        if value is None:
            return

        self._value = value
        self.valueChanged.emit(value)

        #x = value.index.to_numpy()
        n = len(value.columns)

        while len(self.traces) < n:
            self.traces.append(self.plot())

        while len(self.traces) > n:
            self.removeItem(self.traces.pop())

        for trace, column in zip(self.traces, value.columns):
            y = value[column].to_numpy()
            trace.setData(x, y)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.valueChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.valueChanged.disconnect(callback)
