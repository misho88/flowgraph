__all__ = 'Int',

from ..backend import QSpinBox
from .number import Number


class Int(QSpinBox, Number):
    def __init__(self, name=None, callback=None, default=0, start=None, stop=None, step=None):
        QSpinBox.__init__(self)
        Number.__init__(self, name=name, callback=callback, default=default, start=start, stop=stop, step=step)
