class Todo(object):

    def __init__(self, id, user, description, completed):
        self.id = id
        self.user = user
        self.description = description
        self.completed = completed

    def to_json(self):
        json_dict = self.__dict__
        json_dict['user'] = self.user.to_json()

        return json_dict