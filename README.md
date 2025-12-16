# 🐢 SVG to PDF Converter

Convert generative art SVGs to print-ready PDFs for large format printing!

## 🎨 What's This For?

Love the algorithmic art on [Turtletoy](https://turtletoy.net/)? Want to print it big and hang it on your wall? This tool takes those square SVG exports and converts them to print-ready PDFs sized for large format poster printing.

The output is optimized for services like [Officeworks poster printing](https://www.officeworks.com.au/) (Australia) or similar print shops that accept PDF uploads.

> **Note:** Turtletoy artwork is typically licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) - perfect for personal prints, just not for selling!

## ✨ Features

- 🐳 **Docker-based** - No messy local dependencies
- 🎯 **Three scaling modes** - Pick the best look for each artwork
- 🔍 **Smart background detection** - Automatically detects white or black backgrounds
- 🖨️ **Print-ready output** - 707mm × 1000mm @ 300 DPI, grayscale
- 📦 **Batch processing** - Convert entire folders at once

## 🖼️ Output Modes

For each SVG, three PDF variants are generated so you can pick the best one:

| Mode | Description | Best For |
|------|-------------|----------|
| **Centered** | SVG centered with padding above/below | Art that needs breathing room |
| **Stretched** | SVG stretched to fill (distorts) | Patterns that look good stretched |
| **Cropped** | SVG scaled up, edges cropped | Art where the center is the focus |

![Scaling modes diagram](https://via.placeholder.com/600x200?text=Centered+|+Stretched+|+Cropped)

## 🚀 Quick Start

1. Drop your SVG files into `./svgs/`
2. Run the converter:
   ```bash
   ./run.sh
   ```
3. Find your PDFs in `./output/`
4. Upload your favorite variant to your print shop!

## 📐 Print Specifications

| Property | Value |
|----------|-------|
| Physical size | 707mm × 1000mm |
| Pixels | 8350 × 11811 |
| Resolution | 300 DPI |
| Color mode | Grayscale |
| Input format | Square SVG |

## 🛠️ Requirements

- [Docker](https://www.docker.com/get-started)

That's it! Everything else runs inside the container.

## 📁 Project Structure

```
svg2pdf/
├── svgs/           # 📥 Put your SVGs here
├── output/         # 📤 PDFs appear here
├── run.sh          # 🚀 Run this
├── convert.py      # 🐍 Conversion logic
└── Dockerfile      # 🐳 Container config
```

## 🎯 Tips

- **Turtletoy export:** Use the SVG export button on any Turtletoy creation
- **Choosing a mode:** Start with "centered" for most art, try "cropped" if the edges are less interesting
- **Black backgrounds:** The tool auto-detects dark backgrounds and uses matching padding

## 📜 License

This tool is open source. Remember that the artwork you're converting may have its own license (Turtletoy uses CC BY-NC-SA 4.0 by default).

---

Made with 🤖 [Claude Code](https://claude.com/claude-code) for printing robot art on dead trees.
