"""
Loading data
"""
import json

class DataLoader:
    def __init__(self, questions_path):
        self.questions_path = questions_path
        self.additional_questions = ""

    def load_questions(self):
        with open(self.questions_path, encoding='utf-8', errors='ignore') as q:
            questions = json.load(q)
            self.additional_questions = '\n\n'.join(list((f'<b>{k}</b>\n    — {v}' for k, v in questions.items())))

        return self.additional_questions