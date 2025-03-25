__all__ = 'Combo',

from .entry import Entry
from ..backend import QComboBox


class Combo(QComboBox, Entry):
    def __init__(self, name=None, callback=None, default='', options=[]):
        if not default and options:
            default = options[0]

        super().__init__()
        Entry.__init__(self, name, callback, default)
        self.addItems(options)

    def setName(self, name):
        super().setName(name)
        self.setPlaceholderText(name)

    def value(self) -> str:
        return self.currentText()

    def setValue(self, value: str):
        return self.setCurrentText(value)

    def setValueSilently(self, value: str):
        prev = self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(prev)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.currentTextChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.currentTextChanged.disconnect(callback)

