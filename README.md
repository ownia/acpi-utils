# acpi-utils

Some useful ACPI utilities.

#### PPTT Parser
It will parse a PPTT aml and output a topology svg.
```
python3 pptt_parser.py PPTT.aml
```

#### FPDT Parser
It will parse FPDT table and print information
```
acpidump -n FPDT -b
python3 fpdt_parser.py fpdt.dat
```
