import os
from dotenv import load_dotenv
import warnings
import pandas as pd

from methods import API_Parser
from bd.vacancy_db import VacancyDB
from bd.delete_bd import clear_vacancies_table
from bd.cache import VacancyCache
from stats.compute_by_vacancy import VacancyStats

warnings.filterwarnings("ignore")


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

dsn = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def main():
    query = input("Введите запрос: ").strip()

    safe_query = query.lower().replace(" ", "_")
    cache = VacancyCache(f"vacancy_cache_{safe_query}.json")

    vacancies = cache.load()  

    if vacancies is None:
        clear_vacancies_table()
        parser = API_Parser(query=query, per_page=50)
        vacancies = parser.fetch()
        cache.save(vacancies)
        print("Вакансии сохранены в кэш.")
    else:
        print("Данные загружены из кэша.")


    #dsn = "postgresql+psycopg2://postgres:postgres@localhost:5432/vacancies_db"
    db = VacancyDB(dsn)

    existing_rows = db.read_all()
    if not existing_rows:
        db.insert_many(vacancies)
        print("Вакансии сохранены в базу.")
    else:
        print("Вакансии уже есть в базе, вставка не требуется.")


    rows = db.read_all()
    df = pd.DataFrame(rows)
    print("Первые 5 вакансий:")
    print(df.head())


    stats = VacancyStats(dsn)
    df_db = stats.load_data()

  
    stats.plot_salary_distribution(df_db)


    stats.plot_vacancies_by_city(df_db, top_n=10)


    stats.plot_key_skills(df_db, top_n=20)


    stats.plot_salary_by_city(df_db, top_n=10)

if __name__ == "__main__":
    main()
