
import pandas as pd
from src.validation import (
    validate_employee_data,
    validate_employee_history,
)


def test_valid_employee_data():
    df = pd.DataFrame({
        "employee_id": [101, 102],
        "salary": [30000.0, 40000.0],
        "joining_date": pd.to_datetime([
            "2023-01-10",
            "2022-06-15",
        ]),
    })

    result = validate_employee_data(df)

    assert len(result) == 2
    assert result["employee_id"].is_unique
    assert (result["salary"] >= 0).all()

    print("Employee validation test passed!")


def test_negative_salary_is_rejected():
    import pandera.errors

    df = pd.DataFrame({
        "employee_id": [103],
        "salary": [-5000.0],
        "joining_date": pd.to_datetime(["2024-03-01"]),
    })

    try:
        validate_employee_data(df)
    except pandera.errors.SchemaErrors:
        print("Negative salary correctly rejected!")
    else:
        raise AssertionError("Negative salary was not rejected!")


def test_duplicate_employee_ids_are_rejected():
    import pandera.errors

    df = pd.DataFrame({
        "employee_id": [101, 101],
        "salary": [30000.0, 35000.0],
        "joining_date": pd.to_datetime([
            "2023-01-10",
            "2024-03-01",
        ]),
    })

    try:
        validate_employee_data(df)
    except pandera.errors.SchemaErrors:
        print("Duplicate employee IDs correctly rejected!")
    else:
        raise AssertionError("Duplicate employee IDs were not rejected!")


if __name__ == "__main__":
    test_valid_employee_data()
    test_negative_salary_is_rejected()
    test_duplicate_employee_ids_are_rejected()

def test_valid_employee_history_passes():
    df = pd.DataFrame({
        "employee_id": ["E101", "E101"],
        "valid_from": ["2023-01-01", "2024-01-01"],
        "valid_to": ["2023-12-31", None],
    })

    result = validate_employee_history(df)

    assert len(result) == 2


def test_overlapping_employee_history_is_rejected():
    df = pd.DataFrame({
        "employee_id": ["E101", "E101"],
        "valid_from": ["2023-01-01", "2023-06-01"],
        "valid_to": ["2023-12-31", None],
    })

    try:
        validate_employee_history(df)
    except ValueError as exc:
        assert "Overlapping employee history" in str(exc)
    else:
        raise AssertionError("Overlapping employee history was not rejected!")
