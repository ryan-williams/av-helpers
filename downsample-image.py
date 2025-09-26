#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///
from os import makedirs
from os.path import dirname
import shlex
from subprocess import check_call

import click


@click.command()
@click.argument('pct', type=int)
@click.argument('input')
@click.argument('output', required=False)
def main(pct, input, output):
    output = output or f'{pct}p/{input}'
    outdir = dirname(output)
    makedirs(outdir, exist_ok=True)
    cmd = ['convert', '-resize', f'{pct}%', input, output]
    print(f'Running: {shlex.join(cmd)}')
    check_call(cmd)


if __name__ == '__main__':
    main()
