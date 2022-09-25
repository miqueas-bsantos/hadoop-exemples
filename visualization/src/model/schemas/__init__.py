from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class DefaultResponseData(BaseModel):
    statusCode: Optional[int] = 200
    meta: Optional[dict] = {}
    messages: Optional[str] = None
    # data: List[Optional[ReportDetail]]
