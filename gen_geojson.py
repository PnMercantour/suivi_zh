#!/usr/bin/env python3
import argparse
from pathlib import Path

import psycopg2


def main(args):
    fp = Path(Path(__file__).parent, 'sql', 'zh_to_json.sql').open()
    sql = fp.read()
    fp.close()

    connection = psycopg2.connect(service='bd_pnm')

    cur = connection.cursor()
    cur.execute(sql)
    for (id, geojson) in cur:
        path = Path(args.dir, str(id) + '.json')
        print(path)
        fp = path.open(mode='x')
        fp.write(geojson)
        fp.close()
    cur.close()
    connection.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=Path, default=Path(Path(__file__).parent, 'assets', 'sites'),
                        help='Destination directory, defaults to current directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False, help='Verbose mode, print activity to stdout')

    args = parser.parse_args()
    args.dir.mkdir(parents=True, exist_ok=True)
    main(args)
