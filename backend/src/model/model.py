class ChatRequest:
    def __init__(self, model, user, temperature, question, history, ability):
        self.model = model
        self.user = user
        self.temperature = temperature
        self.question = question
        self.history = history
        self.ability = ability
    params = ['model', 'user', 'temperature', 'question', 'history',
              'ability']  # TODO: move to api model
