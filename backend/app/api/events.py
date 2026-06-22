from fastapi import APIRouter, Query
from typing import Optional

from app.db.database import get_connection
from app.schemas.events import ProcessEvent, ProcessEventCreate


router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/process", response_model=ProcessEvent, status_code=201)
def create_process_event(payload: ProcessEventCreate) -> ProcessEvent:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO process_events (
                host, event_type, pid, ppid, uid, comm, filename, exit_code
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.host,
                payload.event_type,
                payload.pid,
                payload.ppid,
                payload.uid,
                payload.comm,
                payload.filename,
                payload.exit_code,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM process_events WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return ProcessEvent(**dict(row))


@router.get("/process", response_model=list[ProcessEvent])
def list_process_events(
    host: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[ProcessEvent]:
    params: list[object] = []
    where = ""
    if host:
        where = "WHERE host = ?"
        params.append(host)

    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM process_events
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [ProcessEvent(**dict(row)) for row in rows]
