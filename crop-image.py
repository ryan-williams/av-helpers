#!/usr/bin/env python
import re
from os import makedirs, cpu_count
from os.path import splitext, basename, exists

import click
from joblib import Parallel, delayed
from utz import process, parallel


class Dims:
    DIM_STR_RGX = re.compile(r'(?P<w>\d+)[ x](?P<h>\d+)')

    def __init__(self, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                m = self.DIM_STR_RGX.fullmatch(arg)
                if not m:
                    raise ValueError(f"Unrecognized arg: {arg}")
                self.w = int(m['w'])
                self.h = int(m['h'])
            else:
                raise ValueError(f"Unrecognized arg: {arg}")
        elif len(args) == 2:
            self.w = int(args[0])
            self.h = int(args[1])
        else:
            raise ValueError(f"Unrecognized args: {args}")

    def __str__(self):
        return f'{self.w}x{self.h}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self})'

    def __add__(l, r):
        if isinstance(r, Dims):
            return Dims(l.w + r.w, l.h + r.h)
        else:
            raise ValueError("Unrecognized arg: {r}")

    def __sub__(l, r):
        if isinstance(r, Dims):
            return Dims(l.w - r.w, l.h - r.h)
        else:
            raise ValueError("Unrecognized arg: {r}")


@click.command()
@click.option('-j', '--n-jobs', default=0, type=int)
@click.option('-n', '--dry-run', is_flag=True)
@click.option('-o', '--out-dir', help='')
@click.option('--number-from', '--nf', type=int, default=None, help='')
@click.option('--top-left-size', '--tl', help='')
@click.option('--final-size', '--fs', help='')
@click.argument('inputs', nargs=-1)
def main(n_jobs, dry_run, out_dir, number_from, top_left_size, final_size, inputs):
    top_left_size = Dims(top_left_size)
    final_size = Dims(final_size)

    n = len(inputs)
    max_len = len(str(n + (number_from or 0) - 1))
    fmt = f'%0{max_len}d'

    def crop(idx, path):
        name, ext = splitext(basename(path))
        if number_from is not None:
            name = fmt % (idx + number_from)
        out_name = f'{name}{ext}'
        if out_dir:
            if not exists(out_dir):
                makedirs(out_dir)
            out_path = f'{out_dir}/{out_name}'
        else:
            out_path = out_name

        orig = Dims(process.line('convert', path, '+profile', '*', '-print', r'%w %h\n', '/dev/null'))
        top_left_offset = orig - top_left_size
        dimensions_str = f'{final_size}+{top_left_offset.w}+{top_left_offset.h}'

        process.run('convert', '-crop', dimensions_str, path, out_path, dry_run=dry_run)

    if n_jobs == 1 or len(inputs) == 1:
        for idx, path in enumerate(inputs):
            crop(idx, path)
    else:
        n_jobs = n_jobs or cpu_count()
        Parallel(n_jobs=n_jobs)(delayed(crop)(idx, path) for idx, path in enumerate(inputs))


if __name__ == '__main__':
    main()
