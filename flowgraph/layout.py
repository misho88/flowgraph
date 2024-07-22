__all__ = 'Box', 'HBox', 'VBox'

from .backend import QWidget, QHBoxLayout, QVBoxLayout, QLayout


class Box(QWidget):
    def __init__(self, layout: QLayout):
        super().__init__()
        self.show()
        self.setLayout(layout)

    def layout(self):
        layout = super().layout()
        assert layout is not None
        return layout

    def add(self, widget: QWidget):
        return self.layout().addWidget(widget)

    def remove(self, widget: QWidget):
        return self.layout().removeWidget(widget)


class HBox(Box):
    def __init__(self):
        super().__init__(QHBoxLayout())


class VBox(Box):
    def __init__(self):
        super().__init__(QVBoxLayout())
