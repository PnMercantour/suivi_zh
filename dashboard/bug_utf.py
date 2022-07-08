from pathlib import Path
from urllib.parse import quote
import csv
import json


def to_dict(l, key='id'):
    "builds a dict from an iterable <l>, indexing on <key>"
    return {i[key]: i for i in l}


with Path('data/notice.csv').open('r') as csvfile:
    reader = csv.DictReader(csvfile)
    notices = [row for row in reader]

for dir in Path('dashboard/assets/pdf').iterdir():
    for path in dir.iterdir():
        print('file', quote(str(path)))
        # print(str(path))

print(quote('é'))

for n in notices:
    print('csv', quote(n['nom']))
    # print(n['nom'])

with Path('dashboard/assets/notice.json').open('r') as f:
    notice_data = to_dict([notice['properties']
                           for notice in json.load(f)['features']])
for n in notice_data.values():
    print('notice_data', quote(n['nom']))
    # print(n['nom'])
