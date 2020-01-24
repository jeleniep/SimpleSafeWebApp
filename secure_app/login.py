import uuid
import bcrypt
from datetime import datetime, timedelta
from dateutil import parser

import time

class Login:
    def __init__(self, redis, mongo):
        self.redis_conn = redis
        self.mongo = mongo
    
    def generate_uuid(self):
        new_uuid = uuid.uuid4()
        while self.redis_conn.hget('sessions', str(new_uuid)):
            new_uuid = uuid.uuid4()
        return str(new_uuid)

    def check_if_ip_locked(self, ip):
        lock_date = self.redis_conn.hget("lock_date", ip)
        if lock_date:
            lock_date = parser.parse(lock_date)
            if datetime.now() < lock_date:
                return lock_date
        return None


    def login_failed(self, ip):
        failed_login_tries = self.redis_conn.hget("failed_login", ip) or 0
        failed_login_tries = int(failed_login_tries) + 1
        if failed_login_tries > 2:
            lock_time = datetime.now() + timedelta(minutes = 5)
            self.redis_conn.hset("lock_date", ip, str(lock_time))
            self.redis_conn.hset("failed_login", ip, 0)
        else:
            self.redis_conn.hset("failed_login", ip, failed_login_tries)

            


    def login(self, login, password, ip):
        try:
            lock_date = self.check_if_ip_locked(ip)
            if lock_date: 
                return {
                    "code": 401,
                    "status": "Logowanie zablokowanie do " + str(lock_date)
                }   
             
            user = self.mongo.db.user.find_one({ "login": login })
            if user is not None:
                password_correct = bcrypt.checkpw(password, user.get("hash"))
                self.add_ip_to_login_history(user.get("_id"), ip, password_correct)
                time.sleep(3)
                if password_correct:
                    self.redis_conn.hset("failed_login", ip, 0)
                    return {
                        "code": 200,
                        "status": ""
                    }
        except:
            return {
            "code": 500,
            "status": "Wystąpił błąd podczas logowania."
            }
        self.login_failed(ip)
        return {
            "code": 401,
            "status": "Niepoprawne dane logowania."
        }
    
    def add_ip_to_login_history(self, id, ip, password_correct):
        try:
            new_login = {
                "ip": ip,
                "date": str(datetime.now()),
                "successful": password_correct
            }
            user_login_history = self.mongo.db.login_history.find_one({ "user_id": id })
            if user_login_history is None:
                user_login_history = {
                    "user_id": id,
                    "history": [new_login]
                }
                self.mongo.db.login_history.insert_one(user_login_history)
            else:
                user_login_history["history"].insert(0, new_login)
                self.mongo.db.login_history.replace_one({ "user_id": id }, user_login_history)

            print(user_login_history["history"])
        except:
            return

    def get_login_history(self, login):
        try:
            user = self.mongo.db.user.find_one({ "login": login })
            if user is not None:
                user_login_history = self.mongo.db.login_history.find_one({ "user_id": user.get("_id") })
                return user_login_history["history"]
        except:
            return []
        return []