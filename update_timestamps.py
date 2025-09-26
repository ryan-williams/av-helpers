#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click", "pytz", "utz"]
# ///
from tempfile import TemporaryDirectory

import json
import pytz
import re

from datetime import datetime

import click
from utz import process, singleton, err

PREFIX_REGEX = re.compile(r'(?:QuickTime|Track\d+):')
YES_RGX = re.compile(r'(?:y(?:es)?)?', re.IGNORECASE)


@click.command('update_timestamps.py')
@click.option('-i', '--in-place', count=True, help='Modify PATH in place; 1x: prompt first, 2x: no prompt')
@click.option('-r', '--tag-regex', 'tag_regexs', multiple=True, help=f'Only include tags matching this regex. Can be passed multiple times. Default: {PREFIX_REGEX.pattern}')
@click.option('-z', '--from-time-zone', default='America/New_York', help='Interpret existing EXIF times as being in this time zone. Default: %(default)s')
@click.option('-Z', '--to-time-zone', default='UTC', help='Convert EXIF times to this time zone (TZ info itself will be omitted, as EXIF doesn\'t support it). Default: %(default)s')
@click.argument("path", type=click.Path(exists=True))
def main(in_place, tag_regexs, from_time_zone, to_time_zone, path):
    """Update EXIF timestamps in PATH to be in a different time zone.

    They will remain "naive" (no TZ info) as EXIF doesn't support TZ info, but the time value will be adjusted to
    correspond to the new time zone.

    By default, times are moved from "America/New_York" to "UTC".
    """
    if tag_regexs:
        tag_regexs = [ re.compile(rgx) for rgx in tag_regexs ]
    else:
        tag_regexs = [PREFIX_REGEX]

    res = process.json("exiftool", "-time:all", "-G1", "-a", "-s", "-j", path)
    tags = singleton(res, dedupe=False)

    from_tz = pytz.timezone(from_time_zone)
    to_tz = pytz.timezone(to_time_zone)

    def convert(v):
        naive_dt = datetime.strptime(v, "%Y:%m:%d %H:%M:%S")
        dt = from_tz.localize(naive_dt)
        if to_time_zone:
            dt = dt.astimezone(to_tz)
        return dt.isoformat()

    new_tags = {
        k: convert(v) if any(rgx.match(k) for rgx in tag_regexs) else v
        for k, v in tags.items()
    }

    print(json.dumps([new_tags], indent=2))

    def prompt():
        while True:
            resp = input(f'Update {path}? [Y/n] ')
            if YES_RGX.fullmatch(resp):
                return True
            elif resp.lower() == 'n':
                return False
            else:
                err('Invalid response')

    if in_place == 1 and prompt() or in_place == 2:
        with TemporaryDirectory() as tmpdir:
            exif_json_path = f'{tmpdir}/exif.json'
            with open(exif_json_path, 'w') as f:
                json.dump([new_tags], f, indent=2)
        process.run('exiftool', '-overwrite_original', '-P', '-json', exif_json_path, path)


if __name__ == "__main__":
    main()
