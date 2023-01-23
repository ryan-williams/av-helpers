#!/usr/bin/env python
import shlex
from os import stat

import click
from subprocess import check_call


@click.command()
@click.option('-o', '--outname', required=False,)
@click.option('-p', '--page',)
@click.option('-r', '--dpi', default=150, type=int,)
@click.option('-x', type=float,)
@click.option('-y', type=float,)
@click.option('-w', '--width', 'w', type=float,)
@click.option('-h', '--height', 'h', type=float,)
@click.argument('pdf')
def main(outname, page, dpi, x, y, w, h, pdf):
    x *= dpi ; x = str(int(x))
    y *= dpi ; y = str(int(y))
    w *= dpi ; w = str(int(w))
    h *= dpi ; h = str(int(h))
    suffix = f'_r{dpi}_x{x}_y{y}_w{w}_h{h}'
    outname += suffix
    outpath = outname + '.png'
    cmd = [
        'pdftoppm',
        '-x', x,
        '-y', y,
        '-W', w,
        '-H', h,
        '-r', f'{dpi}',
        '-png',
        '-f', page,
        '-l', page,
        '-singlefile',
        pdf,
        outname,
    ]
    print(f'Running: {shlex.join(cmd)}')
    check_call(cmd)
    print(f'Size: {stat(outpath).st_size}')
    check_call(['file', outpath])
    check_call(['open', outpath])


if __name__ == '__main__':
    main()
