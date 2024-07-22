__all__ = 'Stateful',

from .backend import QApplication
from debug import debug
from json import loads, dumps


class Stateful:
    def __init__(self):
        self._state = {}
        if type(self) is Stateful:
            raise NotImplementedError

    def iterState(self):
        yield '__module__', type(self).__module__
        yield '__qualname__', type(self).__qualname__
        yield from self._state.items()

    def state(self):
        return dict(self.iterState())

    def setState(self, state, missing='error', return_dunder=False):
        '''apply the state

        state: dict-like or sequence of key-value pairs
        missing: what to do when a key is not present in the object's state:
                 - 'add': add it anyway
                 - 'skip': skip it
                 - 'return': skip it, but also return it in a dictionary
                 - 'error' (default): raise a KeyError
        '''
        if missing not in ('add', 'skip', 'return', 'error'):
            raise ValueError(f"{missing=} must be 'add', 'skip', 'return' or 'error'")
        if isinstance(state, dict):
            state = state.items()

        retval = {} if missing == 'return' else None
        for key, value in state:
            if key.startswith('__'):
                if missing == 'return' and return_dunder:
                    retval[key] = value  # type: ignore
            elif missing == 'add' or key in self._state:
                self._state[key] = value
            elif missing == 'error':
                raise KeyError(key)
            elif missing == 'return':
                retval[key] = value  # type: ignore
        return retval

    @classmethod
    def fromState(cls, *args, **kwargs):
        '''create object from state

        same as `obj(); obj.setState(*args, **kwargs)`

        state: the state
        *args, **kwargs: passed to cls's initializer/constructor
        '''
        obj = cls()
        obj.setState(*args, **kwargs)
        return obj

    def json(self):
        return dumps(self.state())

    def toClipboard(self):
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(self.json())
