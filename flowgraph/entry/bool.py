__all__ = 'Bool',

from ..backend import QCheckBox, blocked_signals
from .entry import Entry


class Bool(QCheckBox, Entry):
    def __init__(self, name=None, callback=None, default=False):
        QCheckBox.__init__(self)
        Entry.__init__(self, name, callback, default)

    def setName(self, name):
        super().setName(name)
        self.setText(name)

    def value(self):
        return self.isChecked()

    def setValue(self, value):
        return self.setChecked(value)

    def setValueSilently(self, value):
        with blocked_signals(self):
            return self.setValue(value)
