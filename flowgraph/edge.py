__all__ = 'Item',


from debug import debug
from .backend import QPainter, QRectF, get_pen, QContextMenuEvent, QMenu, QGraphicsItem, QPainterPath, QPointF, populate_menu
from .stateful import Stateful


class Item(QGraphicsItem, Stateful):
    def __init__(self, source=None, sink=None):
        super().__init__()
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity |
            QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges  # type: ignore
        )
        self.setSource(source)
        self.setSink(sink)
        self._state = dict(
            protrusion=50,
            color='gray',
            width=1,
            style='cubic',
        )
        self.setParentItem(sink)
        self.setZValue(-1)

    def source(self):
        return self._source

    def setSource(self, source):
        self._source = source

    def sink(self):
        return self._sink

    def setSink(self, sink):
        self._sink = sink

    def boundingRect(self) -> QRectF:
        return QRectF(QPointF(0, 0), self.source().mapToItem(self, QPointF(0, 0))).normalized()

    def paint(self, painter: QPainter, option, widget):
        path = QPainterPath()
        d: int = self._state['protrusion']  # type: ignore

        p0 = self.source().mapToItem(self, QPointF(0, 0))
        p3 = QPointF(0, 0)
        p1 = QPointF(p0.x() + d, p0.y())
        p2 = QPointF(p3.x() - d, p3.y())

        path.moveTo(p0)
        style = self._state['style']

        if style == 'line':
            path.lineTo(p1)
            path.lineTo(p2)
            path.lineTo(p3)
        elif style == 'cubic':
            path.cubicTo(p1, p2, p3)
        else:
            raise ValueError(f"{self._state['style']=}")

        painter.setPen(get_pen(self._state['color'], self._state['width']))
        painter.drawPath(path)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self._state['width'] = 3 if self.isSelected() else 1
        return super().itemChange(change, value)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        Menu(self).exec(event.globalPos())

    def iterState(self):
        yield from super().iterState()
        if self.source() is not None:
            yield 'source', self.source()

    def remove(self):
        self.sink().entry().unsetSource()


class Menu(QMenu):
    def __init__(self, item: Item):
        super().__init__()
        populate_menu(self, [
            ('&Delete', 'Delete', item.remove),
        ])
