#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///
from os.path import exists, splitext
from pathlib import Path
from subprocess import check_call
from sys import stderr

from click import argument, command, option


def err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


@command()
@option('-O', '--no-open', is_flag=True, help="Don't open output file after creation")
@option('-o', '--output', help="Output file or directory")
@argument('pct', type=int)
@argument('inputs', nargs=-1, required=True)
def main(no_open, output, pct, inputs):
    """Resize image(s) by percentage using ImageMagick.

    If multiple inputs are provided, output must be a directory or omitted.
    """
    inputs = list(inputs)
    output_files = []

    if output and len(inputs) > 1:
        output_path = Path(output)
        if not output_path.is_dir() and not output.endswith('/'):
            err(f"Error: Multiple inputs require output to be a directory")
            raise SystemExit(1)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)

    for input_file in inputs:
        input_path = Path(input_file)
        if not input_path.exists():
            err(f"Error: Input file not found: {input_file}")
            raise SystemExit(1)

        if output:
            out_path = Path(output)
            if out_path.is_dir() or output.endswith('/'):
                out_path = out_path / input_path.name
            elif len(inputs) == 1:
                if not splitext(output)[1]:
                    ext = input_path.suffix
                    out_path = Path(f"{output}{ext}")
                    err(f"Adding extension: {ext}")
            output_file = str(out_path)
        else:
            stem = input_path.stem
            ext = input_path.suffix
            output_file = f"{stem}_{pct}p{ext}"

        check_call(['magick', input_file, '-resize', f'{pct}%', output_file])

        size = Path(output_file).stat().st_size
        size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f}K" if size < 1024*1024 else f"{size/1024/1024:.1f}M"
        err(f"Output: {output_file} ({size_str})")
        output_files.append(output_file)

    if not no_open and output_files:
        check_call(['open'] + output_files)


if __name__ == '__main__':
    main()
