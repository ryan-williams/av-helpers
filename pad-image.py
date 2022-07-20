#!/usr/bin/env python

import click
from os import makedirs
from os.path import dirname
from subprocess import check_call


@click.command()
@click.option('-b', '--background', default='black')
@click.option('-g', '--geometry', '<w>x<h>')
@click.argument('inpath')
@click.argument('outpath')
def main(background, geometry, inpath, outpath):
    makedirs(dirname(outpath), exist_ok=True)
    check_call([ 'convert', inpath, '-resize', geometry, '-background', background, '-gravity', 'center', '-extent', geometry, outpath, ])


if __name__ == '__main__':
    main()
