#!/usr/bin/env python
import sys

import click
from humanize import naturalsize
from utz import process, singleton


def stderr(msg=''):
    sys.stderr.write(msg)
    sys.stderr.write('\n')


@click.command()
@click.option('-h', '--human-readable', is_flag=True)
@click.argument('filename')
def main(human_readable, filename):
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
        bit_rate = naturalsize(bit_rate)
        duration = f'{duration}s'
    else:
        bit_rate = f'{bit_rate}b'
    print(f'{filename}: {width}x{height}, duration: {duration}, {bit_rate}ps')


if __name__ == '__main__':
    main()
