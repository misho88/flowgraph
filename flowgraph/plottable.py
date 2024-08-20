__all__ = 'Plottable',


class Plottable:
    kind: str = 'plot'

    def __class_getitem__(cls, kind):
        k = kind
        P = Plottable

        class Sub(Plottable):
            kind: str = k

        return Sub
