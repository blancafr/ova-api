import cv2
import numpy as np
from app.processing.utils import enhance_image_quality
from app.processing.constants import ROW_NUMBERS, COLUMNS
from app.main import logger

def detect_table_structure(image, image_path=None):
        height, width = image.shape[:2]
        crop_height = int(height * 0.22)
        crop_width = int(width * 0.075)
        cropped_image = image[crop_height:height, crop_width:width]

        cropped_image_enhanced = enhance_image_quality(cropped_image)

        gray = cv2.cvtColor(cropped_image_enhanced, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY, 15, -2)

        grid = detect_lines(thresh)
        contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        detected_cells = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 20 and h > 20 and w < image.shape[1] * 0.75 and h < 200:
                detected_cells.append((x, y, w, h))

        # Infer vertical and horizontal lines from the detected cells
        vertical_lines, horizontal_lines = infer_grid_lines(detected_cells)

        # Extract cells ordered by row
        cells, grid_image = extract_cells_ordered_by_row(cropped_image.copy(), vertical_lines, horizontal_lines)

        # Ensure the grid image is in the correct format
        if len(cells) != ROW_NUMBERS*len(COLUMNS):
            logger.error(f"Detected cells count {len(cells)} does not match expected {ROW_NUMBERS*len(COLUMNS)}. For image: {image_path}")
            return None, None
        return cells, grid_image

def detect_lines(thresh):
    """Detect horizontal and vertical lines in the thresholded image."""
    horizontal = thresh.copy()
    horizontal_size = horizontal.shape[1] // 30  
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    vertical = thresh.copy()
    vertical_size = vertical.shape[0] // 45
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    grid = cv2.add(horizontal, vertical)

    return grid

def infer_grid_lines(detected_cells, threshold=10):
    """"Infer vertical and horizontal lines from detected cells."""
    
    detected_cells_sorted_by_x = sorted(detected_cells, key=lambda x: x[0])
    detected_cells_sorted_by_y = sorted(detected_cells, key=lambda x: x[1])
    
    x_positions = [x for x, y, w, h in detected_cells_sorted_by_x]
    y_positions = [y for x, y, w, h in detected_cells_sorted_by_y]

    vertical_lines = group_positions(x_positions, threshold)
    horizontal_lines = group_positions(y_positions, threshold)
    
    # Add the last line to ensure the grid is complete
    last_x, last_y, last_w, last_h = detected_cells_sorted_by_x[-1]
    _, last_y_sorted, _, last_h_sorted = detected_cells_sorted_by_y[-1]
    vertical_lines.append(last_x + last_w)
    horizontal_lines.append(last_y_sorted + last_h_sorted)

    return vertical_lines, horizontal_lines

def group_positions(positions, threshold):
    """Group positions based on a threshold to avoid noise in line detection."""
    grouped_positions = []
    current_group = []

    for i, pos in enumerate(positions):
        if not current_group:
            current_group.append(pos)
        else:
            if pos - current_group[-1] < threshold:
                current_group.append(pos)
            else:
                grouped_positions.append(np.mean(current_group))  
                current_group = [pos]
    
    if current_group:
        grouped_positions.append(np.mean(current_group))
    
    return grouped_positions

def extract_cells_ordered_by_row(image, vertical_lines, horizontal_lines):
    """Extratct cells ordered by row from the image based on vertical and horizontal lines"""
    cells = []

    for row_idx in range(len(horizontal_lines) - 1): 
        for col_idx in range(len(vertical_lines) - 1):
            x1 = int(vertical_lines[col_idx])
            y1 = int(horizontal_lines[row_idx])
            x2 = int(vertical_lines[col_idx + 1])
            y2 = int(horizontal_lines[row_idx + 1])

            cell_img = image[y1:y2, x1:x2]

            cells.append({
                "row": row_idx + 1,
                "column": col_idx + 1,
                "x": x1,
                "y": y1,
                "image": cell_img
            })
    return cells, image