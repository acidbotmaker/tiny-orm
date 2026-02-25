from pydantic import BaseModel
from typing import Optional


# Pydantic method to define the structure of Student object
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    dept: str
