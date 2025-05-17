from sqlalchemy import Column, Integer, String, Text, Float
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String, index=True)
    year = Column(Integer)
    description = Column(Text)
    average_rating = Column(Float, default=0.0)
    director = Column(String, index=True)


