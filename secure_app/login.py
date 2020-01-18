import uuid
import bcrypt

class Login:
    def __init__(self, redis, mongo):
        self.redis_conn = redis
        self.mongo = mongo
    
    def generate_uuid(self):
        new_uuid = uuid.uuid4()
        while self.redis_conn.hget('sessions', str(new_uuid)):
            new_uuid = uuid.uuid4()
        return str(new_uuid)

    def login(self, login, password):
        try:
            user = self.mongo.db.user.find_one({ "login": login })
            if user is not None:
                return bcrypt.checkpw(password, user.get("hash"))         
        except:
            return False
        return False

    
