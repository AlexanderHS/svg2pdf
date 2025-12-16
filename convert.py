#!/usr/bin/env python3
"""
SVG to PDF converter with three scaling strategies:
- Centered: Scale to fit width, center vertically with background color padding
- Stretched: Scale to exact dimensions (distorted)
- Cropped: Scale to fit height, crop horizontally from center
"""

import os
import sys
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Physical dimensions: 707mm x 1000mm @ 300 DPI
# 707mm = 27.835 inches * 300 DPI = 8350 pixels
# 1000mm = 39.37 inches * 300 DPI = 11811 pixels
TARGET_WIDTH = 8350
TARGET_HEIGHT = 11811
TARGET_DPI = 300

def detect_background_color(svg_path):
    """
    Detect the background color of an SVG file.
    Returns 'white' or 'black'.

    Strategy:
    1. Check SVG attributes (viewport-fill, style background)
    2. Look for a background rect element with explicit fill
    3. Render with white bg and sample - if corners differ significantly, it has its own bg
    """
    from PIL import Image

    try:
        # First, parse SVG and look for explicit background indicators
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Check viewport-fill attribute
        viewport_fill = root.get('viewport-fill', '')
        if viewport_fill:
            if any(b in viewport_fill.lower() for b in ['#000', 'black', 'rgb(0,0,0)']):
                return 'black'
            elif any(w in viewport_fill.lower() for w in ['#fff', 'white', 'rgb(255,255,255)']):
                return 'white'

        # Check style attribute for background
        style = root.get('style', '')
        if 'background' in style.lower():
            if 'black' in style.lower() or '#000' in style.lower():
                return 'black'
            elif 'white' in style.lower() or '#fff' in style.lower():
                return 'white'

        # Look for a full-size background rect (first rect at 0,0 with 100% size)
        for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
            x = rect.get('x', '0')
            y = rect.get('y', '0')
            width = rect.get('width', '')
            height = rect.get('height', '')
            fill = rect.get('fill', '')
            rect_style = rect.get('style', '')

            # Check if this looks like a background rect
            is_at_origin = x in ['0', '0px', ''] and y in ['0', '0px', '']
            is_full_size = ('100%' in width or '100%' in height or
                          width == root.get('width') or height == root.get('height'))

            if is_at_origin and is_full_size:
                if fill:
                    if any(b in fill.lower() for b in ['#000', 'black']):
                        return 'black'
                    elif any(w in fill.lower() for w in ['#fff', 'white']):
                        return 'white'
                if 'fill:' in rect_style:
                    if any(b in rect_style.lower() for b in ['fill:#000', 'fill:black']):
                        return 'black'
                    elif any(w in rect_style.lower() for w in ['fill:#fff', 'fill:white']):
                        return 'white'

        # Fallback: render to PNG and check if corners are opaque and dark
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_png = tmp.name

        try:
            # Render WITHOUT background to preserve transparency
            subprocess.run([
                'inkscape',
                '--export-type=png',
                '--export-filename=' + tmp_png,
                '--export-width=100',
                '--export-height=100',
                str(svg_path)
            ], check=True, capture_output=True)

            img = Image.open(tmp_png)

            # Check if image has alpha channel
            if img.mode == 'RGBA':
                # Sample corners for alpha - if transparent, there's no explicit background
                width, height = img.size
                margin = 2
                corners = [
                    (margin, margin),
                    (width - margin - 1, margin),
                    (margin, height - margin - 1),
                    (width - margin - 1, height - margin - 1)
                ]

                transparent_corners = 0
                dark_corners = 0

                for x, y in corners:
                    pixel = img.getpixel((x, y))
                    alpha = pixel[3] if len(pixel) > 3 else 255
                    if alpha < 128:
                        transparent_corners += 1
                    else:
                        brightness = sum(pixel[:3]) / 3
                        if brightness < 64:  # Very dark
                            dark_corners += 1

                # If corners are mostly transparent, no explicit background
                if transparent_corners >= 3:
                    return 'white'  # Default to white for transparent SVGs

                # If corners are opaque and dark, it's a black background
                if dark_corners >= 3:
                    return 'black'

        finally:
            if os.path.exists(tmp_png):
                os.unlink(tmp_png)

    except Exception as e:
        print(f"  Warning: Background detection failed: {e}")

    return 'white'  # Default to white


def convert_centered(svg_path, output_pdf, background_color):
    """
    Centered mode: Scale square SVG to 2004x2004, center vertically with padding.
    """
    print(f"  Converting centered mode with {background_color} background...")

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_png = tmp.name

    try:
        # Step 1: Convert SVG to PNG at target width (2004x2004)
        # Use --export-background to handle SVGs with transparent backgrounds
        subprocess.run([
            'inkscape',
            '--export-type=png',
            '--export-filename=' + tmp_png,
            '--export-width=' + str(TARGET_WIDTH),
            '--export-height=' + str(TARGET_WIDTH),
            '--export-background=' + background_color,
            str(svg_path)
        ], check=True, capture_output=True)

        # Step 2: Add padding, convert to grayscale, set correct DPI for 707x1000mm
        subprocess.run([
            'convert',
            tmp_png,
            '-gravity', 'center',
            '-background', background_color,
            '-extent', f'{TARGET_WIDTH}x{TARGET_HEIGHT}',
            '-colorspace', 'Gray',
            '-density', str(TARGET_DPI),
            '-units', 'PixelsPerInch',
            output_pdf
        ], check=True, capture_output=True)

    finally:
        if os.path.exists(tmp_png):
            os.unlink(tmp_png)


def convert_stretched(svg_path, output_pdf):
    """
    Stretched mode: Scale to exact dimensions (aspect ratio ignored).
    """
    print(f"  Converting stretched mode...")

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_png = tmp.name

    try:
        # Convert SVG to PNG at exact target dimensions
        subprocess.run([
            'inkscape',
            '--export-type=png',
            '--export-filename=' + tmp_png,
            '--export-width=' + str(TARGET_WIDTH),
            '--export-height=' + str(TARGET_HEIGHT),
            str(svg_path)
        ], check=True, capture_output=True)

        # Convert PNG to PDF with grayscale and correct DPI for 707x1000mm
        subprocess.run([
            'convert',
            tmp_png,
            '-colorspace', 'Gray',
            '-density', str(TARGET_DPI),
            '-units', 'PixelsPerInch',
            output_pdf
        ], check=True, capture_output=True)

    finally:
        if os.path.exists(tmp_png):
            os.unlink(tmp_png)


def convert_cropped(svg_path, output_pdf):
    """
    Cropped mode: Scale so height fills 2835 (square becomes 2835x2835),
    then crop 415.5 pixels from each side horizontally.
    """
    print(f"  Converting cropped mode...")

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_png = tmp.name

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp2:
        tmp_png_cropped = tmp2.name

    try:
        # Step 1: Convert SVG to PNG at target height (2835x2835 for square)
        subprocess.run([
            'inkscape',
            '--export-type=png',
            '--export-filename=' + tmp_png,
            '--export-width=' + str(TARGET_HEIGHT),
            '--export-height=' + str(TARGET_HEIGHT),
            str(svg_path)
        ], check=True, capture_output=True)

        # Step 2: Crop from center to target width
        # Crop: 2835 wide -> 2004 wide = remove 831 pixels (415.5 from each side)
        subprocess.run([
            'convert',
            tmp_png,
            '-gravity', 'center',
            '-crop', f'{TARGET_WIDTH}x{TARGET_HEIGHT}+0+0',
            '+repage',
            tmp_png_cropped
        ], check=True, capture_output=True)

        # Step 3: Convert cropped PNG to PDF with grayscale and correct DPI
        subprocess.run([
            'convert',
            tmp_png_cropped,
            '-colorspace', 'Gray',
            '-density', str(TARGET_DPI),
            '-units', 'PixelsPerInch',
            output_pdf
        ], check=True, capture_output=True)

    finally:
        if os.path.exists(tmp_png):
            os.unlink(tmp_png)
        if os.path.exists(tmp_png_cropped):
            os.unlink(tmp_png_cropped)


def process_svg(svg_path, output_dir):
    """
    Process a single SVG file and generate all three variants.
    """
    svg_path = Path(svg_path)
    output_dir = Path(output_dir)

    # Get base filename without extension
    base_name = svg_path.stem

    print(f"\nProcessing: {svg_path.name}")

    # Detect background color
    background_color = detect_background_color(svg_path)
    print(f"  Detected background: {background_color}")

    # Generate three variants
    try:
        centered_pdf = output_dir / f"{base_name}-centered.pdf"
        convert_centered(svg_path, centered_pdf, background_color)
        print(f"  ✓ Created: {centered_pdf.name}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error creating centered PDF: {e}")
        if e.stderr:
            print(f"    stderr: {e.stderr.decode()[:500]}")
    except Exception as e:
        print(f"  ✗ Error creating centered PDF: {e}")

    try:
        stretched_pdf = output_dir / f"{base_name}-stretched.pdf"
        convert_stretched(svg_path, stretched_pdf)
        print(f"  ✓ Created: {stretched_pdf.name}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error creating stretched PDF: {e}")
        if e.stderr:
            print(f"    stderr: {e.stderr.decode()[:500]}")
    except Exception as e:
        print(f"  ✗ Error creating stretched PDF: {e}")

    try:
        cropped_pdf = output_dir / f"{base_name}-cropped.pdf"
        convert_cropped(svg_path, cropped_pdf)
        print(f"  ✓ Created: {cropped_pdf.name}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error creating cropped PDF: {e}")
        if e.stderr:
            print(f"    stderr: {e.stderr.decode()[:500]}")
    except Exception as e:
        print(f"  ✗ Error creating cropped PDF: {e}")


def main():
    input_dir = Path('/input')
    output_dir = Path('/output')

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all SVG files
    svg_files = sorted(input_dir.glob('*.svg'))

    # Filter out Zone.Identifier files
    svg_files = [f for f in svg_files if not f.name.endswith(':Zone.Identifier')]

    if not svg_files:
        print("No SVG files found in input directory!")
        sys.exit(1)

    print(f"Found {len(svg_files)} SVG file(s) to process")
    print(f"Target dimensions: {TARGET_WIDTH}x{TARGET_HEIGHT} pixels")
    print("=" * 60)

    # Process each SVG
    for svg_file in svg_files:
        process_svg(svg_file, output_dir)

    print("\n" + "=" * 60)
    print(f"Processing complete! Check {output_dir} for output PDFs.")
    print(f"Each SVG generated 3 variants: -centered.pdf, -stretched.pdf, -cropped.pdf")


if __name__ == '__main__':
    main()
