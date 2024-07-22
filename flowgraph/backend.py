from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QVBoxLayout, QHBoxLayout, QBoxLayout, QLayout, QGridLayout,
    QWidget,
    QLabel, QLineEdit, QFileDialog, QPushButton,
    QGraphicsView, QGraphicsItem, QGraphicsTextItem, QGraphicsSceneMouseEvent, QGraphicsProxyWidget, QGraphicsSceneContextMenuEvent,
    QMenu, QAction, QFrame,
    QGraphicsScene, QGroupBox, QSlider, QDoubleSpinBox, QSpinBox, QTextEdit, QPlainTextEdit, QErrorMessage, QMessageBox, QSizeGrip
)
from PyQt5.QtGui import QKeySequence, QColor, QPainter, QPainterPath, QPen, QBrush, QMouseEvent, QWheelEvent, QKeyEvent, QCursor, QContextMenuEvent, QTransform, QFont, QFontMetrics, QClipboard
from PyQt5.QtCore import pyqtSignal, Qt, QRect, QRectF, QPoint, QPointF, QObject
from functools import cache
from funcpipes import Pipe
from debug import debug


@cache
def get_brush(color: str):
    return QBrush(QColor(color))


@cache
def get_pen(color: str, width=None):
    pen = QPen(QColor(color))
    if width is not None:
        pen.setWidth(width)
    return pen


def populate_menu(menu, items, wrap=None):
    for text, shortcut, callback in items:
        action = menu.addAction(text)
        assert action is not None
        action.triggered.connect(wrap(callback) if wrap else callback)
        if shortcut is None:
            continue
        if not isinstance(shortcut, QKeySequence):
            shortcut = QKeySequence(shortcut)
        action.setShortcut(shortcut)


def traceback_message(e, info=None):
    from io import StringIO
    from traceback import print_exception

    with StringIO() as sio:
        print_exception(e, file=sio)
        text = sio.getvalue()

    msg = QMessageBox(QMessageBox.Critical, text, text, flags=Qt.WindowType.Dialog)
    if info is not None:
        msg.setInformativeText(info)
    msg.setWindowTitle(str(e))
    msg.setFont(QFont('mono'))
    #msg.setSizeGripEnabled(True)
    #msg.setSizeIncrement(1, 1)
    msg.exec_()


@Pipe
def with_error_message(func, parent=None):
    from functools import wraps
    from debug import debug

    @wraps(func)
    def call(*args, **kwargs):
        debug(args, kwargs)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback_message(e)

    return call
