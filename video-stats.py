#!/usr/bin/env python
import re

import json
import sys

import click
from humanize import naturalsize
from utz import process, singleton


def stderr(msg=''):
    sys.stderr.write(msg)
    sys.stderr.write('\n')


@click.command()
@click.option('-H', '--no-human-readable', is_flag=True)
@click.option('-j', '--json', 'output_json', is_flag=True)
@click.argument('filename')
def main(no_human_readable, output_json, filename):
    human_readable = not no_human_readable
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-select_streams', 'v:0',
        *(['-sexagesimal'] if human_readable else []),
        '-show_entries', 'format=filename,bit_rate,duration',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        '-i', filename,
    ]
    o = process.json(*cmd, log=stderr)
    stream = singleton(o['streams'], dedupe=False)
    format = o['format']
    width = stream['width']
    height = stream['height']
    duration = format['duration']
    bit_rate = format['bit_rate']
    if human_readable:
        bit_rate = re.sub('B$', 'bps', naturalsize(bit_rate))
    else:
        bit_rate = f'{bit_rate}bps'

    obj = {
        'width': width,
        'height': height,
        'duration': duration,
        'bit_rate': bit_rate,
    }
    if output_json:
        print(json.dumps(obj, indent=2))
    else:
        for k, v in obj.items():
            print(f'{k}: {v}')
        # print(f'{filename}: {width}x{height}, duration: {duration}, {bit_rate}ps')


if __name__ == '__main__':
    main()
