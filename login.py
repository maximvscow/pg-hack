class UserLogin:
    def fromDB(self, login, cur):
        cur.execute("SELECT * FROM pg_shadow WHERE usename = '" + login + "';")
        self.__user = cur.fetchone()
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user[1])
