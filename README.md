# SVG to PDF Converter

A Docker-based tool for converting SVG files to print-ready PDFs at 707mm x 1000mm (8350x11811 pixels @ 300 DPI).

## Overview

This tool processes SVG files and generates three PDF variants for each input file, allowing you to choose the best scaling approach for printing:

- **Centered** - SVG centered with padding (maintains aspect ratio)
- **Stretched** - SVG stretched to fill page (may distort)
- **Cropped** - SVG scaled up and cropped from center

## Features

- Docker-based (no local dependencies except Docker)
- Automatic background color detection (white or black)
- Print-ready output at 300 DPI
- Grayscale output for printing
- Processes all SVGs in batch
- Handles filenames with spaces

## Usage

Simply run:

```bash
./run.sh
```

This will:
1. Build the Docker image (first time only)
2. Process all SVG files in `./svgs/`
3. Output PDFs to `./output/`

## Output

For each `example.svg` file, three PDFs are generated:

- `example-centered.pdf` - SVG scaled to fit width (8350px), centered vertically with padding
- `example-stretched.pdf` - SVG stretched to exactly 8350x11811 (aspect ratio ignored)
- `example-cropped.pdf` - SVG scaled to fill height (11811px), cropped horizontally from center

All PDFs are 707mm x 1000mm (8350x11811 pixels) at 300 DPI in grayscale.

## Requirements

- Docker

## Technical Details

### Dimensions
- Physical size: 707mm x 1000mm
- Pixels: 8350 x 11811
- Resolution: 300 DPI
- Color mode: Grayscale
- Input: Square aspect ratio SVGs

### Scaling Strategies

**Centered Mode:**
- Scales square SVG to 8350x8350 pixels
- Centers vertically on 11811-tall canvas
- Fills padding with detected background color (white or black)

**Stretched Mode:**
- Scales SVG to exactly 8350x11811 pixels
- Ignores aspect ratio (may distort)

**Cropped Mode:**
- Scales square SVG to 11811x11811 pixels (to fill height)
- Crops horizontally from center to 8350px wide
- Centers the crop

### Background Detection

For centered mode, the tool automatically detects the SVG's background color:
- Checks for background rectangles in the SVG
- Samples corner pixels if needed
- Defaults to white if detection is inconclusive

## Files

- `Dockerfile` - Container configuration with Inkscape and ImageMagick
- `convert.py` - Python conversion script
- `run.sh` - Wrapper script to build and run
- `svgs/` - Input directory (add your SVG files here)
- `output/` - Output directory (PDFs generated here)
