__all__ = 'Entry',

from debug import debug
from .. import socket
from ..util import object_state, get_object_from_state
from ..stateful import Stateful
from dill import loads, dumps
from base64 import b64decode, b64encode


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
        raise NotImplementedError(type(self))

    def setReadOnly(self, value):
        raise NotImplementedError(type(self))

    def value(self):
        raise NotImplementedError(type(self))

    def setValue(self, value):
        raise NotImplementedError(type(self))

    def setValueSilently(self, value):
        raise NotImplementedError(type(self))

    def setValueIfDifferent(self, value):
        if self.value() != value:
            self.setValue(value)

    def setValueSilentlyIfDifferent(self, value):
        if self.value() != value:
            self.setValueSilently(value)

    def parent(self):
        raise NotImplementedError(type(self))

    def setParent(self, value):
        raise NotImplementedError(type(self))

    def addCallback(self, callback):
        self._callbacks.append(callback)

    def removeCallback(self, callback):
        self._callbacks.remove(callback)

    def callbacks(self):
        return self._callbacks.copy()

    def removeAllCallbacks(self):
        for callback in self.callbacks():
            self.removeCallback(callback)

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
        if self.value() is not None:
            yield 'value', b64encode(dumps(self.value())).decode()
        yield 'callbacks', [ object_state(callback) for callback in self.callbacks() ]

    def setState(self, state, parent=None, missing='error'):
        state = super().setState(state, missing='return')
        assert isinstance(state, dict)
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
                        pass
                        #debug(f'skipping callback: {e}')
            elif missing == 'error':
                raise KeyError(key)
            elif missing == 'return':
                rv[key] = value  # type: ignore
        return rv

    def remove(self):
        parent = self.parent()
        self.setParent(None)
        self.unsetSource()
        self.removeAllCallbacks()
        parent.layout().removeWidget(self)


