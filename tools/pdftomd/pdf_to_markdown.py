#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Optional
import pymupdf4llm


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    page_chunks: bool = False,
    write_images: bool = False,
    image_path: Optional[str] = None,
    dpi: int = 150
) -> str:
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_file.suffix.lower() == '.pdf':
        raise ValueError(f"File must be a PDF: {pdf_path}")
    
    if output_path is None:
        output_path = pdf_file.with_suffix('.md')
    
    output_file = Path(output_path)
    
    if image_path is None and write_images:
        image_path = output_file.parent / f"{output_file.stem}_images"
    
    md_text = pymupdf4llm.to_markdown(
        doc=str(pdf_file),
        page_chunks=page_chunks,
        write_images=write_images,
        image_path=str(image_path) if image_path else None,
        dpi=dpi
    )
    
    if page_chunks:
        full_text = "\n\n---\n\n".join([page["text"] for page in md_text])
    else:
        full_text = md_text
    
    output_file.write_text(full_text, encoding='utf-8')
    
    print(f"✓ Converted: {pdf_file}")
    print(f"✓ Output: {output_file}")
    if write_images and image_path:
        print(f"✓ Images: {image_path}")
    
    return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF files to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf -o output.md
  %(prog)s document.pdf --write-images --dpi 300
  %(prog)s document.pdf --page-chunks
        """
    )
    
    parser.add_argument(
        'pdf_path',
        type=str,
        help='Path to the PDF file to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output markdown file path (default: same name as PDF with .md extension)'
    )
    
    parser.add_argument(
        '--page-chunks',
        action='store_true',
        help='Return text as a list of page chunks instead of single document'
    )
    
    parser.add_argument(
        '--write-images',
        action='store_true',
        help='Extract and save images from the PDF'
    )
    
    parser.add_argument(
        '--image-path',
        type=str,
        default=None,
        help='Directory to save extracted images (default: <output>_images/)'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='DPI for image extraction (default: 150)'
    )
    
    args = parser.parse_args()
    
    try:
        convert_pdf_to_markdown(
            pdf_path=args.pdf_path,
            output_path=args.output,
            page_chunks=args.page_chunks,
            write_images=args.write_images,
            image_path=args.image_path,
            dpi=args.dpi
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
