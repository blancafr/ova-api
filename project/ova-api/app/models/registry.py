from sqlalchemy import Column, Integer, String, Date
from app.db.registry_database import Base

class Registry(Base):
    __tablename__ = "registry"

    id = Column(String, primary_key=True, index=True)
    row_num = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    sex = Column(String, nullable=False)
    age = Column(String, nullable=False)
    diseases = Column(String, nullable=False)
