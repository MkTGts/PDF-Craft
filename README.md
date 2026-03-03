# PDF Craft 

A Python GUI application to split, join, and compress PDF files.
Version 0.0.1

## Features

### Split PDF
- **Each page → separate PDF** – Extract every page as its own file
- **Every N pages** – Split into chunks of N pages each (e.g., every 5 pages)
- **Extract only specific pages** – Extract only the pages you need (e.g., 1, 2, 5)

### Join PDF
- Select multiple PDF files and merge them into one
- Reorder files with Move up / Move down
- Remove or clear the list as needed

### Compress PDF
- Reduce PDF file size with lossless compression
- Content stream compression (FlateDecode) – up to ~70% reduction
- Remove duplicate and unused objects – up to ~86% reduction
- Both options can be combined for best results

## Installation

```bash
pip install -r requirements.txt
```

## Compiling to .exe
```
pyinstaller --onefile --windowed main.py or pyinstaller --onefile --windowed main_ru.py
```

## Usage

```bash
python main.py or dist/main.exe if compiled to .exe
```

1. Click **Browse...** to select your PDF file
2. Choose an output folder (defaults to the PDF's folder)
3. Select a split mode and configure options
4. Click **Split PDF**

## Requirements

- Python 3.8+
- pypdf
