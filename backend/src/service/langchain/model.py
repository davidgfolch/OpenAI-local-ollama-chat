class UserData:
    def __init__(self, user, model, ability, history, question, chatType):
        self.user = user
        self.model = model
        self.ability = ability
        self.history = history
        self.question = question
        self.chatType = chatType
        self.chatInstance = None
        self.chatInstanceModel = None
