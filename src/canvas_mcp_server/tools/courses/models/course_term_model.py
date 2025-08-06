from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Annotated
from datetime import datetime


class Term(BaseModel):
    id: Annotated[int, Field(example=1)]
    name: Annotated[str, Field(example="Default Term")]
    start_at: Annotated[
        Optional[datetime], Field(example="2012-06-01T00:00:00-06:00")
    ] = None
    end_at: Annotated[
        Optional[datetime], Field(example="2012-09-01T00:00:00-06:00")
    ] = None

