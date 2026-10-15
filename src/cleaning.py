
import pandas as pd


def clean_dataframe(df, required_columns):
    """Perform basic cleaning and separate rejected rows."""

    df = df.copy()

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove leading and trailing spaces from text columns.
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].str.strip()

    # Treat empty text as missing.
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # Separate rows with missing required values.
    invalid_mask = df[required_columns].isna().any(axis=1)
    rejected_df = df.loc[invalid_mask].copy()
    valid_df = df.loc[~invalid_mask].copy()

    # Remove duplicate rows from the valid data.
    duplicate_mask = valid_df.duplicated(keep="first")
    duplicate_rows = valid_df.loc[duplicate_mask].copy()
    duplicate_rows["rejection_reason"] = "Duplicate row"

    rejected_df["rejection_reason"] = "Missing required value"
    rejected_df = pd.concat(
        [rejected_df, duplicate_rows],
        ignore_index=True,
    )

    valid_df = valid_df.loc[~duplicate_mask].copy()

    return valid_df, rejected_df


def add_employee_helper_columns(df):
    """Add useful date-related columns to employee data."""

    df = df.copy()

    if "joining_date" not in df.columns:
        raise ValueError("Required column 'joining_date' is missing")

    df["joining_date"] = pd.to_datetime(
        df["joining_date"],
        errors="coerce",
    )

    df["joining_month"] = df["joining_date"].dt.month
    df["joining_year"] = df["joining_date"].dt.year

    today = pd.Timestamp.today().normalize()

    df["tenure_days"] = (
        today - df["joining_date"]
    ).dt.days

    # Future joining dates should not have negative tenure.
    df.loc[df["tenure_days"] < 0, "tenure_days"] = pd.NA

    return df


def convert_employee_types(df):
    """Convert salary and joining date to appropriate types."""

    df = df.copy()

    if "salary" in df.columns:
        df["salary"] = pd.to_numeric(
            df["salary"],
            errors="coerce",
        )

    if "joining_date" in df.columns:
        df["joining_date"] = pd.to_datetime(
            df["joining_date"],
            errors="coerce",
        )

    return df


def separate_invalid_employee_types(df):
    """Separate rows with invalid salary or joining date."""

    df = df.copy()
    invalid_mask = pd.Series(False, index=df.index)

    if "salary" in df.columns:
        invalid_mask |= df["salary"].isna()

    if "joining_date" in df.columns:
        invalid_mask |= df["joining_date"].isna()

    rejected_df = df.loc[invalid_mask].copy()
    valid_df = df.loc[~invalid_mask].copy()

    rejected_df["rejection_reason"] = "Missing or invalid salary/date"

    return valid_df, rejected_df
