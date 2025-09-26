#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///
import shlex
from os import environ
from subprocess import check_call, CalledProcessError
from sys import stderr

import click


@click.command()
@click.option('-b', '--background', default='black', help='Divider color')
@click.option('-g', '--gap-size', default=10, type=int, help='Gap size between images')
@click.option('-O', '--no-open', is_flag=True, help='Do not open the output image')
@click.option('-w', '--width', default=800, type=int, help='Width of the output image')
@click.argument("paths", nargs=-1)
def main(background, gap_size, no_open, width, paths):
    [ *inputs, output ] = paths
    if width:
        inputs = [ f"{path}[{width}x]" for path in inputs ]
    cmd = [
        "convert",
        *inputs,
        "-background", background,
        "-splice", f"x{gap_size}",
        "-gravity", "Center",
        "-append", "+gravity",
        "-chop", f"x{gap_size}+0+0",
        output,
    ]
    stderr.write(f'Running: {shlex.join(cmd)}\n')
    check_call(cmd)
    if not no_open:
        open_cmds = list(filter(None, [
            environ.get('OPEN_CMD'),
            'xdg-open',
            'open',
        ]))
        for open_cmd in open_cmds:
            try:
                check_call([open_cmd, output])
                return
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    main()
