from data_functions import hash_pw
from db_procs import insert_user, get_user_id
from validation import check_email, check_name


class User:
    def __init__(self, name, email, password):
        self._id = None
        self._email = None
        self._name = None
        self._password = None
        try:
            self.name = name
        except ValueError:
            raise ValueError("name")
        try:
            self.email = email
        except ValueError:
            raise ValueError("email")
        try:
            self.password = password
        except ValueError:
            raise ValueError("passwd")
        self._insert()
        self.id = None

    def _insert(self):
        name = self.name
        email = self.email
        password = self._password
        insert_user(name, email, password)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, dummy):
        self._id = dummy
        self._id = get_user_id(self._email)

    @property
    def name(self):
        return str(self._name)

    @name.setter
    def name(self, val):
        if check_name(val):
            self._name = val
        else:
            raise ValueError

    @property
    def email(self):
        return str(self._email)

    @email.setter
    def email(self, val):
        if check_email(val):
            self._email = val
        else:
            raise ValueError

    @property
    def password(self):
        return False

    @password.setter
    def password(self, val):
        if 6 <= len(val):
            self._password = hash_pw(val)
        else:
            raise ValueError
