__all__ = 'Str',

from .entry import Entry
from ..backend import QLineEdit


class Str(QLineEdit, Entry):
    def __init__(self, name=None, callback=None, default=''):
        super().__init__()
        Entry.__init__(self, name, callback, default)

    def setName(self, name):
        super().setName(name)
        self.setPlaceholderText(name)

    def value(self) -> str:
        return self.text()

    def setValue(self, value: str):
        return self.setText(value)

    def setValueSilently(self, value: str):
        prev = self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(prev)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.textChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.textChanged.disconnect(callback)
