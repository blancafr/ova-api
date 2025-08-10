import cv2
import numpy as np
from app.processing.utils import enhance_image_quality, crop_borders, ensure_horizontal_orientation, order_corners

def detect_table(image, min_area_ratio=0.1):
    """Detects a table in the given image and returns a cropped version of the table."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    block_size = 25 if image.shape[0] < 1000 else 11
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, block_size, 2)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    min_area = image.shape[0] * image.shape[1] * min_area_ratio
    contours = [c for c in contours if cv2.contourArea(c) >= min_area]
    
    if not contours:
        return None
    
    largest = max(contours, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, epsilon, True)

    if len(approx) != 4:
        return None
    
    corners = order_corners(approx.reshape(4, 2))
    (tl, tr, br, bl) = corners

    margin = 0

    width = max(int(np.linalg.norm(tr - tl)), int(np.linalg.norm(br - bl))) + 2 * margin
    height = max(int(np.linalg.norm(bl - tl)), int(np.linalg.norm(br - tr))) + 2 * margin

    dst = np.array([
    [margin, margin],
    [width - margin - 1, margin],
    [width - margin - 1, height - margin - 1],
    [margin, height - margin - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(image, M, (width, height))



def process_table_with_blurry_fallback(image_path):
    """Process the table in an image with a fallback for blurry images."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not find processing image: {image_path}")
    enhanced = enhance_image_quality(img)

    first_pass = detect_table(enhanced, min_area_ratio=0.1)
    
    if first_pass is None:
        cropped = crop_borders(enhanced, crop_percent=0.1)
        enhanced = enhance_image_quality(cropped)
        
        second_pass = detect_table(enhanced)
        
        if second_pass is not None:
            final_table = second_pass
        else:
            print("There was no table detected in the image, returning False.")
            return False
    else:
        second_pass = detect_table(first_pass, min_area_ratio=0.6)
        final_table = second_pass if second_pass is not None else first_pass
    
    final_table = ensure_horizontal_orientation(final_table)
    return final_table