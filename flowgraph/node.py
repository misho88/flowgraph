__all__ = 'Item',


from debug import debug
from .backend import Qt, QPainter, QWidget, QRectF, get_pen, get_brush, QMenu, QAction, QGraphicsItem, QPainterPath, QGraphicsProxyWidget, QGroupBox, QVBoxLayout, QPointF, QLineEdit, QContextMenuEvent, QApplication, QKeySequence, populate_menu
from typing import Any
from . import entry
from .entry import Entry
from .util import partial, ignore_args, get_static_object_from_state
from .stateful import Stateful


class Widget(QGroupBox, Stateful):
    def __init__(self, name=None, parent=None):
        super().__init__(parent=parent)
        if name is not None:
            self.setName(name)
        #self.setFlat(False)
        self.setLayout(QVBoxLayout())
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._item = None
        self._state = {}

    def name(self):
        return self.title()

    def setName(self, name):
        return self.setTitle(name)

    def addEntry(self, widget):
        widget.setParent(self)
        return self.layout().addWidget(widget)

    def entries(self):
        return [ c for c in self.children() if isinstance(c, Entry) ]

    def inputs(self):
        for entry in self.entries():
            if entry.input().isVisible():
                yield entry

    def outputs(self):
        for entry in self.entries():
            if entry.output().isVisible():
                yield entry

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        #w = QApplication.instance().widgetAt(event.globalX(), event.globalY())
        Menu(self).exec(event.globalPos())

    def item(self):
        return self._item

    def setItem(self, item):
        self._item = item
        for entry in self.entries():
            entry.setParentItem(item)
        return self

    def iterState(self):
        yield from super().iterState()
        yield 'name', self.name()
        yield 'entries', [ entry.state() for entry in self.entries() ]

    def setState(self, state, missing='error'):
        state = Stateful.setState(self, state, missing='return')
        returned = {} if missing == 'return' else None
        for key, value in state.items():
            if key == 'name':
                self.setName(value)
            elif key == 'entries':
                for entry_state in value:
                    cls = get_static_object_from_state(entry_state)
                    self.addEntry(cls.fromState(entry_state, parent=self))
            elif missing == 'error':
                raise KeyError(key)
            elif missing == 'return':
                returned[key] = value  # type: ignore
        return returned

    def editor(self):
        item = self.item()
        if item is None:
            return None
        return item.editor()


class Item(QGraphicsItem, Stateful):
    def __init__(self, widget: Widget | None = None):
        super().__init__()
        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIgnoresParentOpacity |
            QGraphicsItem.ItemSendsScenePositionChanges | 
            QGraphicsItem.ItemIsMovable
        )
        self.setAcceptHoverEvents(True)
        self._state: dict[str, Any] = dict(
            background=dict(color='#7f111111'),
            border=dict(color='white', padding=4, width=1, radius=4),
        )
        self.Proxy: Proxy | None
        self.setZValue(1)
        if widget is not None:
            self.setWidget(widget)

    def widget(self):
        return self.proxy.widget()

    def setWidget(self, widget):
        self.proxy = Proxy(self, widget)
        widget.setItem(self)

    def boundingRect(self) -> QRectF:
        w = self._state['border']['padding']
        return QRectF(-w, -w, self.width() + 2 * w, self.height() + 2 * w).normalized()

    def width(self):
        return self.proxy.widget().width()

    def height(self):
        return self.proxy.widget().height()

    def paint(self, painter: QPainter, option, widget):
        mult = 3 if self.isSelected() else 1

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        r = self._state['border']['radius']
        rect = self.boundingRect()
        path.addRoundedRect(rect, r, r)
        painter.setPen(get_pen(self._state['border']['color'], mult * self._state['border']['width']))
        painter.setBrush(get_brush(self._state['background']['color']))
        painter.drawPath(path)

    #def itemChange(self, change, value):
    #    if change == self.GraphicsItemChange.ItemSelectedHasChanged:
    #        self._state['border']['width'] = 3 if self.isSelected() else 1
    #    return super().itemChange(change, value)

    def iterState(self):
        yield from Stateful.iterState(self)
        yield 'widget', self.widget().state()
        yield 'position', dict(x=self.x(), y=self.y())

    def setState(self, state):
        state = Stateful.setState(self, state, missing='return')
        for key, value in state.items():
            if key == 'widget':
                cls = get_static_object_from_state(value)
                self.setWidget(cls.fromState(value))
            elif key == 'position':
                x, y = value['x'], value['y']
                self.setPos(QPointF(x, y))
            else:
                raise KeyError(key)
        return self

    def editor(self):
        return self.scene().editor()

    def remove(self):
        self.scene().removeItem(self)


class Menu(QMenu):
    def __init__(self, widget: Widget):
        super().__init__()
        populate_menu(self, [
            ('&Delete', 'Delete'         , widget.item().remove),
            ('&Copy'  , QKeySequence.Copy, widget.item().toClipboard),
        ])
        #add_input = self.addMenu('&Add Input To')
        #for entry in widget.entries():
        #    add_input.addAction(entry.name() or 'anonymous').triggered.connect(ignore_args(entry.enableInput))
        #add_output = self.addMenu('&Add Output To')
        #for entry in widget.entries():
        #    add_output.addAction(entry.name() or 'anonymous').triggered.connect(ignore_args(entry.enableOutput))


class Proxy(QGraphicsProxyWidget):
    def __init__(self, parent, widget):
        super().__init__(parent=parent)
        self.setWidget(widget)
