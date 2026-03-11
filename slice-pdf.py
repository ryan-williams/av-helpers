#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# ///
from pathlib import Path
from shutil import which
from subprocess import run
from sys import stderr

from click import argument, command, option


def err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


@command()
@option('-o', '--output', help="Output PDF path (default: input_pXX-YY.pdf)")
@argument('input_pdf')
@argument('start_page', type=int)
@argument('end_page', type=int, required=False)
def main(output, input_pdf, start_page, end_page):
    """Extract pages from a PDF file (preserving form fields).

    Pages are 1-indexed. If end_page is omitted, extracts only start_page.

    Examples:
        slice-pdf input.pdf 5          # Extract page 5
        slice-pdf input.pdf 10 20      # Extract pages 10-20
        slice-pdf input.pdf 1 5 -o out.pdf
    """
    input_path = Path(input_pdf)
    if not input_path.exists():
        err(f"Error: Input file not found: {input_pdf}")
        raise SystemExit(1)

    if end_page is None:
        end_page = start_page

    if start_page < 1:
        err(f"Error: start_page must be >= 1")
        raise SystemExit(1)

    if end_page < start_page:
        err(f"Error: end_page ({end_page}) must be >= start_page ({start_page})")
        raise SystemExit(1)

    if not output:
        if start_page == end_page:
            output = f"{input_path.stem}_p{start_page}.pdf"
        else:
            output = f"{input_path.stem}_p{start_page}-{end_page}.pdf"

    if which("qpdf"):
        result = run(
            ["qpdf", input_pdf, "--pages", ".", f"{start_page}-{end_page}", "--", output],
            capture_output=True, text=True,
        )
        # qpdf exits 0 (success) or 3 (warnings but succeeded); both are fine
        if result.returncode not in (0, 3):
            err(result.stderr)
            raise SystemExit(result.returncode)
    else:
        err("Warning: qpdf not installed, falling back to pypdf (form fields may be lost)")
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            err("Error: neither qpdf nor pypdf available; install one: brew install qpdf")
            raise SystemExit(1)

        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)
        if end_page > total_pages:
            err(f"Error: end_page ({end_page}) exceeds total pages ({total_pages})")
            raise SystemExit(1)

        writer = PdfWriter()
        for page_num in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page_num])

        with open(output, 'wb') as f:
            writer.write(f)

    num_pages = end_page - start_page + 1
    size = Path(output).stat().st_size
    size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f}K" if size < 1024*1024 else f"{size/1024/1024:.1f}M"
    err(f"Extracted {num_pages} page(s) from {input_pdf}")
    err(f"Output: {output} ({size_str})")


if __name__ == '__main__':
    main()
