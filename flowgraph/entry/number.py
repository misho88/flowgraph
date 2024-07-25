__all__ = 'Number',

from .entry import Entry


class Number(Entry):
    def __init__(self, name=None, callback=None, default: int | float = 0, start=None, stop=None, step=None):
        if start is not None:
            self.setMinimum(start)
        if stop is not None:
            self.setMaximum(stop)
        if step is not None:
            self.setSingleStep(step)

        # DO THIS LAST:
        super().__init__(name, callback, default)

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

    def iterState(self):
        yield from super().iterState()
        yield 'start', self.minimum()
        yield 'stop', self.maximum()
        yield 'step', self.singleStep()

    def setState(self, state, parent=None):
        rest = {}
        for key, value in (state.items() if isinstance(state, dict) else state):
            if key == 'start':
                self.setMinimum(value)
            elif key == 'stop':
                self.setMaximum(value)
            elif key == 'step':
                self.setSingleStep(value)
            else:
                rest[key] = value
        return super().setState(rest, parent=parent)

    def minimum(self):
        raise NotImplementedError(type(self))

    def setMinimum(self, value):
        raise NotImplementedError(type(self))

    def maximum(self):
        raise NotImplementedError(type(self))

    def setMaximum(self, value):
        raise NotImplementedError(type(self))

    def singleStep(self):
        raise NotImplementedError(type(self))

    def setSingleStep(self, value):
        raise NotImplementedError(type(self))

    @property
    def valueChanged(self):
        raise NotImplementedError(type(self))
