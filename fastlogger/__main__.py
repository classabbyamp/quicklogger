"""
logparser test interface
---

Copyright (C) 2020 classabbyamp
This software is released under the BSD 3-Clause license.
"""

from datetime import time

import wx

import logparser


col_headings = [
    "",      # index
    "Date",
    "Time",
    "Band",
    "Frequency",
    "Mode",
    "Callsign",
    "Tx RST",
    "Rx RST",
    "Name",
    "Grid",
    "Tx Exch",
    "Rx Exch",
    "WWFF",
    "SOTA",
    "POTA",
    "QSL Message",
    "Notes",
]


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.GridSizer(2)
        self.row_objs = list()

        # === editor setup ===
        self.editor = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_NOHIDESEL | wx.HSCROLL)

        self.editor.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas'))
        # === end editor setup ===

        # === list_ctrl setup ===
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)

        for idx, itm in enumerate(col_headings):
            self.list_ctrl.InsertColumn(idx, itm, width=140)

        for idx in range(self.list_ctrl.GetColumnCount()):
            self.list_ctrl.SetColumnWidth(idx, wx.LIST_AUTOSIZE_USEHEADER)
        # === end list_ctrl setup ===

        main_sizer.Add(self.editor, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def open_log(self, path):
        self.list_ctrl.DeleteAllItems()

        self.editor.LoadFile(path)

        with open(path) as file:
            log = logparser.LogFile(file.readlines())

        for i, r in enumerate(log):
            self.list_ctrl.InsertItem(i, str(i+1))
            for j, itm in enumerate(r.values()):
                if isinstance(itm, float):
                    itm = f"{itm:.3f}"
                elif isinstance(itm, time):
                    itm = time.strftime(itm, "%H:%M")
                else:
                    itm = str(itm)

                self.list_ctrl.SetItem(i, j+1, itm)
            self.row_objs.append(r)

        for idx in range(self.list_ctrl.GetColumnCount()):
            self.list_ctrl.SetColumnWidth(idx, wx.LIST_AUTOSIZE_USEHEADER)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None,
                         title="FastLogger")
        self.panel = MainPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_folder_menu_item = file_menu.Append(wx.ID_ANY, "Open File", "Open a log file")
        menu_bar.Append(file_menu, "&File")
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_open_folder,
            source=open_folder_menu_item,
        )
        self.SetMenuBar(menu_bar)

    def on_open_folder(self, event):
        title = "Choose a Log File:"
        dlg = wx.FileDialog(self, title, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.panel.open_log(dlg.GetPath())
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
