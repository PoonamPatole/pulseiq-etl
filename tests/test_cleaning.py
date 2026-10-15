
import pandas as pd
from src.cleaning import clean_dataframe
from src.cleaning import add_employee_helper_columns
from src.cleaning import convert_employee_types
from src.cleaning import separate_invalid_employee_types

def test_missing_values_are_separated():
    df = pd.DataFrame({
        "employee_id": [101, 102, 103],
        "name": ["Asha", None, "Neha"],
        "salary": [30000, 40000, None],
    })

    valid_df, rejected_df = clean_dataframe(
        df,
        required_columns=["employee_id", "name", "salary"],
    )

    assert len(valid_df) == 1
    assert len(rejected_df) == 2
    assert valid_df["employee_id"].tolist() == [101]


def test_text_spaces_are_removed():
    df = pd.DataFrame({
        "employee_id": [101],
        "name": ["  Asha  "],
        "salary": [30000],
    })

    valid_df, rejected_df = clean_dataframe(
        df,
        required_columns=["employee_id", "name", "salary"],
    )

    assert valid_df.iloc[0]["name"] == "Asha"
    assert len(rejected_df) == 0


from src.cleaning import add_employee_helper_columns


def test_employee_helper_columns():
    df = pd.DataFrame({
        "employee_id": [101, 102],
        "joining_date": ["2023-01-10", "2024-03-01"],
    })

    result = add_employee_helper_columns(df)

    assert result.loc[0, "joining_month"] == 1
    assert result.loc[0, "joining_year"] == 2023
    assert result.loc[1, "joining_month"] == 3
    assert result.loc[1, "joining_year"] == 2024
    assert "tenure_days" in result.columns


def test_employee_types_are_converted():
    df = pd.DataFrame({
        "salary": ["30000", "45000"],
        "joining_date": ["2023-01-10", "2024-03-01"],
    })

    result = convert_employee_types(df)

    assert pd.api.types.is_numeric_dtype(result["salary"])
    assert pd.api.types.is_datetime64_any_dtype(result["joining_date"])
    assert result.loc[0, "salary"] == 30000
    assert result.loc[0, "joining_date"].year == 2023


def test_invalid_salary_and_date_become_missing():
    df = pd.DataFrame({
        "salary": ["30000", "not_a_salary"],
        "joining_date": ["2023-01-10", "not_a_date"],
    })

    result = convert_employee_types(df)

    assert pd.isna(result.loc[1, "salary"])
    assert pd.isna(result.loc[1, "joining_date"])


def test_invalid_employee_types_are_separated():
    df = pd.DataFrame({
        "employee_id": [101, 102, 103],
        "salary": [30000, None, 45000],
        "joining_date": pd.to_datetime([
            "2023-01-10",
            "2023-05-15",
            None,
        ]),
    })

    valid_df, rejected_df = separate_invalid_employee_types(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 2
    assert valid_df["employee_id"].tolist() == [101]
    assert "rejection_reason" in rejected_df.columns
