from pydantic import BaseModel
from typing import Optional

class CobaltPriceResponse(BaseModel):
    price_date: str
    price: float
    raw_text: Optional[str] = None

    class Config:
        from_attributes = True
