# 🔥 SCAN-PIMPING: Image Enhancement Engine 🔥
# This module contains all the core image processing functions to transform
# scanned images into professional-quality, print-ready files.

# Import required libraries
import cv2   # OpenCV - for computer vision and image processing
import numpy as np  # NumPy - for numerical operations on image arrays
from PIL import Image  # Pillow - for image format conversion and saving
import os             # OS operations for file handling
import argparse       # For command line argument parsing

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
        numpy.array: Enhanced black-and-white document image ready for saving
    
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
# IMAGE FILE HANDLING FUNCTIONS
# =============================================================================

def load_image(image_path):
    """
    🔥 LOADS AN IMAGE FROM FILE PATH
    
    Supports common image formats: PNG, JPG, JPEG, BMP, TIFF, etc.
    
    Args:
        image_path (str): Path to the input image file
    
    Returns:
        numpy.array: Image as BGR color array
    
    Raises:
        Exception: If image cannot be loaded
    """
    try:
        # Load image using OpenCV (automatically handles most formats)
        image = cv2.imread(image_path)
        
        if image is None:
            raise Exception(f"Could not load image from {image_path}")
        
        return image
        
    except Exception as e:
        raise Exception(f"Failed to load image. Error: {e}")

def save_image(image, output_path, quality=95):
    """
    🔥 SAVES AN IMAGE TO FILE WITH ORIGINAL FORMAT PRESERVATION
    
    Automatically detects the desired output format from the file extension
    and saves with appropriate quality settings.
    
    Args:
        image (numpy.array): Image array to save
        output_path (str): Path where the image should be saved
        quality (int): JPEG quality (1-100, only used for JPEG files)
    
    Raises:
        Exception: If image cannot be saved
    """
    try:
        # Get file extension to determine format
        _, ext = os.path.splitext(output_path.lower())
        
        # Set compression parameters based on format
        if ext in ['.jpg', '.jpeg']:
            # JPEG format - set quality
            cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        elif ext == '.png':
            # PNG format - set compression level (0-9, 9 = max compression)
            cv2.imwrite(output_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        else:
            # Other formats - use default settings
            cv2.imwrite(output_path, image)
            
    except Exception as e:
        raise Exception(f"Failed to save image. Error: {e}")

def get_output_filename(input_path, suffix="_pimped"):
    """
    🔥 GENERATES OUTPUT FILENAME WITH SUFFIX
    
    Creates an output filename by adding a suffix before the file extension.
    
    Args:
        input_path (str): Original file path
        suffix (str): Suffix to add (default: "_pimped")
    
    Returns:
        str: New filename with suffix
    
    Example:
        get_output_filename("document.jpg") returns "document_pimped.jpg"
    """
    base_name, ext = os.path.splitext(input_path)
    return f"{base_name}{suffix}{ext}"

# =============================================================================
# MAIN PROCESSING FUNCTION
# =============================================================================

def enhance_image_from_path(input_path, output_path=None, area_threshold=0.4, upscale_factor=2, quality=95):
    """
    🔥 MAIN ORCHESTRATION FUNCTION FOR IMAGE ENHANCEMENT
    
    This is the main function that coordinates the entire image pimping process.
    It handles the complete workflow from input image file to enhanced output.
    
    Args:
        input_path (str): Path to the input image file
        output_path (str): Path where the enhanced image should be saved (optional)
        area_threshold (float): Minimum document size ratio (0.4 = 40% of image)
        upscale_factor (int): Image scaling factor (default: 2x)
        quality (int): JPEG quality for output (1-100, default: 95)
    
    Returns:
        str: Path to the enhanced image file
    
    Workflow:
        1. Load the input image
        2. Process the image (detect, straighten, enhance)
        3. Save the processed image with original format
        4. Return the output path
    """
    # Generate output path if not provided
    if output_path is None:
        output_path = get_output_filename(input_path)
    
    # STEP 1: Load the input image
    print(f"🔥 Loading image: {input_path}")
    image = load_image(input_path)
    
    # STEP 2: Process the image through our pimping pipeline
    print(f"🔥 Processing image with area threshold: {area_threshold}, upscale: {upscale_factor}x")
    processed_image = process_image_cv(image, area_threshold, upscale_factor)
    
    # STEP 3: Save the processed image
    print(f"🔥 Saving enhanced image: {output_path}")
    save_image(processed_image, output_path, quality)
    
    print(f"✨ Successfully pimped image: {input_path} -> {output_path}")
    return output_path

# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def main():
    """
    🔥 COMMAND LINE INTERFACE FOR IMAGE ENHANCEMENT
    
    Allows users to enhance images directly from the command line.
    """
    parser = argparse.ArgumentParser(
        description="🔥 Scan-Pimping Image Enhancer - Transform your scanned images into professional masterpieces!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_enhancer.py input.jpg
  python image_enhancer.py input.png -o output.png
  python image_enhancer.py scan.jpg --area-threshold 0.3 --upscale 3
  python image_enhancer.py document.jpeg --quality 90
        """
    )
    
    parser.add_argument(
        'input',
        help='Input image file path (supports PNG, JPG, JPEG, BMP, TIFF, etc.)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output image file path (default: adds "_pimped" suffix to input filename)'
    )
    
    parser.add_argument(
        '--area-threshold',
        type=float,
        default=0.4,
        help='Minimum document area as fraction of total image (default: 0.4 = 40%%)'
    )
    
    parser.add_argument(
        '--upscale',
        type=int,
        default=2,
        help='Image upscaling factor (default: 2x)'
    )
    
    parser.add_argument(
        '--quality',
        type=int,
        default=95,
        help='JPEG output quality 1-100 (default: 95)'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate input file exists
        if not os.path.exists(args.input):
            print(f"❌ Error: Input file '{args.input}' does not exist!")
            return 1
        
        # Validate parameters
        if not 0.1 <= args.area_threshold <= 1.0:
            print("❌ Error: Area threshold must be between 0.1 and 1.0")
            return 1
        
        if not 1 <= args.upscale <= 5:
            print("❌ Error: Upscale factor must be between 1 and 5")
            return 1
        
        if not 1 <= args.quality <= 100:
            print("❌ Error: Quality must be between 1 and 100")
            return 1
        
        # Process the image
        output_path = enhance_image_from_path(
            args.input,
            args.output,
            args.area_threshold,
            args.upscale,
            args.quality
        )
        
        print(f"🎉 Image enhancement complete! Output saved to: {output_path}")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())