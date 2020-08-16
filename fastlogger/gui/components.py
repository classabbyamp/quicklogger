"""
components.py - part of fastlogger
---

Copyright (C) 2020 classabbyamp
Released under the terms of the BSD 3-Clause license.
"""


from typing import List, Optional
from datetime import time
from pathlib import Path

from PyQt5.QtCore import QSize, Qt, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QTextFormat
from PyQt5.QtWidgets import (QPlainTextEdit, QTextEdit, QTableWidget, QWidget, QTableWidgetItem,
                             QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QStatusBar,
                             QLabel, QFrame)

import logparser


__all__ = ["LogEditor", "LogViewer"]


log_template = """# Headers
# only mycall is mandatory
mycall
mygrid
operator
qslmsg
mywwff
mysota
mypota
nickname

# Log
date
"""


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class LogEditor(QPlainTextEdit):
    filename = ""
    saved = False

    def __init__(self, viewer: QTableWidget, statusbar: QStatusBar, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.viewer = viewer
        self.statusbar = statusbar

        self.setFont(QFont("Courier"))

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.updateViewer)
        self.textChanged.connect(self.setSavedStatus)

        self.updateLineNumberAreaWidth(0)

    def onNewFile(self):
        if not self.saved:
            dlg = SaveDialog(self, self)
            if d := dlg.exec() == QDialog.reject:
                return
            elif d == QDialog.accept:
                self.onSaveFile()
        self.clear()
        self.setPlainText(log_template)
        self.filename = ""
        self.saved = False

    def onOpenFile(self):
        # if unsaved, ask to save
        fn = QFileDialog.getOpenFileName(self, "Open Log file", str(Path.home()), "Text files (*.txt)")
        if fn[0]:
            with open(fn[0]) as log_file:
                self.set_content(log_file.read())
                self.filename = fn[0]
                self.saved = False

    def onSaveFile(self):
        if not self.filename:
            fn = QFileDialog.getSaveFileName(self, "Save Log file", str(Path.home()), "Text files (*.txt)")
            if fn[0]:
                self.filename = fn[0]
            else:
                return
        with open(self.filename, "w") as log_file:
            log_file.write(self.toPlainText())
            self.saved = True

    def onSaveAsFile(self):
        fn = QFileDialog.getSaveFileName(self, "Save Log file As", str(Path.home()), "Text files (*.txt)")
        if fn[0]:
            self.filename = fn[0]
        else:
            return
        with open(self.filename, "w") as log_file:
            log_file.write(self.toPlainText())
            self.saved = True

    def set_content(self, new_log):
        self.clear()
        self.setPlainText(new_log)

    def setSavedStatus(self):
        self.saved = False

    def updateViewer(self):
        log_data = logparser.LogFile(self.toPlainText().split("\n"))
        self.viewer.set_data(log_data)
        if log_data.my_call:
            ops = None
            if log_data.operators:
                ops = "Operators: " if len(log_data.operators) > 1 else "Operator: "
                ops += ", ".join(log_data.operators)
            self.statusbar.update_widget("mycall", log_data.my_call, ops)
        else:
            self.statusbar.update_widget("mycall")
        if log_data.qth_nickname:
            self.statusbar.update_widget("qth_nick", log_data.qth_nickname)
        else:
            self.statusbar.update_widget("qth_nick")
        if log_data.my_pota or log_data.my_sota or log_data.my_wwff:
            myota = ""
            if log_data.my_pota:
                myota += log_data.my_pota
                if log_data.my_sota or log_data.my_wwff:
                    myota += " | "
            if log_data.my_sota:
                myota += log_data.my_sota
                if log_data.my_wwff:
                    myota += " | "
            if log_data.my_wwff:
                myota += log_data.my_wwff
            self.statusbar.update_widget("myota", myota)
        else:
            self.statusbar.update_widget("myota")
        if len(log_data) == 1:
            self.statusbar.update_widget("num_qsos", "1 QSO")
        else:
            self.statusbar.update_widget("num_qsos", f"{len(log_data)} QSOs")

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                        self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                n = blockNumber + 1
                # not a x5 or x0
                if (n % 5) and (n % 10):
                    number = "·"
                # x5
                elif not (n % 5) and (n % 10):
                    number = "-"
                # x0
                else:
                    number = str(n)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height,
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor(Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)


class LogViewer(QTableWidget):
    col_headings = ["Date", "Time", "Band", "Frequency", "Mode", "Callsign", "Tx RST", "Rx RST", "Name",
                    "Grid", "Tx Exch", "Rx Exch", "WWFF", "SOTA", "POTA", "QSL Message", "Notes", ]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.create_columns()

    def create_columns(self):
        self.setColumnCount(len(self.col_headings))
        self.setHorizontalHeaderLabels(self.col_headings)
        self.resizeColumnsToContents()

    def data(self) -> List[List[str]]:
        data = [
            [None for _ in range(self.log_viewer.columnCount())]
            for _ in range(self.log_viewer.rowCount())
        ]
        for i in range(self.log_viewer.rowCount()):
            for j in range(self.log_viewer.columnCount()):
                data[i][j] = self.log_viewer.itemAt(i, j).text()
        return data

    def set_data(self, new_data):
        # clear data
        self.clearContents()
        self.setRowCount(0)
        # set new data
        for i, row in enumerate(new_data):
            self.insertRow(i)
            self.setVerticalHeaderItem(i, QTableWidgetItem(str(i+1)))
            for j, itm in enumerate(row.values()):
                if isinstance(itm, float):
                    itm = f"{itm:.3f}"
                elif isinstance(itm, time):
                    itm = time.strftime(itm, "%H:%M")
                else:
                    itm = str(itm)
                self.setItem(i, j, QTableWidgetItem(itm))
        self.resizeColumnsToContents()


class StatusBar(QStatusBar):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.widgets = {
            "log_style": QLabel("Regular Logging"),
            "log_mode": QLabel("Off-Line"),
            "mycall": QLabel(""),
            "myota": QLabel(""),
            "qth_nick": QLabel(""),
            "num_qsos": QLabel("0 QSOs"),
        }

        self._add_widgets()

    def _add_widgets(self):
        for widget in self.widgets.values():
            widget.setFrameShape(QFrame.Panel)
            widget.setFrameShadow(QFrame.Sunken)
            self.addWidget(widget)
            if not widget.text():
                widget.hide()

    def update_widget(self, name: str, value: Optional[str] = None, tooltip: Optional[str] = None):
        if value == "" or value is None:
            self.widgets[name].clear()
            self.widgets[name].hide()
        else:
            self.widgets[name].setText(value)
            self.widgets[name].show()
        if tooltip:
            self.widgets[name].setToolTip(tooltip)
        else:
            self.widgets[name].setToolTip("")


class SaveDialog(QDialog):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.setWindowTitle("Save the current log?")
        buttons = QDialogButtonBox.Discard | QDialogButtonBox.Cancel | QDialogButtonBox.Save
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.destroyed.connect(self.destroy)
        layout = QVBoxLayout()
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
