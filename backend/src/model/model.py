class ChatRequest:
    def __init__(self, model, user, question, history, ability):
        self.model = model
        self.user = user
        self.question = question
        self.history = history
        self.ability = ability
    params = ['model', 'user', 'question', 'history', 'ability']
