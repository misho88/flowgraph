__all__ = (
    'partial', 'ignore_args', 'call_all', 'cache', 'wraps',
    'get_static_object', 'get_static_object_from_state', 'get_object', 'get_object_from_state',
    'static_object_state', 'bound_method_state', 'object_state', 'split_at',
    'with_actions', 'toggle',
)

from functools import partial, wraps, cache
from importlib import import_module
from types import MethodType
from debug import debug
from funcpipes import Pipe


@Pipe
def ignore_args(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func()
    return inner


@Pipe
def call_all(*fs):
    def call():
        for f in fs:
            f()
    return call


@cache
def get_static_object(module, qualname, *, package=None):
    root = import_module(module, package)
    for name in qualname.split('.'):
        root = getattr(root, name)
    return root


def get_static_object_from_state(state):
    m = state['__module__']
    n = state['__qualname__']
    return get_static_object(m, n)


def get_object(module, qualname, self=None, *, package=None):
    cls_or_fun = get_static_object(module, qualname, package=package)
    if self is None:
        return cls_or_fun
    if not callable(cls_or_fun):
        raise TypeError('{repr(cls_or_fun)} is not callable')
    return MethodType(cls_or_fun, self)


def get_object_from_state(state, self=None):
    m = state['__module__']
    n = state['__qualname__']
    if '__self__' not in state:
        return get_static_object(m, n)

    s = get_static_object_from_state(state['__self__'])
    if type(self) is not s:
        raise TypeError(f'{self=} is not of type {repr(s)}')

    return get_object(m, n, self)  # FIXME: something stricter?


def static_object_state(obj):
    return dict(
        __module__=obj.__module__,
        __qualname__=obj.__qualname__,
    )


def bound_method_state(obj):
    return dict(
        __module__=obj.__module__,
        __qualname__=obj.__qualname__,
        __self__=static_object_state(type(obj.__self__)),  # FIXME: or something
    )


def object_state(obj):
    f = bound_method_state if isinstance(obj, MethodType) else static_object_state
    return f(obj)


def split_at(n):
    def inner(seq):
        return seq[:n], seq[n:]
    return inner


def with_actions(actions: dict):
    def add_actions(func):
        func.__actions__ = actions
        return func
    return add_actions


def toggle(func):
    func.__toggle__ = True
    return func
