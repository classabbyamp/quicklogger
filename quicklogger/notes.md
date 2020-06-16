# Parser Notes


## Rules

### Headers
`keyword value`

* `mycall`
* `mygrid`
* `operator`
* `qslmsg`
* `mywwff`
* `mysota`
* `mypota`
* `nickname`

### QSO Fields
A QSO must be on 1 line.

* date: `[date] YYYY-MM-DD` any separator fine, can abbreviate to `yy-m-d`
    * day: `day +[+...]` to increment (# of plus) days
* time: `[[H[H[M]]]M]` can leave out digits if same as previous
* callsign: `xx#xxxx` Only field required for a qso
* band: must be in valid bands, can be m, cm, mm
* frequency: in MHz, must be entered with a decimal pt in the number e.g. `3.545`
    * both freq and band can be specified but must match (band takes precedence)
* mode: must be in valid modes
* sent_rst: only need to enter when differs from 59(9), only have to enter the parts that were different, e.g. 5 -> 559
* rcvd_rst: same as sent but sent needs to be included if rcvd isn't 59(9), e.g. 9 5 -> 599 559
* notes: `< >` surrounds
* name: word starts with `@`
* grid: word starts with `#` (within qso line)
* qsl message: `[ ]` surrounds
* sent exchange: `,exchange`
* rcvd exchange: `.exchange`
* wwff: `wwff XFF-YYYY` (keyword required) X is prefix, YYYY is year
* sota: `[sota] x/x-xxx` (keyword optional) x/x-xxx is a sota designator
* pota: `pota x-xxxx` (keyword required) x-xxxx is a pota designator

### State Changes
Any number of these, in any order.

* date: `[date] YYYY-MM-DD` any separator fine, can abbreviate to `yy-m-d`
    * day: `day +[+...]` to increment (# of plus) days
* band: must be in valid bands, can also be frequency (MHz) or both (freq and band must match)
* mode: must be in valid modes

### Other
* `delete` or `drop` or `error`
    * if on own line: delete prev
    * if on same line: delete current
* Single line comment: `#` at start of line
* multi-line or within line comment: `{ }` surrounds
* Ignore blank lines

## Objects

### Headers

* `mycall {{callsign}}`
    * `^mycall\s+([A-Z0-9/]+)$`
* `mygrid {{grid}}`
    * `^mygrid\s+([A-R]{2}[0-9]{2}(?:[A-X]{2}(?:[0-9]{2})?)?)$`
* `operator {{op_call}}`
    * `^operator\s+([A-Z0-9/]+)$`
* `qslmsg {{default qsl message}}`
    * `^qslmsg\s+(.*)$`
* `mywwff {{XFF-YYYY}}`
    * `^mywwff\s+([A-Z0-9]{1,2}FF-\d{4})$`
* `mysota {{x/x-###}}`
    * `^mysota\s+([A-Z0-9]+/[A-Z0-9]+-\d{3})$`
* `mypota {{x-####}}`
    * `^mypota\s+([A-Z0-9]+-\d{4})$`
* `nickname {{qth nickname}}`
    * `^nickname\s+(.*)$`

### QSO Fields

* `[date] [yy]yy-[m]m-[d]d` (can be other separators)
    * `(?:date)?\s+(\d{2,4})\D(\d{1,2})\D(\d{1,2})`
* `[[H[H[M]]]M]`
    * `(\d{1,4})`
* `xxxxxxx` (callsign)
    * `([A-Z0-9/]+)`
* `xxxx[m,c]m` (band)
    * `(\d+[cm]?m)` and in band list
* `x.xxxx` (frequency)
    * `(\d+\.\d+)` and in ranges of freqs
* `xxx` (mode)
    * `([A-Z0-9]+)` and in mode list
* `###` (sent_rst)
    * `(\d{1,3})`
* `### ###` (sent and received rst)
    * `(\d{1,3})\s+(\d{1,3})`
* `<[ ]xxxx[ ]>` (notes)
    * `<\s*(.+)\s*>`
* `@xxxx` (name)
    * `@(\S+)`
* `#xxxx` (grid)
    * `#([A-R]{2}\d{2}(?:[A-X]{2}(?:\d{2})?)?)`
* `\[[ ]xxxx[ ]\]` (qsl message)
    * `\[\s*(.+)\s*\]`
* `,xxx` (sent exch)
    * `,(\S+)`
* `.xxx` (received exch)
    * `.(\S+)`
* `[wwff] XFF-YYYY`
    * `^(?:wwff)\s+([\w\d]{1,2}FF-\d{4})$`
* `[sota] x/x-###`
    * `^(?:sota)\s+([\w\d]+/[\w\d]+-\d{3})$`
* `[pota] x-####`
    * `^(?:pota)\s+([\w\d]+-\d{4})$`

### Other

* `^# xxxx` (single line comment)
    * `^#.*$`
* `\{\s*.*\s*\}` (inline/multi-line comment)
* `(delete|drop|error)`
* `^\s*$` (ignore empty)