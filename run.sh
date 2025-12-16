#!/bin/bash

# SVG to PDF Converter - Docker wrapper script
# This script builds the Docker image and runs the conversion

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="svg2pdf-converter"

echo "=========================================="
echo "SVG to PDF Converter"
echo "=========================================="
echo ""

# Build Docker image
echo "Building Docker image..."
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
echo ""

# Create output directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/output"

# Run conversion
echo "Running conversion..."
echo ""
docker run --rm \
    -v "$SCRIPT_DIR/svgs:/input:ro" \
    -v "$SCRIPT_DIR/output:/output" \
    "$IMAGE_NAME"

echo ""
echo "=========================================="
echo "Done! Check ./output/ for PDF files."
echo "=========================================="
