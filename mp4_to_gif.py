#!/usr/bin/env python
# Convert a portion of an MP4 to GIF, cf. https://superuser.com/a/556031

from argparse import ArgumentParser
from os.path import splitext
from subprocess import check_call


parser = ArgumentParser()
parser.add_argument('-f','--fps',default=10)
parser.add_argument('-s','--start')
parser.add_argument('-t','--to')
parser.add_argument('-w','--width',default=800)
parser.add_argument('-y','--overwrite',action='store_true')
parser.add_argument('input')
parser.add_argument('output',nargs='?')

args = parser.parse_args()
fps = args.fps
start = args.start
to = args.to
width = args.width
overwrite = args.overwrite

input = args.input
output = args.output

cmd = [
    'ffmpeg',
    '-i',input
]

if overwrite: cmd += ['-y']
if start: cmd += ['-ss',str(start)]
if to: cmd += ['-to',str(to)]

cmd += [
    '-vf',f'fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
    '-loop','0'
]

if not output:
    name, ext = splitext(input)
    output = name
    output += f'_{fps}fps'
    if start: output += f'_ss{start}'
    if to: output += f'_to{to}'
    output += '.gif'

cmd += [output]

check_call(cmd)
