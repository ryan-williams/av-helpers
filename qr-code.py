#!/usr/bin/env python

from os.path import basename, splitext
import shlex

import click
from subprocess import check_call


def run(*args):
    print(f"Running: {shlex.join(args)}")
    check_call(args)


def normalize_color(color):
    if len(color) in [3, 4]:
        return ''.join( ch*2 for ch in color )
    elif len(color) in [6, 8]:
        return color
    else:
        raise ValueError(f'Unrecognized color: {color}')


@click.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('-b', '--background')
@click.option('-f', '--foreground')
@click.option('-m', '--margin', default='1')
@click.option('-o', '--outname')
@click.option('-O', '--no-open', is_flag=True)
@click.option('-P', '--no-png', is_flag=True)
@click.option('-s', '--pixel-size', default='10')
@click.option('-S', '--no-svg', is_flag=True)
@click.argument('qrencode_args', nargs=-1, type=click.UNPROCESSED)
def main(background, foreground, margin, outname, no_open, no_png, pixel_size, no_svg, qrencode_args):
    do_open = not no_open
    do_png = not no_png
    do_svg = not no_svg

    [ *qrencode_args, url ] = qrencode_args
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
