from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Annotated
from datetime import datetime


class Term(BaseModel):
    id: Annotated[str, Field(example="VGVybS0yMjQ=")]
    name: Annotated[str, Field(example="Fall 2025")]
    startAt: Annotated[
        Optional[datetime], Field(example="2025-08-12T23:59:00-05:00")
    ] = None
    endAt: Annotated[
        Optional[datetime], Field(example="2025-12-20T00:00:00-06:00")
    ] = None

