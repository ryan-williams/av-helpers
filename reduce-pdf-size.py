#!/usr/bin/env python

# From https://www.journaldev.com/34668/reduce-pdf-file-size-in-linux:
#
# -dPDFSETTINGS=/screen	    Has a lower quality and smaller size. (72 dpi)
# -dPDFSETTINGS=/ebook	    Has a better quality, but has a slightly larger size (150 dpi)
# -dPDFSETTINGS=/prepress	Output is of a higher size and quality (300 dpi)
# -dPDFSETTINGS=/printer	Output is of a printer type quality (300 dpi)
# -dPDFSETTINGS=/default	Selects the output which is useful for multiple purposes. Can cause large PDFS.

from subprocess import check_call

import click


@click.command()
@click.option('-r', '--reduce', count=True, help='1x: "prepress" (300 dpi), 2x: "ebook" (150 dpi), 3x: "screen" (72 dpi)"')
@click.argument('inpath')
@click.argument('outpath')
def main(reduce, inpath, outpath):
    levels = {
        1: 'prepress',
        2: 'ebook',
        3: 'screen',
    }
    level = levels[reduce]
    check_call([ 'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', f'-dPDFSETTINGS=/{level}', '-dNOPAUSE', '-dQUIET', '-dBATCH', f'-sOutputFile={outpath}', inpath, ])
