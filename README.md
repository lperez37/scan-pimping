<div id="top" align="center">

```
 ███████╗ ██████╗ █████╗ ███╗   ██╗    ██████╗ ██╗███╗   ███╗██████╗ ██╗███╗   ██╗ ██████╗
 ██╔════╝██╔════╝██╔══██╗████╗  ██║    ██╔══██╗██║████╗ ████║██╔══██╗██║████╗  ██║██╔════╝
 ███████╗██║     ███████║██╔██╗ ██║    ██████╔╝██║██╔████╔██║██████╔╝██║██╔██╗ ██║██║  ███╗
 ╚════██║██║     ██╔══██║██║╚██╗██║    ██╔═══╝ ██║██║╚██╔╝██║██╔═══╝ ██║██║╚██╗██║██║   ██║
 ███████║╚██████╗██║  ██║██║ ╚████║    ██║     ██║██║ ╚═╝ ██║██║     ██║██║ ╚████║╚██████╔╝
 ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝
```

# SCAN-PIMPING

</div>

---

## Overview

SCAN-PIMPING is the ultimate tool to transform your scanned documents and images into professional masterpieces. This innovative application uses advanced computer vision techniques to automatically enhance both PDF documents and image files through intelligent image processing.

**Why SCAN-PIMPING? Because your scanned documents and images deserve to look AMAZING.**

This project takes the pain out of dealing with crooked, low-contrast scanned documents and images. The core features include:

- **Lightning-Fast Processing:** In-memory processing for blazing-fast document transformation
- **Smart Page Detection:** Automatically detects and straightens crooked pages
- **Professional Enhancement:** Boosts contrast, cleans backgrounds, and makes documents print-ready
- **REST API Interface:** Powerful FastAPI-based HTTP endpoints for easy integration
- **Seamless Integration:** Built with FastAPI for easy integration into your workflows
- **Docker Ready:** Containerized deployment for consistent results anywhere
- **High-Quality Output:** Crystal-clear, professional PDFs that impress every time

---

## Getting Started

### Usage (Docker Compose):

```sh
# Start the service
docker-compose up -d

# Stop the service
docker-compose down
```

**The API will be available at http://localhost:8000**

API Endpoints:
- `POST /pimp` - **Universal Endpoint** - Upload ANY file (PDF/Image) and get it pimped automatically
- `POST /pimp-pdf` - Upload a PDF file and get the pimped version back
- `POST /pimp-image` - Upload an image file and get the pimped version back
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with ASCII art and service info

#### Universal Endpoint (Recommended)

The `/pimp` endpoint automatically detects your file type and processes it accordingly!

**Using curl:**

```sh
# Works with PDFs
curl -X POST "http://localhost:8000/pimp" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf" \
     -F "dpi=200" \
     --output document_pimped.pdf

# Works with Images
curl -X POST "http://localhost:8000/pimp" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@image.jpg" \
     -F "area_threshold=0.4" \
     -F "upscale_factor=2" \
     -F "quality=95" \
     --output image_pimped.jpg
```

**Using Python requests:**

```python
import requests

# Works with any supported file type!
def pimp_file(file_path, **params):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8000/pimp', files=files, data=params)
        
        if response.status_code == 200:
            # Generate output filename
            base_name, ext = file_path.rsplit('.', 1)
            output_path = f"{base_name}_pimped.{ext}"
            
            with open(output_path, 'wb') as output:
                output.write(response.content)
            print(f"File pimped successfully: {output_path}")
            return output_path

# Pimp a PDF
pimp_file('document.pdf', dpi=200)

# Pimp an image
pimp_file('scan.jpg', area_threshold=0.4, upscale_factor=2, quality=95)
```

#### Individual Endpoints

**PDF Enhancement - Using curl:**

```sh
curl -X POST "http://localhost:8000/pimp-pdf" \
     -H "accept: application/pdf" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf;type=application/pdf" \
     -F "dpi=200" \
     --output your_document_pimped.pdf
```

**Using Python requests:**

```python
import requests

with open('your_document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    data = {'dpi': 200}
    response = requests.post('http://localhost:8000/pimp-pdf', files=files, data=data)
    
    if response.status_code == 200:
        with open('document_pimped.pdf', 'wb') as output:
            output.write(response.content)
        print("PDF pimped successfully!")
```

**Output Filename Format:**
The API automatically generates output filenames by appending `_pimped` before the file extension:
- `document.pdf` → `document_pimped.pdf`
- `scan_001.pdf` → `scan_001_pimped.pdf`
- `report.pdf` → `report_pimped.pdf`

### Image Enhancement API

**Using curl:**

```sh
curl -X POST "http://localhost:8000/pimp-image" \
     -H "accept: image/jpeg" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg;type=image/jpeg" \
     -F "area_threshold=0.4" \
     -F "upscale_factor=2" \
     -F "quality=95" \
     --output your_image_pimped.jpg
```

**Using Python requests:**

```python
import requests

with open('your_image.jpg', 'rb') as f:
    files = {'file': ('image.jpg', f, 'image/jpeg')}
    data = {
        'area_threshold': 0.4,  # Document must be 40% of image area
        'upscale_factor': 2,    # 2x upscaling
        'quality': 95           # JPEG quality (1-100)
    }
    response = requests.post('http://localhost:8000/pimp-image', files=files, data=data)
    
    if response.status_code == 200:
        with open('image_pimped.jpg', 'wb') as output:
            output.write(response.content)
        print("Image pimped successfully!")
```

**Supported Image Formats:**
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- BMP (`.bmp`)
- TIFF (`.tiff`, `.tif`)

**Parameters:**
- `area_threshold` (0.1-1.0): Minimum document size as fraction of total image (default: 0.4)
- `upscale_factor` (1-5): Image scaling factor for better quality (default: 2)
- `quality` (1-100): JPEG output quality, only affects JPEG files (default: 95)

---

## Standalone Image Processing

You can also use the image enhancer as a standalone Python script:

### Command Line Usage

```sh
# Basic usage - adds "_pimped" suffix to filename
python image_enhancer.py input.jpg

# Specify output filename
python image_enhancer.py input.png -o output.png

# Custom parameters
python image_enhancer.py scan.jpg --area-threshold 0.3 --upscale 3 --quality 90
```

### Programmatic Usage

```python
from image_enhancer import enhance_image_from_path

# Basic enhancement
output_path = enhance_image_from_path('input.jpg')

# Custom parameters
output_path = enhance_image_from_path(
    'input.jpg',
    'output.jpg',
    area_threshold=0.4,  # 40% minimum document area
    upscale_factor=2,    # 2x upscaling
    quality=95           # 95% JPEG quality
)
```

**Output Filename Format:**
Both API and standalone script automatically generate output filenames by appending `_pimped` before the file extension:
- `document.jpg` → `document_pimped.jpg`
- `scan_001.png` → `scan_001_pimped.png`
- `photo.jpeg` → `photo_pimped.jpeg`

---

## Output Filename Format

All endpoints (universal `/pimp`, `/pimp-pdf`, `/pimp-image`) and the standalone script automatically generate output filenames by appending `_pimped` before the file extension:

**PDFs:**
- `document.pdf` → `document_pimped.pdf`
- `scan_001.pdf` → `scan_001_pimped.pdf`
- `report.pdf` → `report_pimped.pdf`

**Images:**
- `document.jpg` → `document_pimped.jpg`
- `scan_001.png` → `scan_001_pimped.png`
- `photo.jpeg` → `photo_pimped.jpeg`

---

## Supported File Formats

**PDFs:** `.pdf`

**Images:** `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`

The universal `/pimp` endpoint automatically detects the file type and applies the appropriate enhancement pipeline!
