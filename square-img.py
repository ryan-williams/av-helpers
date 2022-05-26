#!/usr/bin/env python

from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output', nargs='?')
    parser.add_argument('-b', '--background', default='white')
    parser.add_argument('-m', '--method', default='contain', choices=['contain', 'cover'])
    args = parser.parse_args()

    input = args.input
    output = args.output or input
    background = args.background
    method = args.method

    if method == 'contain':
        distort = '%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]'
    elif method == 'cover':
        distort = '%[fx:min(w,h)]x%[fx:min(w,h)]+%[fx:max((w-h)/2,0)]+%[fx:max((h-w)/2,0)]'

    cmd = [
      'convert',
      input,
      '+set', 'date:create', '+set', 'date:modify',
      '-virtual-pixel', background,
      '-set', 'option:distort:viewport',
      distort,
      '-filter', 'point',
      '-distort', 'SRT', '0',
      '+repage',
      output,
    ]

    from subprocess import check_call
    print(cmd)
    check_call(cmd)


if __name__ == '__main__':
    main()
