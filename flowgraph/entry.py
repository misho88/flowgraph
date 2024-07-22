__all__ = 'Str', 'Int', 'Float', 'read_only', 'Entry', 'Generic', 'Button', 'ToggleButton'


from debug import debug
from .backend import QWidget, QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit, pyqtSignal, QPushButton, QFontMetrics
from . import socket
from .util import object_state, get_object_from_state
from .stateful import Stateful
from dill import loads, dumps
from base64 import b64decode, b64encode
from itertools import repeat
from .backend import with_error_message


class Entry(Stateful):
    def __init__(self, name=None, callback=None, default=None):
        super().__init__()
        self._callbacks = []
        self._input, self._output = socket.Input(self), socket.Output(self)
        self._parentItem = None
        self.source = None
        self.setName(name)

        if default is not None:
            self.setValue(default)
        if callback is not None:
            self.addCallback(callback)

    def input(self):
        return self._input

    def output(self):
        return self._output

    def parentItem(self):
        return self._parentItem

    def setParentItem(self, item):
        self._parentItem = item
        self._input.setParentItem(item)
        self._output.setParentItem(item)
        return self

    def name(self):
        return self._name

    def setName(self, name):
        self.setToolTip(name if name is not None else '')
        self._name = name

    def setToolTip(self, text):
        raise NotImplementedError

    def setReadOnly(self, value):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    def addCallback(self, callback):
        self._callbacks.append(callback)

    def removeCallback(self, callback):
        self._callbacks.remove(callback)

    def callbacks(self):
        return self._callbacks

    def setSource(self, source):
        self.unsetSource()
        self.setValue(source.value())
        self.input().setSource(source.output())
        self.source = source
        source.addCallback(self.setValue)
        self.setReadOnly(True)

    def unsetSource(self):
        self.input().unsetSource()
        if self.source is not None:
            self.source.removeCallback(self.setValue)
            self.source = None
        self.setReadOnly(False)

    def iterState(self):
        yield from super().iterState()
        if self.name() is not None:
            yield 'name', self.name()
        yield 'input', self.input().state()
        yield 'output', self.output().state()
        yield 'value', b64encode(dumps(self.value())).decode()
        yield 'callbacks', [ object_state(callback) for callback in self.callbacks() ]

    def setState(self, state, parent=None, missing='error'):
        state = super().setState(state, missing='return')
        rv = {} if missing == 'return' else None
        for key, value in state.items():
            if key == 'name':
                self.setName(value)
            elif key == 'input':
                self.input().setState(value)
            elif key == 'output':
                self.output().setState(value)
            elif key == 'value':
                self.setValue(loads(b64decode(value)))
            elif key == 'callbacks':
                for callback_state in value:
                    try:
                        self.addCallback(get_object_from_state(callback_state, parent))
                    except TypeError as e:
                        debug(f'skipping callback: {e}')
            elif missing == 'error':
                raise KeyError(key)
            elif missing == 'return':
                rv[key] = value  # type: ignore
        return rv


def read_only(widget: QWidget):
    widget.setReadOnly(True)
    return widget


class Generic(QTextEdit, Entry):
    valueChanged = pyqtSignal(object)

    def __init__(self, name=None, callback=None, default=None):
        super().__init__()
        self._value = None
        Entry.__init__(self, name, callback, default)
        self._lines = None
        #self.setLines(1)
        self.setReadOnly()

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
        #if value is not True:
        #    raise ValueError('Generic must be read-only')
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

    def setState(self, state, parent=None):
        state = super().setState(state, parent=parent, missing='return')
        if 'lines' in state:
            self.setLines(state.pop('lines'))
        if state:
            raise KeyError(next(iter(state)))


class Str(QLineEdit, Entry):
    def __init__(self, name=None, callback=None, default=''):
        super().__init__()
        Entry.__init__(self, name, callback, default)

    def value(self) -> str:
        return self.text()

    def setValue(self, value: str):
        return self.setText(value)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.textChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.textChanged.disconnect(callback)


class Int(QSpinBox, Entry):
    def __init__(self, name=None, callback=None, default=0, start=None, stop=None, step=None):
        QSpinBox.__init__(self)
        Entry.__init__(self, name, callback, default)
        if start is not None:
            self.setMinimum(start)
        if stop is not None:
            self.setMaximum(stop)
        if step is not None:
            self.setSingleStep(step)

    def value(self):  # NOTE: CRITICAL FOR SERIALIZATION
        return super().value()

    def setValue(self, value):  # NOTE: CRITICAL FOR SERIALIZATION
        return super().setValue(value)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.valueChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.valueChanged.disconnect(callback)


class Float(QDoubleSpinBox, Entry):
    def __init__(self, name=None, callback=None, default=0.0, start=None, stop=None, step=None):
        QDoubleSpinBox.__init__(self)
        Entry.__init__(self, name, callback, default)
        if start is not None:
            self.setMinimum(start)
        if stop is not None:
            self.setMaximum(stop)
        if step is not None:
            self.setSingleStep(step)

    def value(self):  # NOTE: CRITICAL FOR SERIALIZATION
        return super().value()

    def setValue(self, value):  # NOTE: CRITICAL FOR SERIALIZATION
        return super().setValue(value)

    def addCallback(self, callback):
        super().addCallback(callback)
        self.valueChanged.connect(callback)

    def removeCallback(self, callback):
        super().removeCallback(callback)
        self.valueChanged.disconnect(callback)


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
