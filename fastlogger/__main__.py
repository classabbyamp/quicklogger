"""
logparser test interface
---

Copyright (C) 2020 classabbyamp
This software is released under the BSD 3-Clause license.
"""

import sys

from PyQt5.QtWidgets import QApplication

import gui


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = gui.MainWindowUi()
    view.show()

    gui.MainWindowCtrl(view)

    sys.exit(app.exec())
