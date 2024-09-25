class PromptManager:
    def __init__(self):
        self.prompts = {}

    def load_prompt(self, name, file_path):
        with open(file_path, 'r') as file:
            self.prompts[name] = file.read()

    def get_prompt(self, name):
        return self.prompts.get(name, '')
