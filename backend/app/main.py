from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.events import router as events_router
from app.api.metrics import router as metrics_router
from app.db.database import init_db


app = FastAPI(title="eBPF Server Monitor MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.50.223:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(metrics_router)
app.include_router(events_router)
