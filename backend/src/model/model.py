class ChatRequest:
    def __init__(self, errRes, model, user, question, history, ability):
        self.errRes = errRes
        self.model = model
        self.user = user
        self.question = question
        self.history = history
        self.ability = ability
    params = ['model', 'user', 'question', 'history', 'ability']
