__all__ = 'Widget',


from debug import debug
from . import node, entry
from .constrained import ClampedInt, ClampedFloat
from .backend import QContextMenuEvent, populate_menu, with_error_message, pyqtSlot, pyqtSignal
from inspect import signature, Parameter
from .util import get_static_object_from_state, static_object_state, split_at, ignore_args
from funcpipes import nothing

try:
    from pandas import DataFrame  # type: ignore
except ImportError:
    class DataFrame:
        pass


def default(param: Parameter):
    return param.default if param.default != Parameter.empty else None


def cast(param: Parameter):
    anno = param.annotation
    return anno if anno and anno != Parameter.empty else lambda x: x


class Widget(node.Widget):
    trigger = pyqtSignal()

    def __init__(self, func=None):
        self.n_args = self.n_returns = self.n_actions = 0
        super().__init__()
        self.func = None
        if func is not None:
            self.setFunction(func)

        self.trigger.connect(self.eval)

    def function(self):
        return self.func

    def setFunction(self, func, *, no_entries=False):
        self.setTitle(func.__name__)
        self.func = func
        self.signature = signature(func)

        if no_entries:
            return

        self.removeAllEntries()

        for param in self.signature.parameters.values():
            e = self.createEntry(param)
            e.input().setEnabled(True)
            e.output().setEnabled(True)
            if isinstance(e, entry.Generic):
                e.setLines(1)
            self.addEntry(e)
            self.n_args += 1

        return_annotations = self.signature.return_annotation
        if not isinstance(return_annotations, tuple):
            return_annotations = return_annotations,

        for i, return_annotation in enumerate(return_annotations):
            return_param = Parameter(
                f'return{i}' if len(return_annotations) > 1 else 'return',
                Parameter.POSITIONAL_ONLY,
                annotation=return_annotation,
            )
            e = self.createEntry(return_param, True)
            e.output().setEnabled(True)
            e.setReadOnly(True)
            self.addEntry(e)
            self.n_returns += 1

        if not hasattr(func, '__actions__'):
            return

        for name, callback in func.__actions__.items():
            Button = entry.ToggleButton if getattr(callback, '__toggle__', False) else entry.Button
            self.addEntry(Button(name, callback))
            self.n_actions += 1

        self.eval()

    def eval(self):
        assert self.func is not None

        try:
            self.setErrrored(False)
            entries = self.entries()
            arg_entries, entries = split_at(self.n_args)(entries)
            return_entries, entries = split_at(self.n_returns)(entries)
            action_entries, entries = split_at(self.n_actions)(entries)
            assert len(entries) == 0, entries
            assert len(arg_entries) == len(self.signature.parameters), f'{arg_entries} != {self.signature.parameters}'

            args = [
                cast(param)(arg_entry.value())
                for arg_entry, param in zip(arg_entries, self.signature.parameters.values())
            ]
            results = self.func(*args)
            if results is nothing:
                debug('got nothing')
                return

            for e in action_entries:
                e.setValue(results)

            if self.n_returns == 1:
                return_entries[0].setValue(results)
                return results

            assert len(return_entries) == len(results), (return_entries, results)
            for return_entry, result in zip(return_entries, results):
                return_entry.setValue(result)

            return results
        except Exception as e:
            from traceback import print_exception
            print_exception(e)
            self.setErrrored(True)

    def createEntry(self, param: Parameter, output=False):
        spec = param.annotation
        name = param.name
        callback = None if output else self.eval
        if issubclass(spec, ClampedInt):
            return entry.Int(
                name, callback, default(param) or 0,
                start=spec.spec.start, stop=spec.spec.stop, step=spec.spec.step
            )
        if issubclass(spec, ClampedFloat):
            return entry.Float(
                name, callback, default(param) or 0.0,
                start=spec.spec.start, stop=spec.spec.stop, step=spec.spec.step
            )
        if issubclass(spec, int):
            return entry.Int(name, callback, default(param) or 0)
        if issubclass(spec, float):
            return entry.Float(name, callback, default(param) or 0.0)
        if issubclass(spec, str):
            return entry.Str(name, callback, default(param) or '')
        if issubclass(spec, DataFrame):
            return entry.Plot(name, callback, default(param) or None)
        return entry.Generic(name, callback, default(param) or None)

    def iterState(self):
        yield from super().iterState()
        if self.function() is not None:
            yield 'function', static_object_state(self.function())
            yield 'n_args', self.n_args
            yield 'n_returns', self.n_returns
            yield 'n_actions', self.n_actions

    def setState(self, state):
        state = super().setState(state, missing='return')
        assert isinstance(state, dict)

        for key, value in state.items():
            if key == 'function':
                func = get_static_object_from_state(value)
                self.setFunction(func, no_entries=True)
            elif key in ('n_args', 'n_returns', 'n_actions'):
                setattr(self, key, value)
            else:
                raise KeyError(key)
        return self

    def rebuild(self):
        debug('FIXME', 'the rebuilt entries CANNOT be given new inputs; I have no idea why')
        self.setFunction(self.func)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        Menu(self).exec(event.globalPos())

    def removeAllEntries(self):
        super().removeAllEntries()
        self.n_args = self.n_returns = self.n_actions = 0


class Menu(node.Menu):
    def __init__(self, widget: Widget):
        super().__init__(widget)
        populate_menu(self, [
            ('&Rebuild', 'Ctrl+R', ignore_args(with_error_message(widget.rebuild))),
        ])
