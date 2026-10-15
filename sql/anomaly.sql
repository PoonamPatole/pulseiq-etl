CREATE TABLE IF NOT EXISTS dw.fact_anomaly (
    result_id TEXT PRIMARY KEY,
    source_dataset TEXT NOT NULL,
    record_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    period DATE NOT NULL,
    anomaly_score NUMERIC(4,3) NOT NULL,
    flagged CHAR(1) NOT NULL,
    reason_code TEXT NOT NULL,
    reason_text TEXT NOT NULL,
    money_at_risk NUMERIC(14,2),
    model_version TEXT NOT NULL,
    scored_at TIMESTAMP NOT NULL,
    period_key INTEGER
);
