class User(object):

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username
        }
