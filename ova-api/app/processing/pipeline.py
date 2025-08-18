from .table_detection import process_table_with_blurry_fallback
from .structure_detection import detect_table_structure
from .association import group_data_by_row
from .postprocessing import filter_isolated_rows, compare_and_filter_repeated_rows
from app.schemas.registry import RegistryCreate

def process_image_file(path, previous_rows=None) -> list[RegistryCreate]:
    img = process_table_with_blurry_fallback(path)
    if img is False:
        return []

    cells, _ = detect_table_structure(img, image_path=path)
    if cells is None:
        return list[RegistryCreate]()
    
    raw_rows = group_data_by_row(cells, path)
    rows_ok = filter_isolated_rows(raw_rows, path)
    unique_rows = compare_and_filter_repeated_rows(rows_ok, previous_rows or [])
    return unique_rows
