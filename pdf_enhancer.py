# 🔥 SCAN-PIMPING: PDF Enhancement Engine 🔥
# This module contains all the core image processing functions to transform
# scanned PDF documents into professional-quality, print-ready files.

# Import required libraries
import fitz  # PyMuPDF - for PDF manipulation and rendering
import cv2   # OpenCV - for computer vision and image processing
import numpy as np  # NumPy - for numerical operations on image arrays
from PIL import Image  # Pillow - for image format conversion and saving
import os             # OS operations for file handling

# =============================================================================
# PDF TO IMAGES CONVERSION
# =============================================================================

def pdf_to_images_in_memory(pdf_path, dpi=200):
    """
    🔥 CONVERTS PDF PAGES TO IMAGE ARRAYS IN MEMORY
    
    This function takes a PDF file and converts each page into a numpy array
    representing the image data. This is the first step in our pimping process!
    
    Args:
        pdf_path (str): Full path to the input PDF file
        dpi (int): Dots per inch - higher values = better quality but larger files
                  Typical values: 72 (screen), 150 (draft), 200 (good), 300+ (high quality)
    
    Returns:
        list: List of numpy arrays, each representing a page as an image
              Format: [height, width, channels] where channels = 3 (BGR color)
    
    Raises:
        gr.Error: If PDF cannot be read or processed
    """
    try:
        # Open the PDF document using PyMuPDF
        doc = fitz.open(pdf_path)
        images = []
        
        # Process each page in the PDF
        for i in range(len(doc)):
            # Load the current page
            page = doc.load_page(i)
            
            # Render the page to a pixmap (bitmap) at specified DPI
            # Higher DPI = better quality but more memory usage
            pix = page.get_pixmap(dpi=dpi)
            
            # Convert pixmap to numpy array for OpenCV processing
            # pix.samples contains raw pixel data as bytes
            # We reshape it to [height, width, channels] format
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            
            # Handle color space conversion if needed
            if pix.n == 4:  # RGBA format (Red, Green, Blue, Alpha)
                # Convert BGRA to BGR (remove alpha channel)
                # OpenCV uses BGR color order, not RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Add the processed page image to our list
            images.append(img)
        
        # Close the PDF document to free memory
        doc.close()
        return images
        
    except Exception as e:
        # If anything goes wrong, raise a standard exception
        raise Exception(f"Failed to read PDF. Error: {e}")


# =============================================================================
# GEOMETRIC HELPER FUNCTIONS
# These functions handle the mathematical operations needed for document
# detection and perspective correction (straightening crooked pages)
# =============================================================================

def distance(p1, p2):
    """
    🔥 CALCULATES DISTANCE BETWEEN TWO POINTS
    
    This is a simple Euclidean distance calculation used to measure
    the length of document edges for perspective correction.
    
    Args:
        p1 (numpy.array): First point [x, y]
        p2 (numpy.array): Second point [x, y]
    
    Returns:
        float: Distance between the two points in pixels
    
    Example:
        distance([0, 0], [3, 4]) returns 5.0 (classic 3-4-5 triangle)
    """
    return np.linalg.norm(p1 - p2)

def order_rect(pts):
    """
    🔥 ORDERS FOUR CORNER POINTS IN CONSISTENT SEQUENCE
    
    When we detect a document's corners, they can be in any order.
    This function sorts them into a consistent order: top-left, top-right,
    bottom-right, bottom-left. This is crucial for perspective correction!
    
    Args:
        pts (numpy.array): Array of 4 points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    
    Returns:
        numpy.array: Ordered points [top-left, top-right, bottom-right, bottom-left]
    
    Algorithm:
        - Top-left: smallest sum of x+y coordinates
        - Bottom-right: largest sum of x+y coordinates
        - Top-right: smallest difference of x-y coordinates
        - Bottom-left: largest difference of x-y coordinates
    """
    # Initialize array to hold ordered rectangle points
    rect = np.zeros((4, 2), dtype="float32")
    
    # Calculate sum and difference for each point
    s = pts.sum(axis=1)      # x + y for each point
    diff = np.diff(pts, axis=1)  # x - y for each point

    # Find corners based on mathematical properties:
    rect[0] = pts[np.argmin(s)]    # Top-left: smallest x+y
    rect[2] = pts[np.argmax(s)]    # Bottom-right: largest x+y
    rect[1] = pts[np.argmin(diff)] # Top-right: smallest x-y
    rect[3] = pts[np.argmax(diff)] # Bottom-left: largest x-y
    
    return rect

def four_point_transform(image, pts):
    """
    🔥 APPLIES PERSPECTIVE CORRECTION TO STRAIGHTEN DOCUMENT
    
    This is the magic function that takes a crooked, skewed document
    and transforms it into a perfectly rectangular, straight document!
    It's like having a scanner that can fix perspective distortion.
    
    Args:
        image (numpy.array): Input image containing the document
        pts (numpy.array): Four corner points of the document
    
    Returns:
        numpy.array: Straightened, rectangular document image
    
    Process:
        1. Order the corner points consistently
        2. Calculate the ideal output dimensions
        3. Create a perspective transformation matrix
        4. Apply the transformation to straighten the document
    """
    # Get the corners in the right order
    rect = order_rect(pts)
    (tl, tr, br, bl) = rect  # top-left, top-right, bottom-right, bottom-left

    # Calculate the width of the straightened document
    # We measure both the top and bottom edges and take the maximum
    # This ensures we don't lose any content due to perspective distortion
    widthA = distance(br, bl)  # Bottom edge length
    widthB = distance(tr, tl)  # Top edge length
    maxWidth = int(max(widthA, widthB))

    # Calculate the height of the straightened document
    # We measure both the left and right edges and take the maximum
    heightA = distance(tr, br)  # Right edge length
    heightB = distance(tl, bl)  # Left edge length
    maxHeight = int(max(heightA, heightB))

    # Define where we want the corners to end up in the straightened image
    # This creates a perfect rectangle with corners at:
    # (0,0), (width,0), (width,height), (0,height)
    dst = np.array([
        [0, 0],                           # Top-left destination
        [maxWidth - 1, 0],               # Top-right destination
        [maxWidth - 1, maxHeight - 1],   # Bottom-right destination
        [0, maxHeight - 1]               # Bottom-left destination
    ], dtype="float32")

    # Calculate the perspective transformation matrix
    # This matrix defines how to map the crooked corners to straight corners
    M = cv2.getPerspectiveTransform(rect, dst)
    
    # Apply the transformation to straighten the document
    # This is where the magic happens - crooked becomes straight!
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped

# =============================================================================
# CORE IMAGE PROCESSING ENGINE
# This is the heart of our pimping process! 🔥
# =============================================================================

def process_image_cv(image, area_threshold_ratio=0.4, upscale_factor=2):
    """
    🔥 THE MAIN PIMPING FUNCTION - TRANSFORMS SCANNED IMAGES INTO MASTERPIECES!
    
    This function performs the complete document enhancement pipeline:
    1. Detects the document boundaries in the image
    2. Straightens the document using perspective correction
    3. Enhances the image quality and contrast
    4. Creates a clean, professional black-and-white output
    
    Args:
        image (numpy.array): Input image as BGR color array [height, width, 3]
        area_threshold_ratio (float): Minimum document size as fraction of total image
                                    (0.4 = document must be at least 40% of image area)
        upscale_factor (int): How much to enlarge the final image (2 = double size)
                             Higher values = better quality but larger files
    
    Returns:
        numpy.array: Enhanced black-and-white document image ready for PDF conversion
    
    Process Overview:
        INPUT: Crooked, low-contrast scanned page
        ↓
        STEP 1: Blur and edge detection to find document outline
        ↓
        STEP 2: Find the largest rectangular contour (the document)
        ↓
        STEP 3: Straighten the document using perspective correction
        ↓
        STEP 4: Upscale for better quality
        ↓
        STEP 5: Convert to high-contrast black and white
        ↓
        OUTPUT: Professional, print-ready document! 🔥
    """
    
    # Get image dimensions for calculations
    img_height, img_width = image.shape[:2]
    img_area = img_height * img_width  # Total pixel area
    
    # =================================================================
    # STEP 1: PRE-PROCESSING FOR EDGE DETECTION
    # =================================================================
    
    # Apply Gaussian blur to reduce noise and smooth the image
    # This helps edge detection work better by removing small details
    # Kernel size (5,5) is a good balance - not too blurry, removes enough noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Detect edges using Canny edge detector
    # Low threshold: 10 (weak edges), High threshold: 50 (strong edges)
    # This finds the outlines of objects, including our document borders
    edges = cv2.Canny(blurred, 10, 50)
    
    # =================================================================
    # STEP 2: FIND THE DOCUMENT CONTOUR
    # =================================================================
    
    # Find all contours (connected edge pixels) in the edge image
    # RETR_EXTERNAL: only get outer contours (ignore holes inside shapes)
    # CHAIN_APPROX_SIMPLE: compress contours by removing redundant points
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area (largest first)
    # The document should be the largest rectangular object in the image
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Look for the document contour (should be rectangular with 4 corners)
    screenCnt = None
    for c in contours:
        # Calculate the perimeter of this contour
        peri = cv2.arcLength(c, True)
        
        # Approximate the contour to a simpler polygon
        # 0.02 * peri means we allow 2% deviation from the true contour
        # This helps convert slightly curved edges to straight lines
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        # Check if this looks like a document:
        # 1. Must have exactly 4 corners (rectangular)
        # 2. Must be large enough (at least 40% of image area by default)
        if len(approx) == 4 and cv2.contourArea(approx) > area_threshold_ratio * img_area:
            # Found our document! Convert to simple 4-point format
            screenCnt = approx.reshape(4, 2)
            break  # Stop looking, we found it!
    
    # =================================================================
    # STEP 3: STRAIGHTEN THE DOCUMENT
    # =================================================================
    
    if screenCnt is not None:
        # We found a document contour - straighten it!
        # This transforms the crooked quadrilateral into a perfect rectangle
        warped = four_point_transform(image, screenCnt)
    else:
        # No clear document boundary found - use the whole image
        # This happens with full-page scans or very clean documents
        warped = image
    
    # =================================================================
    # STEP 4: ENHANCE IMAGE QUALITY
    # =================================================================
    
    # Upscale the image for better quality
    # fx, fy = scaling factors for width and height
    # INTER_CUBIC = high-quality interpolation (smooth scaling)
    upscaled = cv2.resize(warped, (0, 0), fx=upscale_factor, fy=upscale_factor,
                         interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale for black-and-white processing
    # This removes color information, focusing on text and content
    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
    
    # =================================================================
    # STEP 5: CREATE HIGH-CONTRAST BLACK AND WHITE OUTPUT
    # =================================================================
    
    # Apply adaptive thresholding for professional black-and-white look
    # This automatically adjusts the threshold for different parts of the image
    # Perfect for handling uneven lighting or shadows!
    binary = cv2.adaptiveThreshold(
        gray,                           # Input grayscale image
        255,                           # Maximum value (pure white)
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, # Use Gaussian-weighted neighborhood
        cv2.THRESH_BINARY,             # Binary output (black or white only)
        blockSize=91,                  # Size of neighborhood area (must be odd)
                                      # Larger = smoother, smaller = more detail
        C=30                          # Constant subtracted from mean
                                      # Higher = more white, lower = more black
    )
    
    # Return the pimped image - ready to impress! 🔥
    return binary

# =============================================================================
# PDF CREATION AND OUTPUT
# =============================================================================

def images_to_pdf_from_arrays(images, output_pdf_path):
    """
    🔥 CONVERTS PROCESSED IMAGES BACK INTO A SINGLE PDF FILE
    
    This function takes our list of pimped images and combines them
    into a single, professional PDF document ready for printing or sharing.
    
    Args:
        images (list): List of numpy arrays representing processed document pages
                      Each array should be a grayscale or RGB image
        output_pdf_path (str): Full path where the final PDF should be saved
    
    Raises:
        gr.Error: If no images are provided (nothing to save)
    
    Process:
        1. Convert numpy arrays to PIL Image objects
        2. Ensure all images are in RGB format (required for PDF)
        3. Use the first image as the base and append the rest
        4. Save as a multi-page PDF file
    """
    # Safety check - make sure we have images to work with
    if not images:
        raise Exception("No images were processed to save.")
    
    # Convert all numpy arrays to PIL Images and ensure RGB format
    # PIL (Python Imaging Library) is needed for PDF creation
    # convert('RGB') ensures consistent color format even for grayscale images
    pil_images = [Image.fromarray(img).convert('RGB') for img in images]
    
    # Create the multi-page PDF
    # The first image becomes the base, and we append all others to it
    # save_all=True enables multi-page PDF creation
    # append_images contains all pages after the first one
    pil_images[0].save(output_pdf_path, save_all=True, append_images=pil_images[1:])

# =============================================================================
# MAIN PROCESSING FUNCTION FOR FASTAPI
# =============================================================================

def enhance_pdf_from_path(pdf_path, output_path, dpi=200):
    """
    🔥 MAIN ORCHESTRATION FUNCTION FOR FASTAPI
    
    This is the main function that coordinates the entire PDF pimping process
    when called from the FastAPI interface. It handles the complete workflow
    from input PDF file to enhanced output.
    
    Args:
        pdf_path (str): Path to the input PDF file
        output_path (str): Path where the enhanced PDF should be saved
        dpi (int): Scan quality setting (default: 200)
    
    Returns:
        str: Path to the enhanced PDF file
    
    Workflow:
        1. Convert PDF pages to images
        2. Process each image (detect, straighten, enhance)
        3. Combine processed images back into a PDF
        4. Return the output path
    """
    # STEP 1: Convert PDF to individual page images
    # This breaks down the PDF into separate images we can process
    images = pdf_to_images_in_memory(pdf_path, dpi)

    # STEP 2: Process each page image through our pimping pipeline
    # Each image gets: document detection → straightening → enhancement
    processed_images = [process_image_cv(img) for img in images]

    # STEP 3: Combine all processed images back into a single PDF
    images_to_pdf_from_arrays(processed_images, output_path)
    
    # Return the output path
    return output_path