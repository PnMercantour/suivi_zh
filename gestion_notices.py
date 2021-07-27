#!/usr/bin/env python3
import argparse
from pathlib import Path

import psycopg2


def main(args):
    if args.execute:
        connection = psycopg2.connect(service='bd_pnm')
        cur = connection.cursor()
        # cur.execute('set role postgres')
        for path in args.root.joinpath('final 2018 2019').iterdir():
            if path.match('*.pdf'):
                print(path.relative_to(args.root))
                cur.execute(
                    f"insert into eau_zh.notice(nom, date) values('{path.relative_to(args.root)}', '2018-09-30')")
        cur.close()
        connection.commit()
    else:
        for path in args.root.joinpath('final 2018 2019').iterdir():
            if path.match('*.pdf'):
                print(path.relative_to(args.root))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=Path,
                        help='subdirectory to scan')
    parser.add_argument('-r', '--root', type=Path,
                        default=Path().resolve(), help='Root directory')
    parser.add_argument('-x', '--execute', action='store_true',
                        default=False, help='To actually write to database')
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False, help='Verbose mode, print activity to stdout')

    args = parser.parse_args()

    main(args)
