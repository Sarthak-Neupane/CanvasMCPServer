from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class Term(BaseModel):
    id: Annotated[str, Field(examples=["VGVybS0yMjQ="])]
    name: Annotated[str, Field(examples=["Fall 2025"])]
    startAt: Annotated[
        Optional[datetime], Field(examples=["2025-08-12T23:59:00-05:00"])
    ] = None
    endAt: Annotated[
        Optional[datetime], Field(examples=["2025-12-20T00:00:00-06:00"])
    ] = None
