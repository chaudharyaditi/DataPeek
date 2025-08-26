# DataPeek 📊
a tiny and simple command-line tool that gives you a quick statistical peek into your csv files. nothing fancy; just rows, columns, and some basic stats for any numeric columns (min, max, mean)!

## usage
```bash
python3 csvsummarizer.py path/to/data.csv
```
## example output
```text
file: data.csv
rows: 1024
columns: 5

column summaries:
---------------------------------
age   min=18, max=72, mean=35.4
score min=0,  max=100, mean=74.2
price min=4.99, max=199.99, mean=52.6
```

## requirements
- python 3.8+   