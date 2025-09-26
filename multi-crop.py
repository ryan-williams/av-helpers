#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///

import click
from os import makedirs
from os.path import basename, exists, isfile
import shlex
from subprocess import check_call


def run(*cmd):
    print(f'Running: {shlex.join(cmd)}')
    check_call(cmd)


@click.command()
@click.option('-g', '--geometry', help='<w>x<h>+<l>+<r>')
@click.option('-o', '--outdir', default='cropped', help='Cropped files, and any derived images, will be written to this directory. Default: `cropped`')
@click.option('-O', '--open', 'do_open', is_flag=True, help='Open generated image')
@click.option('-s', '--sxs', is_flag=True, help='Build a side-by-side montage at `<outdir>/sxs.png`')
@click.option('-S', '--sxspath', help='Build a side-by-side montage at this path')
@click.argument('inpaths', nargs=-1)
def main(geometry, outdir, do_open, sxs, sxspath, inpaths):
    print(f'geometry {geometry}, outdir {outdir}, sxs {sxs}, inpaths {inpaths}')
    if exists(outdir):
        if isfile(outdir):
            raise ValueError('Output must be a directory')
    else:
        makedirs(outdir)

    outpaths = []
    for inpath in inpaths:
        name = basename(inpath)
        print(f'Cropping {inpath}, geometry {geometry}')
        outpath = f'{outdir}/{name}'
        run('convert', '-strip', '-crop', geometry, inpath, outpath)
        outpaths += [ outpath ]

    if sxs or sxspath:
        sxspath = sxspath or f'{outdir}/sxs.png'
        run(*(['montage', ] + outpaths + [ '-tile', f'{len(outpaths)}x1', '-geometry', '+0+0', sxspath, ]))

        if do_open:
            run('open', sxspath)


if __name__ == '__main__':
    main()
