#!/usr/bin/env python3
"""
quicklogger
---

Copyright (C) 2020 classabbyamp
This software is released under the BSD 3-Clause license.
"""

from pathlib import Path
import tabulate

import parser

test_file_dir = Path("./testlogs")

while True:
    for i, f in enumerate(fns := [x for x in test_file_dir.iterdir() if not x.is_dir()]):
        print(f"({i}) {f}")

    try:
        fn = fns[int(input("Choose a file: "))]
    except ValueError:
        break
    except IndexError:
        print("Not Found!")
        continue

    with open(fn) as file:
        try:
            log = parser.LogFile(file.readlines())
        except parser.QLParsingError as e:
            print(f"[!!] {e.msg} on Line {e.line_num}:\n    {e.line}")
        else:
            print("My Call:", log.my_call)
            print("My Grid:", log.my_grid)
            print("Operators:", ", ".join(log.operators))
            print("My QSL Message:", log.qsl_msg)
            print("My WWFF:", log.my_wwff)
            print("My SOTA:", log.my_sota)
            print("My QTH Nickname:", log.qth_nickname)
            header = log[0].keys()
            rows = [x.values() for x in log]
            print(tabulate.tabulate(rows, header))