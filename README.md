# Flowgraph

Graphical node editor.

# Status

Barely functional; it should not be used.

# Requirements

`PyQt5` (for now), ...

# Similar Projects

[QNodeEditor](https://github.com/JasperJeuken/QNodeEditor) directly inspired
this project. The fundamental difference is that QNodeEditor is output driven:
on demand, the subgraph needed to compute an output is evaluated. Flowgraph is
input driven: whenever an input is changed, the subgraph it affects is
evaluated. Furthermore, QNodeEditor is asynchronous and Flowgraph is
synchronous.
