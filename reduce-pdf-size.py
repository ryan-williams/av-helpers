#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///

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
@click.option('-c', '--compatibility-level', default='1.5', help='Compatibility level')
@click.option('-d', '--image-downsample-type', default='Bicubic', help='Image downsample type')
@click.option('-i', '--image-resolution', default=150, type=int, help='Image resolution in dpi')
@click.option('-r', '--reduce', count=True, help='0x: "printer", 1x: "prepress" (300 dpi), 2x: "ebook" (150 dpi), 3x: "screen" (72 dpi)"')
@click.argument('inpath')
@click.argument('outpath')
def main(compatibility_level, image_downsample_type, image_resolution, outpath, reduce, inpath):
    levels = {
        0: 'printer',
        1: 'prepress',
        2: 'ebook',
        3: 'screen',
    }
    level = levels[reduce]
    check_call([
        'gs',
        '-sDEVICE=pdfwrite',
        f'-dCompatibilityLevel={compatibility_level}',
        f'-dPDFSETTINGS=/{level}',
        f'-dColorImageDownsampleType=/{image_downsample_type}',
        f'-dColorImageResolution={image_resolution}',
        f'-dGrayImageDownsampleType=/{image_downsample_type}',
        f'-dGrayImageResolution={image_resolution}',
        f'-dMonoImageDownsampleType=/{image_downsample_type}',
        f'-dMonoImageResolution={image_resolution}',
        f'-dNOPAUSE',
        f'-dQUIET',
        f'-dBATCH',
        f'-sOutputFile={outpath}',
        inpath,
    ])


if __name__ == '__main__':
    main()
