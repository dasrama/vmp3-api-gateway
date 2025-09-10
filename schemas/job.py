from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timezone
from typing import Optional


class Status(str, Enum):
    PENDING="pending"
    PROCESSING="processing"
    COMPLETED="completed"
    FAILED="failed"

class Job(BaseModel):
    job_id: str  
    video_key: str
    mp3_key: str
    status: Status
    created_at: datetime = datetime.now(timezone.utc)
    complete_at: Optional[datetime] = None
