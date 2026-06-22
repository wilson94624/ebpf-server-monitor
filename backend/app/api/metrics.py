from fastapi import APIRouter, Query
from typing import Optional

from app.db.database import get_connection
from app.schemas.metrics import SystemMetric, SystemMetricCreate


router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.post("/system", response_model=SystemMetric, status_code=201)
def create_system_metric(payload: SystemMetricCreate) -> SystemMetric:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO system_metrics (
                host, cpu_usage, memory_total, memory_used, memory_usage,
                load_avg_1, load_avg_5, load_avg_15
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.host,
                payload.cpu_usage,
                payload.memory_total,
                payload.memory_used,
                payload.memory_usage,
                payload.load_avg_1,
                payload.load_avg_5,
                payload.load_avg_15,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM system_metrics WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return SystemMetric(**dict(row))


@router.get("/system", response_model=list[SystemMetric])
def list_system_metrics(
    host: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[SystemMetric]:
    params: list[object] = []
    where = ""
    if host:
        where = "WHERE host = ?"
        params.append(host)

    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM system_metrics
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [SystemMetric(**dict(row)) for row in rows]
