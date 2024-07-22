__all__ = 'Widget',


from debug import debug
from . import node, entry
from .constrained import ClampedInt, ClampedFloat
from .backend import QContextMenuEvent, populate_menu, with_error_message
from inspect import signature, Parameter
from .util import get_static_object_from_state, static_object_state, split_at, toggle, ignore_args


def default(param: Parameter):
    return param.default if param.default != Parameter.empty else None


def cast(param: Parameter):
    anno = param.annotation
    return anno if anno and anno != Parameter.empty else lambda x: x


class Widget(node.Widget):
    def __init__(self, func=None):
        self.n_actions = 0
        super().__init__()
        self.func = None
        if func is not None:
            self.setFunction(func)

    def function(self):
        return self.func

    def setFunction(self, func, *, no_entries=False):
        self.setTitle(func.__name__)
        self.func = func
        self.signature = signature(func)

        if no_entries:
            return

        for param in self.signature.parameters.values():
            e = self.createEntry(param)
            e.input().setEnabled(True)
            if isinstance(e, entry.Generic):
                e.setLines(1)
            self.addEntry(e)

        return_param = Parameter('return', Parameter.POSITIONAL_ONLY, annotation=self.signature.return_annotation)
        e = self.createEntry(return_param, True)
        e.output().setEnabled(True)
        #e.setLines(5)
        e.setReadOnly(True)
        self.addEntry(e)

        if not hasattr(func, '__actions__'):
            return

        for name, callback in func.__actions__.items():
            Button = entry.ToggleButton if getattr(callback, '__toggle__', False) else entry.Button
            self.addEntry(Button(name, callback))
            self.n_actions += 1

        self.eval()

    def eval(self):
        arg_entries, result_entries = split_at(-1 - self.n_actions)(self.entries())
        assert len(arg_entries) == len(self.signature.parameters), f'{arg_entries} != {self.signature.parameters}'
        args = [
            cast(param)(arg_entry.value())
            for arg_entry, param in zip(arg_entries, self.signature.parameters.values())
        ]
        result = self.func(*args)
        for result_entry in result_entries:
            result_entry.setValue(result)
        return result

    def createEntry(self, param: Parameter, output=False):
        spec = param.annotation
        name = param.name
        callback = None if output else self.eval
        if issubclass(spec, ClampedInt):
            return entry.Int(name, callback, default(param) or 0, start=spec.spec.start, stop=spec.spec.stop, step=spec.spec.step)
        if issubclass(spec, ClampedFloat):
            return entry.Float(name, callback, default(param) or 0, start=spec.spec.start, stop=spec.spec.stop, step=spec.spec.step)
        if issubclass(spec, int):
            return entry.Int(name, callback, default(param) or 0)
        if issubclass(spec, float):
            return entry.Float(name, callback, default(param) or 0.0)
        if issubclass(spec, str):
            return entry.Str(name, callback, default(param) or '')
        return entry.Generic(name, callback, default(param) or None)

    def iterState(self):
        yield from super().iterState()
        if self.function() is not None:
            yield 'function', static_object_state(self.function())
            yield 'n_actions', self.n_actions

    def setState(self, state):
        state = super().setState(state, missing='return')
        for key, value in state.items():
            if key == 'function':
                func = get_static_object_from_state(value)
                self.setFunction(func, no_entries=True)
            elif key == 'n_actions':
                self.n_actions = value
            else:
                raise KeyError(key)
        return self

    def rebuild(self):
        debug('FIXME', 'the rebuilt entries CANNOT be given new inputs; I have no idea why')
        self.removeAllEntries()
        self.n_actions = 0
        self.setFunction(self.func)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        Menu(self).exec(event.globalPos())


class Menu(node.Menu):
    def __init__(self, widget: Widget):
        super().__init__(widget)
        populate_menu(self, [
            ('&Rebuild', 'Ctrl+R', ignore_args(with_error_message(widget.rebuild))),
        ])
