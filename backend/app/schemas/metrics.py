from pydantic import BaseModel, Field


class SystemMetricCreate(BaseModel):
    host: str = Field(default="localhost", max_length=255)
    cpu_usage: float = Field(ge=0, le=100)
    memory_total: int = Field(ge=0)
    memory_used: int = Field(ge=0)
    memory_usage: float = Field(ge=0, le=100)
    load_avg_1: float = Field(ge=0)
    load_avg_5: float = Field(ge=0)
    load_avg_15: float = Field(ge=0)


class SystemMetric(SystemMetricCreate):
    id: int
    created_at: str

