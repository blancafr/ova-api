import os
from .mark_detection import detect_X_in_cell
from .constants import COLUMNS, SEX_GROUP, AGE_GROUP
from datetime import datetime


def group_data_by_row(cells, imge_file_name):
    """
    Returns a list of dictionaries with the detected rows and their corresponding fields.
    """

    filename = os.path.basename(imge_file_name)
    filename_no_ext = os.path.splitext(filename)[0]

    dt = datetime.strptime(filename_no_ext[:8], "%Y%m%d")
    date = dt.strftime("%Y-%m-%d")  

    detected_rows = {}

    for cell in cells:
        if detect_X_in_cell(cell["image"]):
            row = cell["row"]
            column_idx = cell["column"] - 1
            if column_idx >= len(COLUMNS):
                continue
            field = COLUMNS[column_idx]

            if row not in detected_rows:
                detected_rows[row] = {
                    "row_num": row,
                    "date": date,
                    "id": filename_no_ext,
                    "sex": [],
                    "age": [],
                    "diseases": []
                }

            if field in SEX_GROUP:
                detected_rows[row]["sex"].append(field)
            elif field in AGE_GROUP:
                detected_rows[row]["age"].append(field)
            else:
                detected_rows[row]["diseases"].append(field)

    return [detected_rows[k] for k in sorted(detected_rows)]


