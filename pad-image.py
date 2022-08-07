#!/usr/bin/env python

import click
from os import makedirs
from os.path import dirname, exists
from subprocess import check_call


@click.command()
@click.option('-b', '--background', default='black')
@click.option('-e', '--extent', '<w>x<h>', help="Overall image size (defaults to -g/--geometry value)")
@click.option('-g', '--geometry', '<w>x<h>', required=True, help="Resized image size")
@click.argument('inpath')
@click.argument('outpath')
def main(background, extent, geometry, inpath, outpath):
    outdir = dirname(outpath)
    if outdir and not exists(outdir):
        makedirs(outdir, exist_ok=True)
    extent = extent or geometry
    check_call([
        'convert', inpath,
        '-resize', geometry,
        '-background', background,
        '-gravity', 'center',
        '-extent', extent,
        outpath,
    ])


if __name__ == '__main__':
    main()
