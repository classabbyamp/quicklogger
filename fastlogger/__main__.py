"""
logparser test interface
---

Copyright (C) 2020 classabbyamp
This software is released under the BSD 3-Clause license.
"""

from datetime import datetime

import wx

import logparser


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.row_objs = list()

        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 100),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, "Date", width=140)
        self.list_ctrl.InsertColumn(1, "Time", width=140)
        self.list_ctrl.InsertColumn(2, "Band", width=200)
        self.list_ctrl.InsertColumn(3, "Frequency", width=200)
        self.list_ctrl.InsertColumn(4, "Mode", width=200)
        self.list_ctrl.InsertColumn(5, "Callsign", width=200)
        self.list_ctrl.InsertColumn(6, "Sent RST", width=200)
        self.list_ctrl.InsertColumn(7, "Received RST", width=200)
        self.list_ctrl.InsertColumn(8, "Name", width=200)
        self.list_ctrl.InsertColumn(9, "Grid", width=200)
        self.list_ctrl.InsertColumn(10, "Sent Exchange", width=200)
        self.list_ctrl.InsertColumn(11, "Received Exchange", width=200)
        self.list_ctrl.InsertColumn(12, "Their WWFF", width=200)
        self.list_ctrl.InsertColumn(13, "Their SOTA", width=200)
        self.list_ctrl.InsertColumn(14, "Their POTA", width=200)
        self.list_ctrl.InsertColumn(15, "QSL Message", width=200)
        self.list_ctrl.InsertColumn(16, "Notes", width=200)

        for idx in range(self.list_ctrl.GetColumnCount()):
            self.list_ctrl.SetColumnWidth(idx, wx.LIST_AUTOSIZE_USEHEADER)

        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def update_log(self, path):
        self.list_ctrl.ClearAll()

        self.list_ctrl.InsertColumn(0, "", width=40)
        self.list_ctrl.InsertColumn(1, "Date", width=100)
        self.list_ctrl.InsertColumn(2, "Time", width=80)
        self.list_ctrl.InsertColumn(3, "Band", width=80)
        self.list_ctrl.InsertColumn(4, "Frequency", width=100)
        self.list_ctrl.InsertColumn(5, "Mode", width=80)
        self.list_ctrl.InsertColumn(6, "Callsign", width=120)
        self.list_ctrl.InsertColumn(7, "Sent RST", width=80)
        self.list_ctrl.InsertColumn(8, "Received RST", width=80)
        self.list_ctrl.InsertColumn(9, "Name", width=140)
        self.list_ctrl.InsertColumn(10, "Grid", width=80)
        self.list_ctrl.InsertColumn(11, "Sent Exchange", width=100)
        self.list_ctrl.InsertColumn(12, "Received Exchange", width=100)
        self.list_ctrl.InsertColumn(13, "Their WWFF", width=100)
        self.list_ctrl.InsertColumn(14, "Their SOTA", width=100)
        self.list_ctrl.InsertColumn(15, "Their POTA", width=100)
        self.list_ctrl.InsertColumn(16, "QSL Message", width=200)
        self.list_ctrl.InsertColumn(17, "Notes", width=200)

        with open(path) as file:
            log = logparser.LogFile(file.readlines())

        for i, r in enumerate(log):
            self.list_ctrl.InsertItem(i, str(i+1))
            self.list_ctrl.SetItem(i, 1, datetime.strftime(r.date_time, "%Y-%m-%d"))
            self.list_ctrl.SetItem(i, 2, datetime.strftime(r.date_time, "%H:%M"))
            self.list_ctrl.SetItem(i, 3, r.band)
            self.list_ctrl.SetItem(i, 4, f"{r.freq:.3f}" if isinstance(r.freq, float) else r.freq)
            self.list_ctrl.SetItem(i, 5, r.mode)
            self.list_ctrl.SetItem(i, 6, r.call.replace("0", "Ø"))
            self.list_ctrl.SetItem(i, 7, str(r.sent_rst))
            self.list_ctrl.SetItem(i, 8, str(r.rcvd_rst))
            self.list_ctrl.SetItem(i, 9, r.name)
            self.list_ctrl.SetItem(i, 10, r.grid)
            self.list_ctrl.SetItem(i, 11, r.sent_exch)
            self.list_ctrl.SetItem(i, 12, r.rcvd_exch)
            self.list_ctrl.SetItem(i, 13, r.wwff)
            self.list_ctrl.SetItem(i, 14, r.sota)
            self.list_ctrl.SetItem(i, 15, r.pota)
            self.list_ctrl.SetItem(i, 16, r.qsl_msg)
            self.list_ctrl.SetItem(i, 17, r.notes)
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
            self.panel.update_log(dlg.GetPath())
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
