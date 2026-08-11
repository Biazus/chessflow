from pydantic import BaseModel


class PositionResponse(BaseModel):
    move_number: int
    move_san: str
    fen: str

    class Config:
        from_attributes = True