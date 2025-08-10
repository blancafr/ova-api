from app.schemas.registry import RegistryCreate

def filter_isolated_rows(detected_rows, min_consecutive=2, min_variables=2) -> list[RegistryCreate]:
    """
    Removes:
    - Isolated rows or blocks that are too small (less than `min_consecutive`)
    - Rows that contain fewer than `min_variables` marked variables (sex, age, or diseases)
    """
    if not detected_rows:
        return []

    sorted_rows = sorted(detected_rows, key=lambda r: r["row_num"])
    row_numbers = [row["row_num"] for row in sorted_rows]

    valid_blocks = []
    current_block = [row_numbers[0]]

    for i in range(1, len(row_numbers)):
        if row_numbers[i] == row_numbers[i-1] + 1:
            current_block.append(row_numbers[i])
        else:
            if len(current_block) >= min_consecutive:
                valid_blocks.extend(current_block)
            current_block = [row_numbers[i]]

    if len(current_block) >= min_consecutive:
        valid_blocks.extend(current_block)

    # Filter by valid blocks and minimum number of variables
    filtered_rows = []
    for row in sorted_rows:
        if row["row_num"] in valid_blocks:
            total_variables = len(row["sex"]) + len(row["age"]) + len(row["diseases"])
            if total_variables >= min_variables:
                filtered_rows.append(RegistryCreate(
                    row_num=row["row_num"],
                    date=row["date"],
                    id=row["id"],
                    sex=row["sex"][0] if row["sex"] else "",
                    age=row["age"][0] if row["age"] else "",
                    diseases=row["diseases"]))

    return filtered_rows

def compare_and_filter_repeated_rows(
    new_rows: list[RegistryCreate], 
    previous_rows: list[RegistryCreate], 
    match_threshold=0.70
):
    """
    Detects if the new rows already include records from the previous day.
    If so, returns only the new rows starting from the last previous row.
    """
    if not previous_rows:
        return new_rows

    max_prev_row = max(r.row_num for r in previous_rows)

    possible_matches = [r for r in new_rows if r.row_num <= max_prev_row]

    matches = 0
    for new in possible_matches:
        for prev in previous_rows:
            if new.row_num == prev.row_num:
                sex_match = (new.sex == prev.sex)
                age_match = (new.age == prev.age)
                diseases_match = (set(new.diseases) == set(prev.diseases))

                if sex_match and age_match and diseases_match:
                    matches += 1
                break

    total_prev = len([r for r in previous_rows if r.row_num <= max_prev_row])
    if total_prev == 0:
        return new_rows

    ratio = matches / total_prev

    if ratio >= match_threshold:
        filtered_new_rows = [r for r in new_rows if r.row_num > max_prev_row]
        return filtered_new_rows
    else:
        return new_rows