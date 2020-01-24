import uuid
import crypt
import random
import string
import re
from bson import ObjectId


# pattern.match(string)

class Notes:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_users_list(self):
        try: 
            logins_list = []
            users = self.mongo.db.user.find()
            for user in users:
                print(user["login"], flush=True)
                logins_list.append(user["login"])
            return logins_list
        except:            
             return []

    def add_note(self, note_data, login):
        text = note_data.get('note')
        usernames = note_data.getlist('users')
        pattern = re.compile("^[A-Za-z0-9    _.]+")

        ret = {
                "code": 201,
                "status": None
        }
        if pattern.fullmatch(text) is None:
            ret = {
            "code": 406,
            "status": "Notatka może składać się tylko z liter, cyfr, spacji oraz znaku '_'."
            }
            return ret

        user_ids = []
        owner = self.mongo.db.user.find_one({"login": login})
        owner_id = ""

        if owner is not None:
            owner_id = owner["_id"]

        for username in usernames:
            user = self.mongo.db.user.find_one({"login": username})
            if user is not None:
                user_ids.append(user["_id"])

        note = {
            "text": text,
            "users_allowed": user_ids,
            "public": len(user_ids) == 0,
            "owner": owner_id
        }

        try:
            self.mongo.db.note.insert_one(note)  
        except:
            ret = {
                "code": 500,
                "status": "Błąd przy dodawaniu notatki."
            }
        return ret

    def get_notes(self, login):
        try: 
            user = self.mongo.db.user.find_one({"login": login})
            if user is None:
                return []
            notes_list = []
            notes = self.mongo.db.note.find({ "$or": [ { "users_allowed": user["_id"] }, { "public": True }, { "owner": user["_id"] } ] })

            # print("\n\n\n\n blee \n\n", flush=True)

            for note in notes:
                owner_username = ""
                user = self.mongo.db.user.find_one({"_id": ObjectId(note["owner"])})
                if user is not None:
                     owner_username = user["login"]
                # print(note["public"], flush=True)
                notes_list.append({ "text": note["text"], "id": note["_id"], "owner": owner_username, "can_delete": login == owner_username})
            return notes_list
        except:            
             return []

    def delete_note(self, note_id, login):      
        try:
            note = self.mongo.db.note.find_one({"_id": ObjectId(note_id)})
            user = self.mongo.db.user.find_one({"login": login})
            if user["_id"] == note["owner"]:
                self.mongo.db.note.delete_one({"_id": ObjectId(note_id)})
                return {
                    "code": 201,
                    "status": None
                }   
        except:
            return {
                "code": 500,
                "status": "Błąd podczas usuwania."
            }
        return {
            "code": 401,
            "status": "Brak uprawnień."
        }

    def edit_note(self, note_id, login):
        return False
