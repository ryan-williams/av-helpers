#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///
import shlex

import click
from click import Choice
from subprocess import check_call


@click.command()
@click.option('-b', '--background', default='edge')
@click.option('-g', '--geometry')
@click.option('-m', '--method', default='contain', type=Choice(['contain', 'cover']))
@click.argument('in_path')
@click.argument('out_path', required=False)
def main(background, geometry, method, in_path, out_path):
    if not geometry:
        if method == 'contain':
            geometry = '%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]'
        elif method == 'cover':
            geometry = '%[fx:min(w,h)]x%[fx:min(w,h)]+%[fx:max((w-h)/2,0)]+%[fx:max((h-w)/2,0)]'

    cmd = [
        'convert',
        in_path,
        '+set', 'date:create', '+set', 'date:modify',
        '-virtual-pixel', background,
        '-set', 'option:distort:viewport',
        geometry,
        '-filter', 'point',
        '-distort', 'SRT', '0',
        '+repage',
        out_path,
    ]

    print(shlex.join(cmd))
    check_call(cmd)


if __name__ == '__main__':
    main()
