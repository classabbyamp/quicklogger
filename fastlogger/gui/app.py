"""
app.py - part of fastlogger
---

Copyright (C) 2020 classabbyamp
Released under the terms of the BSD 3-Clause license.
"""


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QSplitter, QMenuBar, QToolBar,
                             QMenu, QWidget, QAction, )

from .components import LogEditor, LogViewer, StatusBar


__all__ = ["MainWindowUi", "MainWindowCtrl"]


class MainWindowUi(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FastLogger")
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)
        self.layout = QGridLayout()
        self._central_widget.setLayout(self.layout)

        self._create_actions()

        self._create_menubar()
        self._create_toolbar()
        self._create_statusbar()

        self._create_log_area()

        self._bind_actions()

    def _create_actions(self):
        self.action_new = QAction(QIcon("assets/icons/document-new.png"), "&New Log")
        self.action_new.setShortcut("Ctrl+N")
        self.action_open = QAction(QIcon("assets/icons/document-open.png"), "&Open Log")
        self.action_open.setShortcut("Ctrl+O")
        self.action_save = QAction(QIcon("assets/icons/document-save.png"), "&Save Log")
        self.action_save.setShortcut("Ctrl+S")
        self.action_save_as = QAction(QIcon("assets/icons/document-save-as.png"), "Save Log &as")
        self.action_save_as.setShortcut("Ctrl+Shift+S")

    def _bind_actions(self):
        self.action_new.triggered.connect(self.log_editor.onNewFile)
        self.action_open.triggered.connect(self.log_editor.onOpenFile)
        self.action_save.triggered.connect(self.log_editor.onSaveFile)
        self.action_save_as.triggered.connect(self.log_editor.onSaveAsFile)

    def _create_log_area(self):
        self.log_area = QSplitter(self)
        self.log_area.setChildrenCollapsible(False)
        self.log_viewer = LogViewer()
        self.log_editor = LogEditor(self.log_viewer, self.statusbar)
        self.log_area.addWidget(self.log_editor)
        self.log_area.addWidget(self.log_viewer)

        self.layout.addWidget(self.log_area, 0, 0, 1, 1)

    def _create_menubar(self):
        self.menubar = QMenuBar(self)
        self.menu_file = QMenu("&File", self.menubar)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_edit = QMenu("&Edit", self.menubar)
        self.setMenuBar(self.menubar)

    def _create_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toolbar.addAction(self.action_new)
        self.toolbar.addAction(self.action_open)
        self.toolbar.addAction(self.action_save)
        self.toolbar.addAction(self.action_save_as)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

    def _create_statusbar(self):
        self.statusbar = StatusBar(self)
        self.setStatusBar(self.statusbar)


class MainWindowCtrl:
    def __init__(self, view):
        self._view = view
        self._connect_signals()

    def _connect_signals(self):
        pass  # self._view.log_editor.textChanged.connect()
