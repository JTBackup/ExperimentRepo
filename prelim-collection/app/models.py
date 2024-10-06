from dataclasses import dataclass
from typing import List



@dataclass
class User:
    first_name: str
    last_name: str
    age: str
    email: str
    gender: str
    type_of_participant: str
    time_spent: str
    platforms_used: List[str]
    

@dataclass
class UserResponse:
    responses: dict
    audio_files: List
