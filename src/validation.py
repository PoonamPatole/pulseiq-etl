
import pandas as pd
import pandera.pandas as pa


def validate_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate either the original employee sample or the workbook dimension."""

    df = df.copy()

    # Keep compatibility with the original project tests.
    if "joining_date" in df.columns:
        for column in ["joining_date"]:
            df[column] = pd.to_datetime(df[column], errors="coerce")

        schema = pa.DataFrameSchema(
            {
                "employee_id": pa.Column(
                    int,
                    nullable=False,
                    unique=True,
                ),
                "salary": pa.Column(
                    float,
                    checks=pa.Check.ge(0),
                    nullable=False,
                ),
                "joining_date": pa.Column(
                    pa.DateTime,
                    nullable=False,
                ),
            },
            strict=False,
            coerce=True,
        )

        return schema.validate(df, lazy=True)

    # Validate the actual PulseIQ employee dimension.
    date_columns = [
        "hire_date",
        "exit_date",
        "valid_from",
        "valid_to",
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    schema = pa.DataFrameSchema(
        {
            "employee_key": pa.Column(
                int,
                nullable=False,
                unique=True,
            ),
            "employee_id": pa.Column(
                str,
                nullable=False,
            ),
            "hire_date": pa.Column(
                pa.DateTime,
                nullable=False,
            ),
            "exit_date": pa.Column(
                pa.DateTime,
                nullable=True,
            ),
            "valid_from": pa.Column(
                pa.DateTime,
                nullable=False,
            ),
            "valid_to": pa.Column(
                pa.DateTime,
                nullable=True,
            ),
        },
        strict=False,
        coerce=False,
    )

    return schema.validate(df, lazy=True)

def validate_employee_history(df: pd.DataFrame) -> pd.DataFrame:
    """Detect overlapping historical versions of the same employee."""
    df = df.copy()

    required_columns = {"employee_id", "valid_from", "valid_to"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns for history validation: {sorted(missing)}"
        )

    for column in ["valid_from", "valid_to"]:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    if df["employee_id"].isna().any() or df["valid_from"].isna().any():
        raise ValueError("Employee ID and valid_from must not be missing.")

    for employee_id, group in df.groupby("employee_id"):
        group = group.sort_values("valid_from")
        rows = list(
            group[["valid_from", "valid_to"]].itertuples(
                index=False, name=None
            )
        )

        for i in range(1, len(rows)):
            previous_start, previous_end = rows[i - 1]
            current_start, current_end = rows[i]

            # A missing valid_to means the previous version remains open.
            if pd.isna(previous_end) or previous_end >= current_start:
                raise ValueError(
                    "Overlapping employee history for "
                    f"employee_id={employee_id}: "
                    f"previous period {previous_start} to {previous_end}; "
                    f"next period {current_start} to {current_end}"
                )

    return df
