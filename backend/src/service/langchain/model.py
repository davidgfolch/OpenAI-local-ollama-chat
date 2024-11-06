from numbers import Number


class UserData:
    def __init__(self, user: str, model: str, temperature: Number, ability: str, history: str, question: str, chatType):
        self.user = user
        self.model = model
        self.temperature = temperature
        self.ability = ability
        self.history = history
        self.question = question
        self.chatType = chatType
        self.chatInstance = None
        self.chatInstanceModel = None
