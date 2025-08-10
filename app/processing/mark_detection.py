import cv2

def detect_X_in_cell(cell_image):
    """Detects if there is a large enough "X" in the given cell image."""
    gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=4.5, tileGridSize=(2, 2))
    enhanced_gray = clahe.apply(gray)

    _, binary = cv2.threshold(enhanced_gray, 60, 255, cv2.THRESH_BINARY)

    border_size = 8
    cropped_binary = binary[border_size:-border_size, border_size:-border_size]

    # Count the number of black pixels in the cropped binary image
    black_pixels = cv2.countNonZero(255 - cropped_binary)

    if black_pixels > 0 :
        return True
    
    return False