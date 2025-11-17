from sqlalchemy import create_engine, text

# -----------------------------
# Настройки подключения
# -----------------------------
USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = 5432
DATABASE = "vacancies_db"

DSN = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

def clear_vacancies_table():
    engine = create_engine(DSN)

    with engine.connect() as conn:
    
        conn.execute(text("DROP TABLE IF EXISTS public.vacancies CASCADE;;"))
        conn.commit()
        print("Все данные из таблицы 'vacancies' удалены.")

if __name__ == "__main__":
    clear_vacancies_table()
