#!/usr/bin/env python3

from argparse import ArgumentParser
from functools import cached_property
from subprocess import check_call, check_output, CalledProcessError

parser = ArgumentParser()
parser.add_argument('input')
parser.add_argument('crop', help='[x1]-[x2],[y1-y2]')
parser.add_argument('output', nargs='?')
parser.add_argument('-n', '--dry-run', action='store_true')
parser.add_argument('-o', '--open', action='store_true')
args, extras = parser.parse_known_args()

from re import match

input = args.input
[ horz, vert ] = args.crop.split(',')

_dims = None
def dims():
    global _dims
    if not _dims:
        _dims = dict([
            tuple(line.split('='))
            for line in
            check_output([
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'default=noprint_wrappers=1',
                args.input,
            ]) \
            .decode() \
            .split('\n')
            if line
        ])
        _dims = { k: int(v) for k, v in _dims.items() }
    return _dims


def num(s, default): return int(s) if s else default

class Range:
    def __init__(self, s, key):
        self.s = s
        self.key = key

        # start_end = r'(?P<start>\d*)-(?P<end>\d*)'
        # start_size = r'(?P<start>\d*)\+(?P<size>\d*)'
        # regex = f'(?:{start_end}|{start_size})'
        # m = match(regex, s)
        # if m:
        #     start = int(m['start']) if m and m['start'] else 0
        #
        # else:
        #     raise ValueError(f'Unrecognized crop rect: {s}')

        def num(m, k, default):
            return \
                int(m[k]) \
                    if m and m[k] \
                    else (
                        default()
                        if callable(default)
                        else default
                    )

        m = match(r'(?P<start>\d*):(?P<end>\d*)', s)
        if m or not s:
            start = num(m, 'start', 0)
            end = num(m, 'end', self.max)
            if end < 0: end = self.max() + end
            size = end - start
        else:
            m = match(r'(?P<start>\d*)\+(?P<size>\d*)', s)
            if m:
                start = int(m['start']) if m['start'] else 0
                size = int(m['size']) if m['size'] else (self.max() - start)
                end = start + size
            else:
                raise ValueError(f'Unrecognized crop rect: {s}')

        self.start = start
        self.end = end
        self.size = size

    def max(self):
        if not hasattr(self, '_max'): self._max = dims()[self.key]
        return self._max

    @property
    def dims(self): return ( self.start, self.size )

    def __str__(self):
        if not self.s: return ''
        start_min = not self.start
        size_max = self.start + self.size == self.max()
        if start_min and size_max: return ''
        if size_max: return f'{self.start}+'
        if start_min: return f'+{self.size}'
        return f'{self.start}+{self.size}'


horz = Range(horz, 'width')
vert = Range(vert, 'height')
[ x, w ] = horz.dims
[ y, h ] = vert.dims


def get_output(input, crop):
    [ base, extension ] = input.rsplit('.', 1)
    return f'{base}-{crop}.{extension}'


output = args.output or get_output(input, f'{horz},{vert}')


cmd = [ 'ffmpeg', '-i', input, '-filter:v', f'crop={w}:{h}:{x}:{y}', '-c:a', 'copy', ] + extras + [ output ]
print(' '.join(cmd))
if not args.dry_run:
    check_call(cmd)

if args.open:
    try:
        check_call([ 'open', output ])
    except CalledProcessError:
        pass
