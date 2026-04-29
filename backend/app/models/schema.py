from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start: str
    end: str


class DatasetProfile(BaseModel):
    label: str
    count: int
    total_amount: float
    duplicate_rows: int
    negative_amount_rows: int
    date_range: DateRange


class ReconciliationRecord(BaseModel):
    txn_id: str | None
    settle_id: str | None
    status: str
    transaction_date: str | None
    settlement_date: str | None
    platform_amount: float | None
    settlement_amount: float | None
    amount_delta: float
    days_to_settle: int | None
    explanation: str


class ReconciliationTotals(BaseModel):
    platform_total: float
    settlement_total: float
    net_difference: float
    explained_difference: float
    matched_count: int
    unmatched_count: int
    duplicate_settlement_amount: float


class ReconciliationSummary(BaseModel):
    reporting_month: str
    month_start: str
    month_end: str
    tolerance: float
    record_results: list[ReconciliationRecord]
    totals: ReconciliationTotals


class AnomalyBucket(BaseModel):
    key: str
    title: str
    description: str
    count: int
    net_amount: float
    records: list[ReconciliationRecord]


class ReconciliationResponse(BaseModel):
    assumptions: list[str] = Field(default_factory=list)
    transaction_profile: DatasetProfile
    settlement_profile: DatasetProfile
    reconciliation: ReconciliationSummary
    anomalies: list[AnomalyBucket]
    highlights: list[str]
    sample_source_rows: list[dict[str, Any]]
    sample_target_rows: list[dict[str, Any]]
