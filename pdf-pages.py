#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click", "pypdf"]
# ///
from pathlib import Path
from sys import stderr

from click import argument, command
from pypdf import PdfReader


def err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


@command()
@argument('pdfs', nargs=-1, required=True)
def main(pdfs):
    """Show number of pages in PDF file(s)."""
    for pdf_path in pdfs:
        path = Path(pdf_path)
        if not path.exists():
            err(f"Error: File not found: {pdf_path}")
            continue

        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            if len(pdfs) == 1:
                print(num_pages)
            else:
                print(f"{num_pages}\t{pdf_path}")
        except Exception as e:
            err(f"Error reading {pdf_path}: {e}")


if __name__ == '__main__':
    main()
