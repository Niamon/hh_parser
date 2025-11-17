import requests
import time
from collections import defaultdict
from .base import ParserBase


def delay(func):

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        time.sleep(0.1)
        return result
    return wrapper



class API_Parser(ParserBase):
    API_URL = "https://api.hh.ru/vacancies"

    def build_params(self):
        return {
            "text": self.query,
            "page": 0,
            "per_page": self.per_page
        }

    def get_pages_count(self, params):
        response = requests.get(self.API_URL, params=params)
        data = response.json()

        pages_total = data.get("pages", 1)
        found_total = data.get("found", 0)

        print(f"Найдено вакансий: {found_total}")
        print(f"Количество страниц: {pages_total}")

        return pages_total


    @delay
    def fetch_vacancy_details(self, vacancy_id):
        url = f"{self.API_URL}/{vacancy_id}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception:

            return None, [], None

        schedule = data.get("schedule", {}).get("name")
        key_skills = [skill["name"] for skill in data.get("key_skills", [])]
        experience = data.get("experience", {}).get("name")
        return schedule, key_skills, experience


    def fetch(self):
        params = self.build_params()
        total_pages = self.get_pages_count(params)

        all_vacancies = []

        for page in range(total_pages):
            params["page"] = page
            response = requests.get(self.API_URL, params=params)
            data = response.json()

            for item in data.get("items", []):
                vacancy_id = item["id"]

                schedule, key_skills, experience = self.fetch_vacancy_details(vacancy_id)

                area = item.get("area", {})
                city = area.get("name")

                salary_data = item.get("salary") or {}
                salary_from = salary_data.get("from")
                salary_to = salary_data.get("to")
                gross = 1 if salary_data.get("gross") else 2  # 1 = до вычета налогов, 2 = после
                currency = salary_data.get("currency")
                vacancy = defaultdict(lambda: None)
                vacancy["name"] = item.get("name")
                vacancy["company"] = item.get("employer", {}).get("name")
                vacancy["salary_from"] = salary_from
                vacancy["salary_to"] = salary_to
                vacancy["salary_gross"] = gross
                vacancy["salary_currency"] = currency
                vacancy["schedule"] = schedule
                vacancy["experience_level"] = experience
                vacancy["city"] = city
                vacancy["key_skills"] = key_skills
                vacancy["url"] = item.get("alternate_url")

                all_vacancies.append(dict(vacancy))

        return all_vacancies
