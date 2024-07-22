__all__ = 'Window',

from .backend import QWidget, QMainWindow, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QPoint, populate_menu, QKeySequence, QFileDialog, with_error_message
from .layout import HBox, VBox
from . import editor, function
from .util import ignore_args
from debug import debug
from pathlib import Path
from .stateful import Stateful
from tempfile import NamedTemporaryFile
from shutil import copy
from json import dump, load
from functools import partial


class Window(QMainWindow, Stateful):
    def __init__(self, title=None, functions=(), state_file=None):
        super().__init__()
        self._state = {}
        self.show()

        self._state_file = state_file
        self._title = title
        self.updateTitle()

        self._editor = editor.View()
        scene = self._editor.scene()
        assert scene is not None

        for function in functions:
            self.addFunction(function)

        vbox = VBox()
        vbox.add(self._editor)
        vbox.add(QLineEdit())
        self.setCentralWidget(vbox)

        file, edit = self.populate_menu_bar('&File', '&Edit')
        populate_menu(file, [
            ('&Open'   , QKeySequence.Open, self.loadState    ),
            ('&Save'   , QKeySequence.Save, self.saveState    ),
            ('Save &As', 'Ctrl+Shift+S'   , partial(self.saveState, force_dialog=True)),
            ('&Quit'   , QKeySequence.Quit, self.quit         ),
        ], wrap=ignore_args & with_error_message)
        populate_menu(edit, [
            ('&Copy'  , QKeySequence.Copy  , scene.selectedToClipboard),
            ('&Paste' , QKeySequence.Paste , scene.addFromClipboard   ),
            ('&Delete', QKeySequence.Delete, scene.removeSelected     ),
            ('&Clear' , None               , scene.removeAll          ),
        ], wrap=ignore_args & with_error_message)

        if state_file is not None:
            self.loadState(force_dialog=False)

    def updateTitle(self):
        return self.setWindowTitle(self._title if self._state_file is None else f'{self._title} ({self._state_file})')

    def addFunction(self, function):
        self.editor().addFunction(function)

    def editor(self):
        return self._editor

    def populate_menu_bar(self, *items):
        bar = self.menuBar()
        assert bar is not None
        for item in items:
            menu = bar.addMenu(item)
            assert menu is not None
            yield menu

    def quit(self, *_):
        self.close()

    def iterState(self):
        yield from super().iterState()
        yield 'title', self._title
        yield 'editor', self.editor().state()

    def setState(self, state):
        state = super().setState(state, missing='return')
        for key, value in state.items():
            if key.startswith('__'):
                pass
            elif key == 'title':
                self._title = value
                self.updateTitle()
            elif key == 'editor':
                self.editor().setState(value)
            else:
                raise KeyError(key)

    def loadState(self, force_dialog=True):
        if self._state_file is None or force_dialog:
            path, filter = QFileDialog.getOpenFileName(self, 'Save File', '', 'JSON Files (*.json)')
            if not path:
                return
        else:
            path = self._state_file

        with open(path) as file:
            self.setState(load(file))

        self._state_file = path
        self.updateTitle()

    def saveState(self, force_dialog=False):
        if self._state_file is None or force_dialog:
            path, filter = QFileDialog.getSaveFileName(self, 'Save File', '', 'JSON Files (*.json)')
            if not path:
                return
        else:
            path = self._state_file

        with NamedTemporaryFile('w') as file:
            dump(self.state(), file, indent='\t')
            print(file=file)
            file.flush()
            copy(file.name, path)

        self._state_file = path
        self.updateTitle()
