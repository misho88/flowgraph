#!/usr/bin/env python3

from pathlib import Path
from argparse import ArgumentParser
from argcomplete import autocomplete
from sys import stderr
from debug import debug

app_name = 'Flow Graph Demo'
parser = ArgumentParser(
    prog=app_name,
    description='Flow Graph Demo',
)
parser.add_argument(
    'state', type=Path, nargs='?', default=Path('nodes.json'),
    help='state file which defines the graphical nodes (default: nodes.json)'
)
autocomplete(parser)
args = parser.parse_args()

from tempfile import NamedTemporaryFile
from shutil import copy
from pysh import Thread, proc  # noqa: E402
from glob import glob  # noqa: E402
from termcolor import colored  # noqa: E402
from json import load, dump
from .window import Window
from .backend import QApplication

app = QApplication([])

win = Window(app_name)
if args.state.exists():
    with args.state.open('r') as file:
        state = load(file)
    win.setState(state)
app.exec()

with NamedTemporaryFile('w') as file:
    dump(win.state(), file, indent='\t')
    print(file=file)
    file.flush()
    copy(file.name, args.state)
