#!/usr/bin/env python
from __future__ import annotations

from functools import partial
from os.path import basename, splitext
import shlex
from sys import stdout

import click
from subprocess import check_call, check_output

err = partial(print, file=stdout)


def run(*args):
    cmd = [ str(arg) for arg in args ]
    err(f"Running: {shlex.join(cmd)}")
    check_call(cmd)


def normalize_color(color):
    if len(color) in [3, 4]:
        return ''.join( ch*2 for ch in color )
    elif len(color) in [6, 8]:
        return color
    else:
        raise ValueError(f'Unrecognized color: {color}')


@click.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('-b', '--background', help='Background color')
@click.option('-d', '--decode', help='Decode the URL from an existing QR code')
@click.option('-f', '--foreground', help='Foreground color')
@click.option('-m', '--margin', default=1, help='Margin around QR code (in "QR"-pixels)')
@click.option('-o', '--outname', help='Output path stem, e.g. "my-qr" will result in `my-qr.{png,svg}` being generated')
@click.option('-O', '--no-open', is_flag=True, help='Skip attempting to invoke `open` on the resulting QR code')
@click.option('-P', '--no-png', is_flag=True, help='Skip exporting a PNG')
@click.option('-s', '--pixel-size', default=10, help='Pixels per QR code "pixel"')
@click.option('-S', '--no-svg', is_flag=True, help='Skip exporting an SVG')
@click.option('-u', '--to-upper', is_flag=True, help='Convert the URL to upper-case (can result in smaller output QR codes)')
@click.argument('qrencode_args', nargs=-1, type=click.UNPROCESSED)
def main(
    background: str,
    decode: str | None,
    foreground: str,
    margin: int,
    outname: str,
    no_open: bool,
    no_png: bool,
    pixel_size: int,
    no_svg: bool,
    to_upper: bool,
    qrencode_args: tuple[str, ...],
):
    """`qrencode` wrapper, generates PNG+SVG by default, `open`s result."""
    do_open = not no_open
    do_png = not no_png
    do_svg = not no_svg

    if decode:
        [line] = list(filter(None, check_output(['zbarimg', decode]).decode().split('\n')))
        _, url = line.split(':', 1)
        err(f"Decoded {url=} from {decode}")
    else:
        [ *qrencode_args, url ] = qrencode_args

    if to_upper:
        url = url.upper()
        err(f"Converted to upper-case: {url}")

    if outname is None:
        outname = splitext(basename(url))[0]

    qrencode_args = qrencode_args or []
    base_cmd = [ 'qrencode', '-s', pixel_size, '-m', margin, ]
    if foreground:
        foreground = normalize_color(foreground)
        base_cmd += [ f'--foreground={foreground}' ]
    if background:
        background = normalize_color(background)
        base_cmd += [ f'--background={background}' ]
    base_cmd += qrencode_args

    outpaths = []

    def write_fmt(fmt):
        outpath = f'{outname}.{fmt}'
        cmd = base_cmd + [ '-t', fmt, '-o', outpath, url ]
        run(*cmd)
        nonlocal outpaths
        outpaths += [ outpath ]
        return outpath

    png_outpath = None
    if do_png:
        png_outpath = write_fmt('png')

    svg_outpath = None
    if do_svg:
        svg_outpath = write_fmt('svg')

    if do_open:
        open_path = png_outpath or svg_outpath
        if open_path:
            run('open', open_path)


if __name__ == '__main__':
    main()
