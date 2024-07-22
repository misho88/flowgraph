__all__ = 'Box', 'HBox', 'VBox'

from .backend import QWidget, QHBoxLayout, QVBoxLayout, QLayout


class Box(QWidget):
    def __init__(self, layout: QLayout):
        super().__init__()
        self.show()
        self.layout = layout
        self.setLayout(layout)

    def add(self, widget: QWidget):
        return self.layout.addWidget(widget)

    def remove(self, widget: QWidget):
        return self.layout.removeWidget(widget)


class HBox(Box):
    def __init__(self):
        super().__init__(QHBoxLayout())


class VBox(Box):
    def __init__(self):
        super().__init__(QVBoxLayout())
