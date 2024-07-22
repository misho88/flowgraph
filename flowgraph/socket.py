__all__ = 'Item', 'Input', 'Output'


from debug import debug
from .backend import QPainter, QRectF, get_pen, get_brush, QMenu, QGraphicsItem, QPointF, with_error_message
from . import edge
from .util import partial
from .stateful import Stateful


class Item(QGraphicsItem, Stateful):
    def __init__(self, entry=None):
        super().__init__()
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity |
            QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges  # type: ignore
        )
        self._state = dict(
            width=20,
            radius=4,
        )
        self.setEntry(entry)
        self.setEnabled(False)
        self.setZValue(2)

    def entry(self):
        return self._entry

    def setEntry(self, entry):
        self._entry = entry

    def boundingRect(self) -> QRectF:
        w = self._state['width']
        return QRectF(-w, -w, 2 * w, 2 * w)

    def paint(self, painter: QPainter, option, widget):
        parent = self.parentItem()
        assert parent is not None

        painter.setPen(get_pen(parent._state['border']['color']))  # type: ignore
        painter.setBrush(get_brush(parent._state['border']['color']))  # type: ignore
        r = self._state['radius']
        painter.drawEllipse(QPointF(0, 0), r, r)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self._state['radius'] = 6 if self.isSelected() else 4
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        Menu(self).exec(event.globalPos())  # type: ignore

    def enabled(self):
        return self.isVisible()

    def setEnabled(self, value=True):
        return self.setVisible(value)

    def iterState(self):
        yield from super().iterState()
        yield 'enabled', self.enabled()

    def setState(self, state, missing='error'):
        state = super().setState(state, missing='return')
        assert isinstance(state, dict)

        rv = {} if missing == 'return' else None
        for key, value in state.items():
            if key == 'enabled':
                self.setEnabled(value)
            elif missing == 'return':
                rv[key] = value  # type: ignore
            elif missing == 'error':
                raise KeyError(key)
        return rv


class Input(Item):
    def __init__(self, entry):
        super().__init__(entry)
        self._edge = None

    def setParentItem(self, parent):
        super().setParentItem(parent)
        assert parent is not None

        frame = self.entry().frameGeometry()
        rect = parent.boundingRect()
        pos = parent.mapToItem(self, frame.topLeft())
        self.setPos(rect.left(), pos.y() + frame.height() / 2)

    def edge(self):
        return self._edge

    def setEdge(self, edge):
        self._edge = edge

    def setSource(self, source):
        self.setEdge(edge.Item(source, self))

    def unsetSource(self):
        if self._edge is None:
            return
        self._edge.setParentItem(None)
        self._edge = None


class Output(Item):
    def __init__(self, entry):
        super().__init__(entry)

    def setParentItem(self, parent):
        super().setParentItem(parent)
        assert parent is not None

        frame = self.entry().frameGeometry()
        rect = parent.boundingRect()
        pos = parent.mapToItem(self, frame.topLeft())
        self.setPos(rect.right(), pos.y() + frame.height() / 2)


def connect(item):
    scene = item.scene()
    sockets = [ item for item in scene.selectedItems() if isinstance(item, Item) ]
    if not sockets:
        debug('no selected sockets')
        return
    if not isinstance(item, Output):
        source = sockets[-1].entry()
        item.entry().setSource(source)
        return
    for sink in sockets:
        sink.entry().setSource(item.entry())


class Menu(QMenu):
    def __init__(self, item: Item):
        super().__init__()
        self.addAction('&Connect', with_error_message(partial(connect, item)))
