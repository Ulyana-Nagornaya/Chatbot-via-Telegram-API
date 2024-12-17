"""
Loading data
"""
import json

class DataLoader:
    def __init__(self, clear_data_path, questions_path):
        self.clear_data_path = clear_data_path
        self.questions_path = questions_path
        self.data = {}
        self.additional_questions = ""

    def load_data(self):
        with open(self.clear_data_path, encoding='utf-8', errors='ignore') as f:
            self.data = json.load(f)

        with open(self.questions_path, encoding='utf-8', errors='ignore') as q:
            questions = json.load(q)
            self.additional_questions = '\n\n'.join(list((f'<b>{k}</b>\n    — {v}' for k, v in questions.items())))

        return self.data, self.additional_questions