from pathlib import Path
from urllib.parse import quote
import csv

with Path('data/notice.csv').open('r') as csvfile:
    reader = csv.DictReader(csvfile)
    notices = [row for row in reader]

for dir in Path('dashboard/assets/pdf').iterdir():
    for path in dir.iterdir():
        print(quote(str(path)))
        print(str(path))

print(quote('é'))

for n in notices:
    print(quote(n['nom']))
    print(n['nom'])
