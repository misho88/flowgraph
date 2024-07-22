__all__ = 'Clamped', 'ClampedInt', 'ClampedFloat', 'Optioned', 'OptionedInt', 'OptionedFloat', 'OptionedStr'

from Levenshtein import distance
from debug import debug


def slice_str(s: slice):
    if s.start is not None:
        if s.stop is not None:
            if s.step is not None:
                return f'{s.start}:{s.stop}:{s.step}'
            else:
                return f'{s.start}:{s.stop}'
        else:
            if s.step is not None:
                return f'{s.start}::{s.step}'
            else:
                return f'{s.start}:'
    else:
        if s.stop is not None:
            if s.step is not None:
                return f':{s.stop}:{s.step}'
            else:
                return f':{s.stop}'
        else:
            if s.step is not None:
                return f'::{s.step}'
            else:
                return ':'


def tuple_str(t: tuple):
    return ', '.join(repr(item) for item in t)


class Clamped:
    spec = slice(None)

    @classmethod
    def round(cls, num, to):
        return round(num / to) * to

    def __new__(cls, value):
        if cls.spec.stop is not None and value > cls.spec.stop:
            value = cls.spec.stop
        if cls.spec.start is not None:
            if value < cls.spec.start:
                value = cls.spec.start
            elif cls.spec.step is not None:
                value = cls.spec.start + cls.round(value - cls.spec.start, cls.spec.step)
        elif cls.spec.step is not None:
            value = cls.round(value, cls.spec.step)
        return super().__new__(cls, value)  # type: ignore

    def __repr__(self):
        n = type(self).__name__
        r = super().__repr__()
        s = slice_str(self.spec)
        s = f'[{s}]' if s != ':' else ''
        return f'{n}{s}({r})'

    def __class_getitem__(cls, spec):
        if not isinstance(spec, slice):
            raise ValueError(f'{spec=} is not a slice')
        spec_ = spec

        class Sub(cls):  # type: ignore (I have no idea what PyRight wants here)
            spec = spec_

        Sub.__name__ = cls.__name__
        return Sub


class Optioned:
    spec = ()

    @classmethod
    def compare(cls, a, b):
        if isinstance(a, str):
            return distance(a.lower(), b.lower())
        return abs(a - b)

    def __new__(cls, value):
        value = min(cls.spec, key=lambda opt: cls.compare(value, opt))
        return super().__new__(cls, value)  # type: ignore

    def __repr__(self):
        n = type(self).__name__
        r = super().__repr__()
        t = tuple_str(self.spec)
        t = f'[{t}]' if t != '' else ''
        return f'{n}{t}({r})'

    def __class_getitem__(cls, spec):
        if not isinstance(spec, tuple):
            spec = spec,
        spec_ = spec

        class Sub(cls):  # type: ignore (I have no idea what PyRight wants here)
            spec = spec_

        Sub.__name__ = cls.__name__
        return Sub


class Constrained(Clamped, Optioned):
    spec: slice | tuple

    def __new__(cls, value):
        return (Clamped if isinstance(cls.spec, slice | None) else Optioned).__new__(cls, value)

    def __class_getitem__(cls, spec):
        return (Clamped if isinstance(cls.spec, slice) else Optioned).__class_getitem__(spec)

    def __repr__(self):
        return (Clamped if isinstance(self.spec, slice) else Optioned).__repr__(self)


class ClampedInt(Clamped, int):
    ...


class ClampedFloat(Clamped, float):
    ...


class OptionedInt(Optioned, float):
    ...


class OptionedFloat(Optioned, float):
    ...


class OptionedStr(Optioned, str):
    ...
