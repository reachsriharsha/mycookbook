# PDF to Markdown Converter

A Python tool to convert PDF files to Markdown format with support for image extraction and page-based chunking.

## Features

- Convert PDF documents to clean Markdown format
- Extract and save images from PDFs
- Optional page-by-page chunking
- Configurable DPI for image extraction
- Command-line interface and Python API

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

**Basic conversion:**
```bash
python pdf_to_markdown.py document.pdf
```

**Specify output file:**
```bash
python pdf_to_markdown.py document.pdf -o output.md
```

**Extract images:**
```bash
python pdf_to_markdown.py document.pdf --write-images --dpi 300
```

**Convert with page chunks:**
```bash
python pdf_to_markdown.py document.pdf --page-chunks
```

**Custom image directory:**
```bash
python pdf_to_markdown.py document.pdf --write-images --image-path ./my_images
```

### Python API

```python
from pdf_to_markdown import convert_pdf_to_markdown

# Basic conversion
convert_pdf_to_markdown('document.pdf')

# With options
convert_pdf_to_markdown(
    pdf_path='document.pdf',
    output_path='output.md',
    write_images=True,
    image_path='./images',
    dpi=300
)
```

## Command Line Options

- `pdf_path` - Path to the PDF file to convert (required)
- `-o, --output` - Output markdown file path (default: same name as PDF with .md extension)
- `--page-chunks` - Return text as page chunks separated by horizontal rules
- `--write-images` - Extract and save images from the PDF
- `--image-path` - Directory to save extracted images (default: `<output>_images/`)
- `--dpi` - DPI for image extraction (default: 150)

## Dependencies

- **pymupdf4llm** - High-level PDF to Markdown conversion
- **pymupdf** - PDF processing library

## Output

The tool generates:
- A Markdown file with the converted content
- (Optional) A directory containing extracted images
- Console output showing the conversion status

## Examples

Convert a research paper with high-quality images:
```bash
python pdf_to_markdown.py research_paper.pdf --write-images --dpi 300
```

Convert a book and organize by pages:
```bash
python pdf_to_markdown.py book.pdf --page-chunks -o book_output.md
```

## Notes

- Images are referenced in the Markdown using relative paths
- Page chunks are separated by `---` horizontal rules
- The tool preserves text formatting, tables, and document structure
- Supports all PDF versions compatible with PyMuPDF
