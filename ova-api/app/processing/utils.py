import cv2
import numpy as np

def enhance_image_quality(image):
    """ Improve the quality of the image by applying a series of transformations. """
    blurred = cv2.GaussianBlur(image, (0, 0), 3)
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
    
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    lab_enhanced = cv2.merge((l_enhanced, a, b))
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    return denoised

def crop_borders(image, crop_percent=0.1):
    """Crop the borders of the image by a specified percentage."""
    h, w = image.shape[:2]
    border = int(min(h, w) * crop_percent)
    return image[border:h-border, border:w-border]

def ensure_horizontal_orientation(image):
    """Ensure the image is oriented horizontally with header on the top by checking its dimensions and applying transformations if necessary."""
    h, w = image.shape[:2]
    if h > w:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        h, w = w, h
    
    # Detect if the image is upside down with techniques like contrast, edge density, and column structure
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    top_contrast = np.mean(thresh[:h//10, :])
    bottom_contrast = np.mean(thresh[-h//10:, :])

    edges = cv2.Canny(gray, 50, 150)
    top_edges = np.sum(edges[:h//10, :]) / (w * h//10)
    bottom_edges = np.sum(edges[-h//10:, :]) / (w * h//10)
    

    def count_vertical_lines(region):
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        vertical_edges = cv2.morphologyEx(region, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        contours, _ = cv2.findContours(vertical_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len(contours)
    
    top_lines = count_vertical_lines(thresh[:h//15, :])
    bottom_lines = count_vertical_lines(thresh[-h//15:, :])
    
    score = 0
    score += 1 if top_contrast > bottom_contrast else -1
    score += 1 if top_edges < bottom_edges else -1
    score += 3 if top_lines > bottom_lines else 0
    
    if score > 0:
        image = cv2.rotate(image, cv2.ROTATE_180)
    return image

def order_corners(pts):
    """Order the corners of a quadrilateral in a consistent manner: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)] 
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect
