from typing import TypedDict
from datetime import datetime

class TimelineDict(TypedDict):
    FIRST_UPDATE: str
    LAST_REACT: str
    LAST_REMINDED: str
    WARN_MODE:bool

class ActionDict(TypedDict):
    MESSAGE: int       # số tin nhắn
    VOICE_TIME: int    # số phút voice
    REACTION: int      # số lần reaction

class LevelDict(TypedDict):
    LEVEL: int
    EXP: int
    LEVEL_EXP: int
    TOTAL_EXP: int

class UserData(TypedDict):
    NAME: str
    DISPLAY: str
    TIMELINE: TimelineDict
    ACTION: ActionDict
    LVL: LevelDict

# dict chính: id (chuỗi) -> UserData
DataJson = dict[str, UserData]