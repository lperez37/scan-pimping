from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import Response
import tempfile
import os
from pdf_enhancer import enhance_pdf_from_path
from image_enhancer import enhance_image_from_path
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
            "enhance": "POST /pimp - Upload any file (PDF/Image) and get enhanced version! 🔥",
            "enhance_pdf": "POST /pimp-pdf - Upload and enhance your PDF",
            "enhance_image": "POST /pimp-image - Upload and enhance your image",
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

@app.post("/pimp-image")
async def pimp_image_endpoint(
    file: UploadFile = File(..., description="Image file to pimp up! 🔥"),
    area_threshold: float = Form(0.4, description="Document area threshold (0.1-1.0)", ge=0.1, le=1.0),
    upscale_factor: int = Form(2, description="Image upscaling factor (1-5x)", ge=1, le=5),
    quality: int = Form(95, description="Output quality for JPEG (1-100)", ge=1, le=100)
):
    """
    🔥 PIMP YOUR IMAGE! 🔥
    
    Transform your scanned image into a professional masterpiece by:
    - Straightening crooked pages/documents
    - Enhancing contrast and clarity
    - Cleaning up backgrounds
    - Making it print-ready
    
    Supports common formats: PNG, JPG, JPEG, BMP, TIFF, etc.
    
    Args:
        file: Image file to pimp up (PNG, JPG, JPEG, BMP, TIFF, etc.)
        area_threshold: Minimum document size as fraction of image (0.4 = 40%)
        upscale_factor: Image scaling factor (2 = double size)
        quality: JPEG output quality (1-100, only affects JPEG output)
    
    Returns:
        Pimped image as binary response in the same format as input! ✨
    """
    
    # Get file extension to determine format
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_ext = file.filename.lower().split('.')[-1]
    supported_formats = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif']
    
    if file_ext not in supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"
        )
    
    try:
        # Create temporary files for input and output
        input_suffix = f'.{file_ext}'
        output_suffix = f'.{file_ext}'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=input_suffix) as temp_input:
            # Save uploaded file
            content = await file.read()
            temp_input.write(content)
            temp_input.flush()
            
            logger.info(f"🔥 PIMPING IMAGE: {file.filename} with threshold: {area_threshold}, upscale: {upscale_factor}x")
            
            # Create output temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=output_suffix) as temp_output:
                # Process the image using our enhancement function
                enhance_image_from_path(
                    temp_input.name,
                    temp_output.name,
                    area_threshold,
                    upscale_factor,
                    quality
                )
                
                # Read the pimped image
                with open(temp_output.name, 'rb') as pimped_image:
                    image_bytes = pimped_image.read()
                
                # Clean up temporary files
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)
                
                logger.info(f"✨ Successfully pimped image: {file.filename}")
                
                # Generate output filename with "_pimped" before extension
                base_name, ext = os.path.splitext(file.filename)
                pimped_filename = f"{base_name}_pimped{ext}"
                
                # Determine media type based on file extension
                media_type_map = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'bmp': 'image/bmp',
                    'tiff': 'image/tiff',
                    'tif': 'image/tiff'
                }
                media_type = media_type_map.get(file_ext, 'application/octet-stream')
                
                # Return the pimped image as binary response
                return Response(
                    content=image_bytes,
                    media_type=media_type,
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
        
        logger.error(f"Error processing image {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@app.post("/pimp")
async def pimp_file_endpoint(
    file: UploadFile = File(..., description="Any file to pimp up! PDF or Image 🔥"),
    dpi: int = Form(200, description="PDF scan quality (DPI) - only for PDFs", ge=72, le=600),
    area_threshold: float = Form(0.4, description="Image document area threshold - only for images", ge=0.1, le=1.0),
    upscale_factor: int = Form(2, description="Image upscaling factor - only for images", ge=1, le=5),
    quality: int = Form(95, description="Output quality for JPEG images", ge=1, le=100)
):
    """
    🔥 UNIVERSAL PIMP ENDPOINT! 🔥
    
    Upload ANY supported file and get it pimped automatically!
    This endpoint intelligently detects whether you uploaded a PDF or image
    and routes it to the appropriate processing pipeline.
    
    Supported formats:
    📄 PDFs: .pdf
    🖼️ Images: .png, .jpg, .jpeg, .bmp, .tiff, .tif
    
    Args:
        file: Any supported file (PDF or image)
        dpi: PDF scan quality (72-600 DPI) - only used for PDFs
        area_threshold: Image document area threshold (0.1-1.0) - only used for images
        upscale_factor: Image scaling factor (1-5x) - only used for images
        quality: JPEG output quality (1-100) - only used for JPEG images
    
    Returns:
        Enhanced file in the same format as input! ✨
    """
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Get file extension to determine processing type
    file_ext = file.filename.lower().split('.')[-1]
    
    # Define supported formats
    pdf_formats = ['pdf']
    image_formats = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif']
    all_supported = pdf_formats + image_formats
    
    if file_ext not in all_supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Supported formats: PDF ({', '.join(pdf_formats)}), Images ({', '.join(image_formats)})"
        )
    
    logger.info(f"🔥 Universal endpoint: Detected {file_ext} file: {file.filename}")
    
    # Route to appropriate endpoint based on file type
    if file_ext in pdf_formats:
        logger.info(f"📄 Routing to PDF pipeline")
        return await pimp_pdf_endpoint(file, dpi)
    
    elif file_ext in image_formats:
        logger.info(f"🖼️ Routing to image pipeline")
        return await pimp_image_endpoint(file, area_threshold, upscale_factor, quality)

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy", "service": "scan-pimping", "message": "Ready to pimp your PDFs! 🔥"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)