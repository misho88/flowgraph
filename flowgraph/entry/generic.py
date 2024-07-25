__all__ = 'Generic',

from .entry import Entry
from ..backend import QTextEdit, pyqtSignal, QFontMetrics


class Generic(QTextEdit, Entry):
    valueChanged = pyqtSignal(object)

    def __init__(self, name=None, callback=None, default=None):
        super().__init__()
        self._value = None
        Entry.__init__(self, name, callback, default)
        self._lines = None
        #self.setLines(1)
        self.setReadOnly()

    def setName(self, name):
        super().setName(name)
        self.setPlaceholderText(name)

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self.setText(str(value) if value is not None else '')
        self.valueChanged.emit(value)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.valueChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.valueChanged.disconnect(callback)

    def setReadOnly(self, value=True):
        super().setReadOnly(True)

    def setLines(self, n):
        self._lines = n
        font = self.currentFont()
        metrics = QFontMetrics(font)
        line = metrics.lineSpacing()
        self.setFixedHeight(12 + n * line)

    def lines(self):
        return self._lines

    def iterState(self):
        yield from super().iterState()
        if self.lines() is not None:
            yield 'lines', self.lines()

    def setState(self, state, parent=None, missing='error'):
        state = super().setState(state, parent=parent, missing='return')
        rv = {} if missing == 'return' else None
        for key, value in state.items():
            if key == 'lines':
                self.setLines(value)
            elif missing == 'error':
                raise KeyError(next(iter(state)))
            elif missing == 'return':
                rv[key] = value  # type: ignore
        return rv

