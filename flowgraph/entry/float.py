__all__ = 'Float',

from ..backend import QDoubleSpinBox
from .number import Number
from debug import debug


class Float(QDoubleSpinBox, Number):
    def __init__(self, name=None, callback=None, default=0.0, start=None, stop=None, step=None):
        QDoubleSpinBox.__init__(self)
        Number.__init__(self, name=name, callback=callback, default=default, start=start, stop=stop, step=step)
        if step is not None:
            self.setDecimals(len(str(round(step % 1.0, 6))) - 2)

    def iterState(self):
        yield from super().iterState()
        yield 'decimals', self.decimals()

    def setState(self, state, parent=None):
        rest = {}
        for key, value in (state.items() if isinstance(state, dict) else state):
            if key == 'decimals':
                self.setDecimals(value)
            else:
                rest[key] = value
        return super().setState(rest, parent=parent)
