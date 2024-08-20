__all__ = 'Button', 'ToggleButton'

from ..backend import QPushButton, with_error_message
from .entry import Entry
from itertools import repeat


class Button(QPushButton, Entry):
    #triggered = pyqtSignal(object)

    def __init__(self, name=None, callback=None, default=None):
        super().__init__()
        Entry.__init__(self, name, callback, default)
        self.clicked.connect(self.onClicked)
        #if callback:
        #    self.addCallback(callback)
        self._value = None
        self.results = None

    def onClicked(self, checked):
        results = self.results if self.results is not None else repeat(None)
        self.results = [
            with_error_message(callback)(self, result)
            for callback, result in zip(self.callbacks(), results)
        ]
        #self.triggered.emit(self.value())

    def value(self):
        return self._value

    def setValue(self, value):
        self.setValueSilently(value)  # FIXME: should this emit something??

    def setValueSilently(self, value):
        self._value = value

    def addCallback(self, callback):
        super().addCallback(callback)
        #self.triggered.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        #self.triggered.disconnect(callback)

    def setName(self, name):
        self.setToolTip(name if name is not None else '')
        self._name = name
        self.setText(name)

    def setReadOnly(self, value=True):
        pass


class ToggleButton(Button):
    def __init__(self, name=None, callback=None, default=None):
        super().__init__(name, callback, default)
        self.setCheckable(True)
        self.styles = (
            'QPushButton { border-style: outset; border-width: 1px; border-color: green; }',
            'QPushButton { border-style: inset ; border-width: 1px; border-color: red  ; }',
        )
        self.setStyleSheet(self.styles[0])

    def setChecked(self, value):
        super().setChecked(value)
        self.setStyleSheet(self.styles[int(self.isChecked())])

    def onClicked(self, checked):
        super().onClicked(checked)
        self.setStyleSheet(self.styles[int(self.isChecked())])
