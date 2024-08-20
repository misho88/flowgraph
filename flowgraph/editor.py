__all__ = 'View',

from debug import debug
from . import node, function, socket, edge, entry
from .backend import Qt, QGraphicsView, QGraphicsScene, QPainter, QRectF, QWheelEvent, QFrame, QContextMenuEvent, QMenu, QApplication, QWidget, QTransform, populate_menu, QKeySequence, with_error_message, get_brush
from .util import partial, ignore_args, get_static_object_from_state
from .stateful import Stateful
from json import loads, dumps


class Scene(QGraphicsScene, Stateful):
    def __init__(self):
        super().__init__()
        self._state = {}
        self._dirty = False  # FIXME: something to keep track of whether the thing has been saved or not
        self._nodes = []

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)
        painter.fillRect(rect, get_brush('#3f7f7f7f'))

    def nodes(self):
        return self._nodes.copy()

    def findEntry(self, entry_or_socket):
        if isinstance(entry_or_socket, socket.Item):
            entry = entry_or_socket.entry()
        else:
            entry = entry_or_socket

        nodes = self.nodes()
        for n, node in enumerate(nodes):
            entries = node.widget().entries()
            for e, entry_ in enumerate(entries):
                if entry_ is entry:
                    return n, e
        raise ValueError(entry)

    def edges(self, with_indices=False):
        nodes = self.nodes()
        for n, node in enumerate(nodes):
            entries = node.widget().entries()
            for e, entry in enumerate(entries):
                edge = entry.input().edge()
                if edge is None:
                    continue
                if not with_indices:
                    yield edge
                    continue
                sink_idx = n, e
                source = edge.source()
                source_idx = self.findEntry(source)
                yield source_idx, sink_idx, edge

    def addEdge(self, source, sink):
        if isinstance(source, list | tuple):
            n, e = source
            source = self.nodes()[n].widget().entries()[e]
        if isinstance(sink, list | tuple):
            n, e = sink
            sink = self.nodes()[n].widget().entries()[e]
        #if isinstance(source, entry.Entry):
        #    source = source.output()
        #if isinstance(sink, entry.Entry):
        #    sink = sink.input()
        sink.setSource(source)

    def iterState(self):
        yield from Stateful.iterState(self)
        yield 'nodes', [ node.state() for node in self.nodes() ]
        yield 'edges', [
            dict(source=source, sink=sink)
            for source, sink, edge in self.edges(with_indices=True)
        ]

    def addState(self, state):
        for key, value in (state.items() if isinstance(state, dict) else state):
            if key in self._state:
                self._state[key] = value
            elif key == 'nodes':
                for node_state in value:
                    Node = get_static_object_from_state(node_state)
                    node = Node.fromState(node_state)
                    self.addNode(node)
            elif key == 'edges':
                for edge in value:
                    self.addEdge(edge['source'], edge['sink'])
            else:
                raise KeyError(f'{repr(key)}: {repr(value)}')

    def setState(self, state):
        state = super().setState(state, missing='return')
        self.removeAll()
        self.addState(state)

    def addNode(self, widget_or_item, pos=None):
        item = node.Item(widget_or_item) if isinstance(widget_or_item, QWidget) else widget_or_item
        if pos is not None:
            item.setPos(pos)
        self.addItem(item)
        self._nodes.append(item)
        return item

    def removeNode(self, node):
        if isinstance(node, int):
            return self.removeItem(self.nodes().pop(node))
        self._nodes.remove(node)
        self.removeItem(node)

    def removeEdge(self, edge):
        # FIXME: by index?
        edge.remove()
        self.removeItem(edge)

    def editor(self):
        return self.views()[0]

    def selectedNodes(self):
        return [ i for i in self.selectedItems() if isinstance(i, node.Item) ]

    def selectedEdges(self):
        return [ i for i in self.selectedItems() if isinstance(i, edge.Item) ]

    def removeSelected(self):
        for item in self.selectedItems():
            if isinstance(item, node.Item):
                self.removeNode(item)
            elif isinstance(item, edge.Item):
                self.removeEdge(item)

    def removeAll(self):
        for node in self.nodes():
            self.removeNode(node)

    def selectedToClipboard(self):
        clipboard = QApplication.instance().clipboard()  # type: ignore
        nodes = [ n.state() for n in self.selectedNodes() ]
        edges = [ e.state() for e in self.selectedEdges() ]
        clipboard.setText(dumps(dict(nodes=nodes, edges=edges)))

    def addFromClipboard(self):
        clipboard = QApplication.instance().clipboard()  # type: ignore
        state = loads(clipboard.text())
        if set(state.keys()) == { 'nodes', 'edges' }:
            return self.addState(state)

        obj = get_static_object_from_state(state)
        if isinstance(obj, node.Item):
            self.addState(dict(nodes=[state], edges=[]))
        elif isinstance(obj, edge.Item):
            self.addState(dict(nodes=[], edges=[state]))
        else:
            raise ValueError(state)


class View(QGraphicsView, Stateful):
    def __init__(self):
        super().__init__()
        self.setScene(Scene())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._state = dict(
            zoom=dict(increment=1.2),
        )
        #self._mouse_press = None

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        # Set viewport properties
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.functions = []

        self._entry_types: dict[str, entry.Entry] = {
            name: attr
            for name, attr in vars(entry).items()
            if isinstance(attr, type) and issubclass(attr, entry.Entry) and attr is not entry.Entry
        }

    def registerEntryType(self, Entry):
        if not isinstance(Entry, entry.Entry):
            raise ValueError(f'{Entry=} must be a subclass of entry.Entry')
        self._entry_types[Entry.__name__] = Entry

    def scene(self) -> Scene:
        scene = super().scene()
        assert isinstance(scene, Scene)
        return scene

    def transformAsList(self):
        t = self.transform()
        return [
            t.m11(), t.m12(), t.m13(),
            t.m21(), t.m22(), t.m23(),
            t.m31(), t.m32(), t.m33(),
        ]

    def wheelEvent(self, event: QWheelEvent):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            incr = self._state['zoom']['increment']  # type: ignore
            if event.angleDelta().y() < 0:
                incr = 1 / incr
            self.scale(incr, incr)
        else:
            super().wheelEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        item = self.itemAt(event.x(), event.y())
        if item is None:
            Menu(self, event).exec(event.globalPos())
            return
        if hasattr(item, 'widget'):
            item = item.widget()  # type: ignore
        item.contextMenuEvent(event)  # type: ignore

    def addNode(self, widget_or_item, pos=None):
        return self.scene().addNode(widget_or_item, self.mapToScene(pos) if pos is not None else None)

    def addFunction(self, function):
        self.functions.append(function)

    def iterState(self):
        yield from Stateful.iterState(self)
        yield 'transform', self.transformAsList()
        yield 'scene', self.scene().state()

    def setState(self, state):
        state = super().setState(state, missing='return')
        for key, value in state.items():
            if key.startswith('__'):
                pass
            elif key == 'transform':
                self.setTransform(QTransform(*value))
            elif key == 'scene':
                self.scene().setState(value)
            else:
                raise KeyError(key)
        return self


@with_error_message
def add_function(view, f, pos):
    return view.addNode(function.Widget(f), pos)


class Menu(QMenu):
    def __init__(self, view: View, event: QContextMenuEvent | None = None):
        super().__init__()
        pos = event.pos() if event is not None else None
        add = self.addMenu('&Add Function')
        assert add is not None
        for f in view.functions:
            action = add.addAction(f'&{f.__name__}')
            assert action is not None
            action.triggered.connect(ignore_args(partial(add_function, view, f, pos)))
        populate_menu(self, [
            ('&Delete', 'Delete'         , view.scene().removeSelected     ),
            ('&Copy'  , QKeySequence.Copy, view.scene().selectedToClipboard),
        ])
