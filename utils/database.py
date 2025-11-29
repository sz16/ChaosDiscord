from firebase_admin import db
from .data_type import UserData, DataJson
from typing import cast
import logging
from datetime import datetime

log = logging.getLogger(__name__)

ref = db.reference("/")

messageExp = 1
reactionExp = 5
voiceExp = 1

baseExp = 100
incExp = 25

def _NewUser(name: str, display_name: str) -> UserData:
    newData: UserData= {
        "NAME": name,
        "DISPLAY": display_name,
        "TIMELINE": {
            "FIRST_UPDATE": datetime.now().strftime("%Y-%m-%d"),
            "LAST_REACT": datetime.now().strftime("%Y-%m-%d"),
            "LAST_REMINDED": datetime.now().strftime("%Y-%m-%d"),
        },
        "ACTION": {
            "MESSAGE": 0,
            "VOICE_TIME": 0,
            "REACTION": 0 
        },
        "LVL": {
            "LEVEL": 1,
            "EXP": 0,
            "LEVEL_EXP": baseExp,
            "TOTAL_EXP": 0,
        }
    }
    return newData

def addNewUser(id: str, name: str, display_name: str):
    return ref.child(id).update(_NewUser(name, display_name))
    
def getDatabase() -> DataJson:
    return cast(DataJson, ref.get())

def getUser(id: str) -> UserData:
    user = ref.child(id).get()
    if user is None:
        log.info(f"User {id} not found")
        addNewUser(id, "Unknown", "Unknown")
        return getUser(id)
    return cast(UserData, user)

def updateUser(id: str, data: UserData):
    return ref.child(id).update(data)

def deleteUser(id: str):
    return ref.child(id).delete()

def batchUpdate(data: DataJson):
    'Data must be a DataJson object'
    if len(data.keys()) == 0: return
    ref.update(data)
    
def setDatabase(data: DataJson):
    return ref.set(data)

def updateName(id: str, name: str, display_name: str):
    user = getUser(id)
    user["NAME"] = name
    user["DISPLAY"] = display_name
    updateUser(id, user)

def addExp(id: str, userdata: UserData, amount, needUpdate: bool = True):
    userlvl = userdata["LVL"]
    userlvl["EXP"] += amount
    if userlvl["EXP"] < 0:
        userlvl["EXP"] = 0
    userlvl["TOTAL_EXP"] += amount
    
    while userlvl["EXP"] >= userlvl["LEVEL_EXP"]:
        userlvl["EXP"] -= userlvl["LEVEL_EXP"]
        userlvl["LEVEL"] += 1
        userlvl["LEVEL_EXP"] += incExp
    
    userdata["TIMELINE"]["LAST_REACT"] = datetime.now().strftime("%Y-%m-%d")
    userdata["TIMELINE"]["LAST_REMINDED"] = datetime.now().strftime("%Y-%m-%d")

    if needUpdate:
        updateUser(id, userdata)    
    
def addMessage(id: str):
    user = getUser(id)
    user["ACTION"]["MESSAGE"] += 1
    addExp(id, user, messageExp)

def addReaction(id: str):
    user = getUser(id)
    user["ACTION"]["REACTION"] += 1
    addExp(id, user, reactionExp)
    
def addVoice(ids: list[str]):
    if len(ids) == 0: return
    batch: DataJson = {}
    database = getDatabase()
    for id in ids:
        user: UserData = database[id]
        user["ACTION"]["VOICE_TIME"] += 1
        addExp(id, user, voiceExp)
        batch[id] = user
    batchUpdate(batch)

def addWarns(ids):
    batch: DataJson = {}
    database = getDatabase()
    for id in ids:
        user: UserData = database[id]
        user["TIMELINE"]["LAST_REMINDED"] = datetime.now().strftime("%Y-%m-%d")
        batch[id] = user
    batchUpdate(batch)

def verifyDatabase(userList: list):
    'userlist: [("id","name","display")]'
    batch: DataJson = {}
    database: DataJson= getDatabase()
    for id, name, display in userList:
        if id not in database:
            batch[id] = _NewUser(name, display)
        else:
            if database[id]["NAME"] != name or database[id]["DISPLAY"] != display: 
                log.info(f"Update name of {id} with name from {database[id]['NAME']} to {name} and display from {database[id]['DISPLAY']} to {display}")
                database[id]["NAME"] = name
                database[id]["DISPLAY"] = display
                batch[id] = database[id]
    
    batchUpdate(batch)
    setId = set(i[0] for i in userList)
    for id in database.keys():
        if id not in setId:
            log.info(f"Delete user {id}, name {database[id]['NAME']}")
            deleteUser(id)

def getScoreboard():
    database = getDatabase()
    board = sorted(database.items(), key=lambda x: x[1]["LVL"]["TOTAL_EXP"], reverse=True)
    return board