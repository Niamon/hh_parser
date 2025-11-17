from sqlalchemy import create_engine, Column, Integer, String, ARRAY
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    company = Column(String)

    salary_from = Column(Integer)
    salary_to = Column(Integer)
    salary_gross = Column(Integer)
    salary_currency = Column(String)
    schedule = Column(String)
    experience_level = Column(String)
    city = Column(String)
    key_skills = Column(ARRAY(String))
    url = Column(String)


class VacancyDB:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_many(self, vacancies: list[dict]):
        session = self.Session()
        objects = [Vacancy(**v) for v in vacancies]
        session.add_all(objects)
        session.commit()
        session.close()

    def read_all(self) -> list[dict]:
        session = self.Session()
        rows = session.query(Vacancy).all()
        session.close()
        return [
            {
                "id": r.id,
                "name": r.name,
                "company": r.company,
                "salary_from": r.salary_from,
                "salary_to": r.salary_to,
                "salary_gross": r.salary_gross,
                "schedule": r.schedule,
                "experience_level": r.experience_level,
                "city": r.city,
                "key_skills": r.key_skills,
                "url": r.url,
            }
            for r in rows
        ]
