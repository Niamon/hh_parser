import json
import os

class VacancyCache:
    def __init__(self, filename="vacancy_cache.json"):
        self.filename = filename

    def save(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.filename):
            return None

        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)
