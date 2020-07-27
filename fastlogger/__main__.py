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


class FLLogEditor(wx.Panel):
    auto_incr = False

    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)

        log_editor_sizer = wx.GridSizer(1, 1, 0, 0)

        self.log_editor = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.log_editor.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Consolas"))

        log_editor_sizer.Add(self.log_editor, 0, wx.EXPAND, 0)
        self.SetSizer(log_editor_sizer)
        self.Layout()

        self.Bind(wx.EVT_TEXT, self.update_log_viewer, self.log_editor)

    def open_file(self, event: wx.CommandEvent):
        title = "Open a Log"
        dlg = wx.FileDialog(self, title, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.log_editor.LoadFile(dlg.GetPath())
        dlg.Destroy()

    def update_log_viewer(self, event: wx.CommandEvent):
        text = event.GetString()
        log = logparser.LogFile(text.split("\n"), self.auto_incr)

        log_viewer = self.Parent.log_viewer_pane.log_viewer

        log_viewer.DeleteAllItems()

        for i, r in enumerate(log):
            log_viewer.InsertItem(i, str(i+1))
            for j, itm in enumerate(r.values()):
                if isinstance(itm, float):
                    itm = f"{itm:.3f}"
                elif isinstance(itm, time):
                    itm = time.strftime(itm, "%H:%M")
                else:
                    itm = str(itm)

                log_viewer.SetItem(i, j+1, itm)
            # self.row_objs.append(r)

        for idx in range(log_viewer.GetColumnCount()):
            log_viewer.SetColumnWidth(idx, wx.LIST_AUTOSIZE_USEHEADER)


class FLLogViewer(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)

        log_viewer_sizer = wx.GridSizer(1, 1, 0, 0)

        self.log_viewer = wx.ListCtrl(self, wx.ID_ANY, style=wx.BORDER_SUNKEN | wx.LC_REPORT | wx.LC_VRULES)

        for idx, itm in enumerate(col_headings):
            self.log_viewer.InsertColumn(idx, itm, width=140)

        for idx in range(self.log_viewer.GetColumnCount()):
            self.log_viewer.SetColumnWidth(idx, wx.LIST_AUTOSIZE_USEHEADER)

        log_viewer_sizer.Add(self.log_viewer, 1, wx.EXPAND, 0)

        self.SetSizer(log_viewer_sizer)

        self.Layout()


class FLLogWindow(wx.SplitterWindow):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.SP_LIVE_UPDATE
        wx.SplitterWindow.__init__(self, *args, **kwds)

        self.log_editor_pane = FLLogEditor(self, wx.ID_ANY)
        self.log_viewer_pane = FLLogViewer(self, wx.ID_ANY)
        self.SetMinimumPaneSize(20)

        self.SplitVertically(self.log_editor_pane, self.log_viewer_pane, sashPosition=0)


class FLMainPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)

        main_sizer = wx.GridSizer(1, 1, 0, 0)

        self.log_window = FLLogWindow(self, wx.ID_ANY)
        main_sizer.Add(self.log_window, 1, wx.EXPAND, 0)

        self.SetSizer(main_sizer)

        self.Layout()


class FLMainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("FastLogger")

        self.menubar = FLMenuBar()
        self.SetMenuBar(self.menubar)

        self.toolbar = FLToolBar(self, -1)
        self.SetToolBar(self.toolbar)

        self.main_panel = FLMainPanel(self, wx.ID_ANY)
        self.Layout()

        self.Bind(event=wx.EVT_MENU, handler=self.main_panel.log_window.log_editor_pane.open_file,
                  source=self.menubar.open_log)


class FLMenuBar(wx.MenuBar):
    def __init__(self, *args, **kwds):
        wx.MenuBar.__init__(self, *args, **kwds)
        self.create_file_menu()
        self.create_edit_menu()

    def create_file_menu(self):
        wxglade_tmp_menu = wx.Menu()
        self.open_log = wxglade_tmp_menu.Append(wx.ID_ANY, "Open Log...", "")
        self.Append(wxglade_tmp_menu, "File")

    def create_edit_menu(self):
        wxglade_tmp_menu = wx.Menu()
        self.Append(wxglade_tmp_menu, "Edit")


class FLToolBar(wx.ToolBar):
    def __init__(self, *args, **kwds):
        wx.ToolBar.__init__(self, *args, **kwds)

        self.AddTool(wx.ID_OPEN, "Open", wx.Bitmap(16, 16), wx.NullBitmap, wx.ITEM_NORMAL,
                     "Open a file.", "Open a log file.")
        self.AddTool(wx.ID_SAVE, "Save", wx.Bitmap(16, 16), wx.NullBitmap, wx.ITEM_NORMAL,
                     "Save the open file.", "Save the open log file.")
        self.Realize()


class FLApp(wx.App):
    def OnInit(self):
        self.main_frame = FLMainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.main_frame)
        self.main_frame.Show()
        return True


if __name__ == "__main__":
    FastLogger = FLApp(0)
    FastLogger.MainLoop()
