
#!/usr/bin/env python3
"""
parser.py - part of quicklogger
---

Copyright (C) 2020 classabbyamp
This software is released under the BSD 3-Clause license.
"""

from typing import List, Sequence, Dict, AnyStr, Union
import collections.abc as abc
from datetime import datetime, timedelta, MINYEAR
import re


class LogFile(abc.Sequence):
    def __init__(self, data: Sequence[str], auto_incr: bool = False):
        self.my_call = ""
        self.my_grid = ""
        self.operators = []
        self.qsl_msg = ""
        self.my_wwff = ""
        self.my_sota = ""
        self.my_pota = ""
        self.qth_nickname = ""
        self._auto_exch = auto_incr
        self._raw_data = tuple(data)
        self._data = self._parse(data)

    def _parse(self, data: List[str]):
        rows = list()
        curr_datetime = datetime(MINYEAR, 1, 1)
        curr_band = None
        curr_freq = None
        curr_mode = None
        comment = False

        for i, ln in enumerate(data):
            ln = ln.strip()
            call = None
            notes = None
            sent_rst = None
            rcvd_rst = None
            grid = None
            name = None
            qsl_msg = None
            sent_exch = None
            rcvd_exch = None
            wwff = None
            sota = None
            pota = None

            # single line comment or empty line
            if not ln or ln.startswith("#"):
                continue

            # multi-line comment
            clean_ln = ""
            for char in ln:
                # not in a comment
                if not comment:
                    # if a comment starts, don't add it and turn on the comment flag
                    if char == "{":
                        comment = True
                    # otherwise, add the char to the commentless string
                    else:
                        clean_ln += char
                # in a comment
                else:
                    # if a comment ends, turn off the comment flag
                    if char == "}":
                        comment = False
                    # otherwise, keep going
                    else:
                        continue
            ln = clean_ln

            # delete, drop, error: remove previous log entry
            if ln.lower() in ["delete", "drop", "error"]:
                rows.pop()

            # headers
            elif m := re.match(r"mycall\s*([\w\d/]+)?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.my_call = m.group(1).upper()

            elif m := re.match(r"mygrid\s*([A-R]{2}[0-9]{2}(?:[A-X]{2}(?:[0-9]{2})?)?)?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.my_grid = m.group(1).upper()

            elif m := re.match(r"op(?:erator)?s?\s*((?:[\w\d\/]{3,}\s*)+)?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    for op in m.group(1).upper().split():
                        self.operators.append(op)

            elif m := re.match(r"qslmsg\s*(.*)?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.qsl_msg = m.group(1)

            elif m := re.match(r"mywwff\s*([\w\d]{1,2}FF-\d{4})?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.my_wwff = m.group(1).upper()

            elif m := re.match(r"mysota\s*([\w\d]+/[\w\d]+-\d{3})?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.my_sota = m.group(1).upper()

            elif m := re.match(r"mypota\s*([\w\d]+-\d{4})?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.my_pota = m.group(1).upper()

            elif m := re.match(r"nickname\s*(.*)?", ln, re.I):
                if len(m.groups()) and m.group(1):
                    self.qth_nickname = m.group(1)

            # qsos
            else:
                # notes
                if m := re.search(r"\<\s*?(.+)\s*?\>", ln, re.I):
                    notes = m.group(1)
                    ln = ln.replace(m.group(0), "", 1)

                # qsl msg
                if m := re.search(r"\b\[\s*(.+)\s*\]", ln, re.I):
                    qsl_msg = m.group(1)
                    ln = ln.replace(m.group(0), "", 1)

                # band
                if m := re.search(r"(?:\s|^)(\d+[cm]?m)\b", ln, re.I):
                    if (b := m.group(1).lower()) in bands.keys():
                        curr_band = b
                    ln = ln.replace(m.group(0), "", 1)

                # frequency
                if m := re.search(r"(?:\s|^)(\d+\.\d+)(?:\s|$)", ln, re.I):
                    for min_f, max_f in bands.values():
                        if min_f <= (f := float(m.group(1))) <= max_f:
                            curr_freq = f
                            break
                    ln = ln.replace(m.group(1), "", 1)

                # date
                if m := re.search(r"(?:\s|^)(?:date)?\s+(\d{2,4})\D(\d{1,2})\D(\d{1,2})\b", ln, re.I):
                    # 2 digit year
                    if len(y := m.group(1)) == 2:
                        if int("20" + y) >= datetime.today().year:
                            y = int("19" + y)
                        else:
                            y = int("20" + y)
                    else:
                        # 3 digit year
                        if len(y) == 3 and y[0] == 9:
                            y = int("1" + y)
                        elif len(y) == 3:
                            y = int("2" + y)
                        else:
                            y = int(y)
                    if len(mo := m.group(2)) == 1:
                        mo = int("0" + m)
                    else:
                        mo = int(mo)
                    if len(d := m.group(3)) == 1:
                        d = int("0" + d)
                    else:
                        d = int(d)
                    curr_datetime = datetime(y, mo, d, hour=curr_datetime.hour, minute=curr_datetime.minute)
                    ln = ln.replace(m.group(0), "", 1)
                elif m := re.match(r"day\s*(\++)", ln, re.I):
                    curr_datetime += timedelta(days=len(m.group(1)))
                    ln = ln.replace(m.group(0), "", 1)

                # time
                if m := re.search(r"(?:\s|^)(\d{1,4})\b", ln, re.I):
                    if len(t := m.group(1)) <= 2:
                        curr_datetime += timedelta(seconds=int(t)*60)
                    elif len(t) == 3:
                        curr_datetime += timedelta(seconds=int(t[0:1])*3600 + int(t[1:])*60)
                    else:
                        curr_datetime += timedelta(seconds=int(t[0:2])*3600 + int(t[2:])*60)
                    ln = ln.replace(m.group(1), "", 1)

                # mode
                if m := re.search(r"(?:\s|^)([\w\d]+)\b", ln, re.I):
                    if (mode := m.group(1).upper()) in modes:
                        curr_mode = mode
                        ln = ln.replace(m.group(0), "", 1)
                # callsign
                if m := re.search(r"(?:\s|^)([\w\d\/]{3,})\b", ln, re.I):
                    call = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # name
                if m := re.search(r"(?:\s|^)@(.+?)\b", ln, re.I):
                    name = m.group(1).title()
                    ln = ln.replace(m.group(0), "", 1)

                # grid
                if m := re.search(r"(?:\s|^)#(.+?)\b", ln, re.I):
                    grid = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # sent exchange
                if m := re.search(r"(?:\s|^),(.+?)\b", ln, re.I):
                    sent_exch = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # received exchange
                if m := re.search(r"(?:\s|^)\.(.+?)\b", ln, re.I):
                    rcvd_exch = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # wwff
                if m := re.search(r"(?:\s|^)(?:wwff)?\s+([\w\d]{1,2}FF-\d{4})\b", ln, re.I):
                    wwff = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # sota
                if m := re.search(r"(?:\s|^)(?:sota)?\s+([\w\d]+/[\w\d]+-\d{3})\b", ln, re.I):
                    sota = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # pota
                if m := re.search(r"(?:\s|^)(?:pota)?\s+([\w\d]+-\d{4})\b", ln, re.I):
                    pota = m.group(1).upper()
                    ln = ln.replace(m.group(0), "", 1)

                # sent and received rst
                if m := re.search(r"\b([+-]?\d{1,3})\s*([+-]?\d{1,3})?\b", ln, re.I):
                    if len(m.groups()) == 2:
                        sent_rst = process_rst(m.group(1), curr_mode)
                        rcvd_rst = process_rst(m.group(2), curr_mode)
                    else:
                        rcvd_rst = process_rst(m.group(1), curr_mode)
                    ln = ln.replace(m.group(0), "", 1)
                if re.search(r"(?:\s|^)(delete|drop|error)\b", ln, re.I):
                    continue

                default_rst = "599" if curr_mode in ["CW", "RTTY", "PSK"] else "59"

                if curr_band and curr_freq and not (bands[curr_band][0] <= curr_freq <= bands[curr_band][1]):
                    curr_freq = None

                if not sent_exch and len(rows) and (p_sent_exch := rows[-1].sent_exch):
                    if self._auto_exch:
                        sent_exch = str(int(p_sent_exch) + 1)
                    else:
                        sent_exch = p_sent_exch

                if call:
                    row = {
                        "date_time": curr_datetime,
                        "band": curr_band,
                        "freq": curr_freq,
                        "mode": curr_mode,
                        "call": call,
                        "sent_rst": sent_rst if sent_rst else default_rst,
                        "rcvd_rst": rcvd_rst if rcvd_rst else default_rst,
                        "notes": notes,
                        "name": name,
                        "grid": grid,
                        "qsl_msg": qsl_msg,
                        "sent_exch": sent_exch,
                        "rcvd_exch": rcvd_exch,
                        "wwff": wwff,
                        "sota": sota,
                        "pota": pota,
                    }
                    rows.append(LogRow(row))
        
        self.operators = tuple(set(self.operators))

        return tuple(rows)

    # --- Wrappers to implement sequence-like functionality ---
    def __len__(self):
        return len(self._data)

    def __getitem__(self, index: Union[int, slice]):
        return self._data[index]

    def __iter__(self):
        return iter(self._data)


class LogRow(abc.Mapping):
    def __init__(self, data):
        self._data = data
        # required
        self.date_time: datetime = data["date_time"]
        self.band: str = data["band"]
        self.freq: float = data["freq"]
        self.mode: str = data["mode"]
        self.call: str = data["call"]
        # RST
        self.sent_rst: str = data.get("sent_rst", None)
        self.rcvd_rst: str = data.get("rcvd_rst", None)
        # optional
        self.notes: str = data.get("notes", None)
        self.name: str = data.get("name", None)
        self.grid: str = data.get("grid", None)
        self.qsl_msg: str = data.get("qsl_msg", None)
        # contest
        self.sent_exch: str = data.get("sent_exch", None)
        self.rcvd_exch: str = data.get("rcvd_exch", None)
        # WWFF
        self.wwff: str = data.get("wwff", None)
        # SOTA
        self.sota: str = data.get("sota", None)
        # POTA
        self.pota: str = data.get("pota", None)
    
    def __str__(self):
        return str(self._data)

    # --- Wrappers to implement mapping-like functionality ---
    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)


class QLParsingError(Exception):
    def __init__(self, msg, line_num, line):
        self.msg = msg
        self.line_num = line_num + 1 # make it human-readable
        self.line = line


def process_rst(raw: str, mode: str):
    if not raw or raw[0] in ["+", "-"]:
        return raw
    elif mode in ["CW", "RTTY", "PSK"]:
        if len(raw) == 3:
            return raw
        elif len(raw) == 2:
            if int(raw[0]) < 5:
                return raw + "9"
            elif int(raw[0]) < 9:
                return "5" + raw
            else:
                return raw
        elif len(raw) == 1:
            if int(raw) < 5:
                return raw + "99"
            elif int(raw) < 9:
                return "5" + raw + "9"
            else:
                return raw
        else:
            return raw
    elif mode in ["SSB", "AM", "FM", "LSB", "USB"]:
        if len(raw) == 2:
            return raw
        if len(raw) == 1:
            if int(raw) < 5:
                return raw + "9"
            elif int(raw) < 9:
                return "5" + raw
        else:
            return raw
    else:
        return raw


bands = {
    # wl: (lower f, upper f)
    # [pfx]metres (MHz, MHz)
    "2200m": (0.1357, 0.1358),
    "630m": (0.472, 0.479),
    "160m": (1.8, 2.0),
    "80m": (3.5, 4.0),
    "60m": (5.06, 5.45),
    "40m": (7.0, 7.3),
    "30m": (10.1, 10.15),
    "20m": (14.0, 14.35),
    "17m": (18.068, 18.168),
    "15m": (21.0, 21.45),
    "12m": (24.89, 24.99),
    "10m": (28.0, 29.7),
    "6m": (50.0, 54.0),
    "4m": (70.0, 71.0),
    "2m": (144.0, 148.0),
    "1.25m": (222.0, 225.0),
    "70cm": (420.0, 450.0),
    "33cm": (902.0, 928.0),
    "23cm": (1240.0, 1300.0),
    "13cm": (2300.0, 2450.0),
    "9cm": (3300.0, 3500.0),
    "6cm": (5650.0, 5925.0),
    "3cm": (10000.0, 10500.0),
    "1.25cm": (24000.0, 24250.0),
    "6mm": (47000.0, 47200.0),
    "4mm": (75500.0, 81000.0),
    "2.5mm": (119980.0, 120020.0),
    "2mm": (142000.0, 149000.0),
    "1mm": (241000.0, 250000.0),
}

modes = [
    "CW",
    "SSB",
    "USB",
    "LSB",
    "AM",
    "FM",
    "RTTY",
    "FT8",
    "PSK",
    "JT65",
    "JT9",
    "FT4",
    "JS8",
    "ARDOP",
    "ATV",
    "C4FM",
    "CHIP",
    "CLO",
    "CONTESTI",
    "DIGITALVOICE",
    "DOMINO",
    "DSTAR",
    "FAX",
    "FSK441",
    "HELL",
    "ISCAT",
    "JT4",
    "JT6M",
    "JT44",
    "MFSK",
    "MSK144",
    "MT63",
    "OLIVIA",
    "OPERA",
    "PAC",
    "PAX",
    "PKT",
    "PSK2K",
    "Q15",
    "QRA64",
    "ROS",
    "RTTYM",
    "SSTV",
    "T10",
    "THOR",
    "THRB",
    "TOR",
    "V4",
    "VOI",
    "WINMOR",
    "WSPR",
]