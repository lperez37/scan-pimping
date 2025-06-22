<div id="top" align="center">

```
 ███████╗ ██████╗ █████╗ ███╗   ██╗    ██████╗ ██╗███╗   ███╗██████╗ ██╗███╗   ██╗ ██████╗
 ██╔════╝██╔════╝██╔══██╗████╗  ██║    ██╔══██╗██║████╗ ████║██╔══██╗██║████╗  ██║██╔════╝
 ███████╗██║     ███████║██╔██╗ ██║    ██████╔╝██║██╔████╔██║██████╔╝██║██╔██╗ ██║██║  ███╗
 ╚════██║██║     ██╔══██║██║╚██╗██║    ██╔═══╝ ██║██║╚██╔╝██║██╔═══╝ ██║██║╚██╗██║██║   ██║
 ███████║╚██████╗██║  ██║██║ ╚████║    ██║     ██║██║ ╚═╝ ██║██║     ██║██║ ╚████║╚██████╔╝
 ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝
```

# 🔥 SCAN-PIMPING 🔥


</div>

---

## Overview

🔥 **SCAN-PIMPING** is the ultimate tool to transform your scanned documents into professional masterpieces! This innovative application uses advanced computer vision techniques to automatically enhance PDF document quality through intelligent image processing.

**Why SCAN-PIMPING? Because your scanned documents deserve to look AMAZING! 🚀**

This project takes the pain out of dealing with crooked, low-contrast scanned documents. The core features include:

-   🔥 **Lightning-Fast Processing:** In-memory processing for blazing-fast document transformation
-   🎯 **Smart Page Detection:** Automatically detects and straightens crooked pages
-   ✨ **Professional Enhancement:** Boosts contrast, cleans backgrounds, and makes documents print-ready
-   🌐 **REST API Interface:** Powerful FastAPI-based HTTP endpoints for easy integration
-   📄 **Seamless Integration:** Built with FastAPI for easy integration into your workflows
-   🐳 **Docker Ready:** Containerized deployment for consistent results anywhere
-   💡 **High-Quality Output:** Crystal-clear, professional PDFs that impress every time

---

## Getting Started

### Usage (Docker Compose):**

```sh
# Start the service
docker-compose up -d

# Stop the service
docker-compose down
```

**The API will be available at http://localhost:8000**

🔥 API Endpoints:
- `POST /pimp-pdf` - Upload a PDF file and get the pimped version back! 🚀
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with ASCII art and service info

#### Testing the API

**Using curl:**

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
        print("🔥 PDF pimped successfully!")
```

**Output Filename Format:**
The API automatically generates output filenames by appending `_pimped` before the file extension:
- `document.pdf` → `document_pimped.pdf`
- `scan_001.pdf` → `scan_001_pimped.pdf`
- `report.pdf` → `report_pimped.pdf`
