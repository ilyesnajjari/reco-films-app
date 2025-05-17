from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    title: str
    genre: str
    year: int
    description: str
    director: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    director: Optional[str] = None

class Movie(MovieBase):
    id: int
    average_rating: float

    class Config:
        #orm_mode = True
        from_attributes = True