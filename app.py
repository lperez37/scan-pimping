# Ahmed Gali
# Copyright (c) 2025 Ahmed Gali
# Licensed under the MIT License

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import Response
import tempfile
import os
from pdf_enhancer import enhance_pdf_from_path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ASCII_ART = """
 ███████╗ ██████╗ █████╗ ███╗   ██╗    ██████╗ ██╗███╗   ███╗██████╗ ██╗███╗   ██╗ ██████╗
 ██╔════╝██╔════╝██╔══██╗████╗  ██║    ██╔══██╗██║████╗ ████║██╔══██╗██║████╗  ██║██╔════╝
 ███████╗██║     ███████║██╔██╗ ██║    ██████╔╝██║██╔████╔██║██████╔╝██║██╔██╗ ██║██║  ███╗
 ╚════██║██║     ██╔══██║██║╚██╗██║    ██╔═══╝ ██║██║╚██╔╝██║██╔═══╝ ██║██║╚██╗██║██║   ██║
 ███████║╚██████╗██║  ██║██║ ╚████║    ██║     ██║██║ ╚═╝ ██║██║     ██║██║ ╚████║╚██████╔╝
 ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝
                                                                                              
"""

app = FastAPI(
    title="Scan-Pimping API",
    description="🚀 Pimp your scanned PDFs! Straighten pages, enhance contrast, and make documents look professional",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Welcome endpoint with ASCII art"""
    return {
        "message": "Welcome to Scan-Pimping API! 🔥",
        "ascii_art": ASCII_ART,
        "description": "Transform your scanned documents into professional masterpieces!",
        "endpoints": {
            "enhance": "POST /pimp-pdf - Upload and enhance your PDF",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        }
    }

@app.post("/pimp-pdf")
async def pimp_pdf_endpoint(
    file: UploadFile = File(..., description="PDF file to pimp up! 🔥"),
    dpi: int = Form(200, description="Scan quality (DPI) - Higher = Better!", ge=72, le=600)
):
    """
    🔥 PIMP YOUR PDF! 🔥
    
    Transform your scanned PDF into a professional masterpiece by:
    - Straightening crooked pages
    - Enhancing contrast and clarity
    - Cleaning up backgrounds
    - Making it print-ready
    
    Args:
        file: PDF file to pimp up
        dpi: Scan quality (72-600 DPI) - Higher values = better quality
    
    Returns:
        Pimped PDF as binary response, ready to impress! ✨
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
            # Save uploaded file
            content = await file.read()
            temp_input.write(content)
            temp_input.flush()
            
            logger.info(f"🔥 PIMPING PDF: {file.filename} with DPI: {dpi}")
            
            # Create output temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_output:
                # Process the PDF using our simplified function
                enhance_pdf_from_path(temp_input.name, temp_output.name, dpi)
                
                # Read the pimped PDF
                with open(temp_output.name, 'rb') as pimped_pdf:
                    pdf_bytes = pimped_pdf.read()
                
                # Clean up temporary files
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)
                
                logger.info(f"✨ Successfully pimped PDF: {file.filename}")
                
                # Generate output filename with "_pimped" before extension
                base_name, ext = os.path.splitext(file.filename)
                pimped_filename = f"{base_name}_pimped{ext}"
                
                # Return the pimped PDF as binary response
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename={pimped_filename}"
                    }
                )
                
    except Exception as e:
        # Clean up temporary files in case of error
        try:
            if 'temp_input' in locals():
                os.unlink(temp_input.name)
            if 'temp_output' in locals():
                os.unlink(temp_output.name)
        except:
            pass
        
        logger.error(f"Error processing PDF {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy", "service": "scan-pimping", "message": "Ready to pimp your PDFs! 🔥"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)