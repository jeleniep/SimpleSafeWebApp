import uuid
import random
import string
import re
import bcrypt

# pattern.match(string)

class Register:
    def __init__(self, mongo):
        self.mongo = mongo
    
    def check_login(self, login):
        user = self.mongo.db.user.find_one({"login": login})
        if user is not None:
            ret = {
                "code": 400,
                "status": "Podany login jest już zajęty"
            }
            return ret
        pattern = re.compile("[A-Za-z0-9_]+")
        if pattern.fullmatch(login) is None:
            ret = {
                "code": 400,
                "status": "Login może składać się tylko z małych i dużych liter, cyfr oraz znaku '_'."
            }
            return ret
        return None
    
    def check_password(self, password, repeat_password):
        if password != repeat_password:
            ret = {
                "code": 404,
                "status": "Podane hasła są niezgodne"
            }
            return ret
        length_error = len(password) < 8
        digit_error = re.search(r"\d", password) is None
        uppercase_error = re.search(r"[A-Z]", password) is None
        lowercase_error = re.search(r"[a-z]", password) is None
        password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error )
        if not password_ok:
            ret = {
                "code": 400,
                "status": "Hasło powinno składać z małej i wielkiej litery, cyfry oraz mieć długość przynajmniej 8 znaków."
            }
            return ret
        return None
        

    def create_user(self, login, password):
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(12))
        print("\n\n" + hashed_password, flush=True)
        user = {
            "login": login,
            "hash": hashed_password,
        }

        try: 
            self.mongo.db.user.insert_one(user)
        except:            
            ret = {
                "code": 500,
                "status": "Błąd przy dodawaniu użytkownika"
            }
            return ret
    
    def change_password(self, login, change_password_data):
        ret = {
            "code": 500,
            "status": "Błąd podczas zmiany hasła."
        }

        old_password = change_password_data.get('old_password')
        password = change_password_data.get('password')
        repeat_password = change_password_data.get('repeated_password')
        ret_check_password = self.check_password(password, repeat_password)
        if ret_check_password is not None:
            return ret_check_password

        try:
            user = self.mongo.db.user.find_one({ "login": login })
            if user is not None:
                if bcrypt.checkpw(old_password, user.get("hash")):
                    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(12))
                    self.mongo.db.user.update_one({ "login": login }, {"$set": { "hash": hashed_password }})
                    ret = {
                        "code": 201,
                        "status": None
                    }
                    return ret
            ret = {
                "code": 500,
                "status": "Podane hasło jest nieprawidłowe."
            }
            return ret
        except:
            return ret

        return ret

    def register(self, registration_data):
        login = registration_data.get('login')
        password = registration_data.get('password')
        repeat_password = registration_data.get('repeated_password')
        ret = self.check_login(login)
        if ret is not None:
            return ret

        ret = self.check_password(password, repeat_password)
        if ret is not None:
            return ret

        
        ret = self.create_user(login, password)
        if ret is not None:
            return ret

        ret = {
            "code": 201,
            "status": None
        }
        return ret

    def test(self):
        print("test", flush=True)
    
