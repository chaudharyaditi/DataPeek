import sys
import os
import csv
import ctypes
import math
from typing import List, Tuple

# Shared library loader

def load_lib() -> ctypes.CDLL:
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    if sys.platform.startswith('win'):
        candidates = [os.path.join(here, 'csvstats.dll')]
    elif sys.platform == 'darwin':
        candidates = [os.path.join(here, 'libcsvstats.dylib'), os.path.join(here, 'csvstats.dylib')]
    else:
        candidates = [os.path.join(here, 'libcsvstats.so'), os.path.join(here, 'csvstats.so')]

    last_err = None
    for path in candidates:
        if os.path.exists(path):
            try:
                return ctypes.CDLL(path)
            except OSError as e:
                last_err = e
    msg = "\n".join([
        "Could not load the csvstats library.",
        "Tried these paths:",
        *candidates,
        f"Last error: {last_err}",
    ])
    raise RuntimeError(msg)

# CSV helpers

def sniff_dialect(path: str):
    with open(path, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
            dialect.skipinitialspace = True
            return dialect
        except csv.Error:
            # Fallback to comma
            class Simple:
                delimiter = ','
                quotechar = '"'
                doublequote = True
                skipinitialspace = True
                lineterminator = '\n'
                quoting = csv.QUOTE_MINIMAL
            return Simple()

def read_csv(path: str) -> Tuple[List[str], List[List[str]]]:
    dialect = sniff_dialect(path)
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, dialect)
        try:
            headers = next(reader)
        except StopIteration:
            return [], []
        rows = [row for row in reader]
    return headers, rows

# Numeric detection 

def to_float_or_none(s: str):
    if s is None:
        return None
    s = s.strip()
    if s == '':
        return None
    try:
        return float(s.replace(',', ''))
    except ValueError:
        return None

# Printing helpers 

def fmt(x: float) -> str:
    if x is None or math.isnan(x):
        return 'NA'
    txt = f"{x:.6f}"
    txt = txt.rstrip('0').rstrip('.') if '.' in txt else txt
    return txt

def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python csv_summarizer.py <file.csv>")
        return 1
    path = argv[1]
    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        return 1

    headers, rows = read_csv(path)
    n_rows = len(rows)
    n_cols = len(headers)

    print(f"File: {os.path.basename(path)}")
    print(f"Rows: {n_rows}")
    print(f"Columns: {n_cols}\n")

    if n_rows == 0 or n_cols == 0:
        print("(Empty file)")
        return 0

    # Transpose rows -> columns with padding
    columns: List[List[str]] = [[] for _ in range(n_cols)]
    for row in rows:
        for i in range(n_cols):
            val = row[i] if i < len(row) else ''
            columns[i].append(val)

    numeric_results = []  # (col_name, min, max, mean)

    for idx, col in enumerate(columns):
        nums = [to_float_or_none(x) for x in col]
        nums = [x for x in nums if x is not None and not math.isnan(x)]
        if len(nums) == 0:
            continue  
        mn, mx, mean = summarize(nums)
        name = headers[idx] if idx < len(headers) and headers[idx] else f"col_{idx}"
        numeric_results.append((name, mn, mx, mean))

    if not numeric_results:
        print("No numeric columns detected.")
        return 0

    print("Column summaries:")
    print("-" * 33)
    max_name = max(len(n[0]) for n in numeric_results)
    for name, mn, mx, mean in numeric_results:
        pad = ' ' * (max_name - len(name) + 2)
        print(f"{name}{pad}min={fmt(mn)}, max={fmt(mx)}, mean={fmt(mean)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
