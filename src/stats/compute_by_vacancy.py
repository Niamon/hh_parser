# stats/compute_by_vacancy.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

sns.set(style="whitegrid")

class VacancyStats:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn)
    
    def load_data(self):
        query = "SELECT * FROM vacancies"
        df = pd.read_sql(query, self.engine)
        return df


    def _prepare_salary_columns(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

  
        df["salary_from"] = pd.to_numeric(df.get("salary_from"), errors="coerce")
        df["salary_to"] = pd.to_numeric(df.get("salary_to"), errors="coerce")

        df.loc[df["salary_from"] <= 0, "salary_from"] = pd.NA
        df.loc[df["salary_to"] <= 0, "salary_to"] = pd.NA


        df["salary_mean"] = df[["salary_from", "salary_to"]].mean(axis=1, skipna=True)

        return df

    
    def salary_stats(self, df):
   
        df = self._prepare_salary_columns(df)
        df = df.dropna(subset=["salary_currency", "salary_mean"])

        result = {}

        for curr, curr_df in df.groupby("salary_currency"):
            result[curr] = {
                "min_salary": curr_df["salary_mean"].min(skipna=True),
                "max_salary": curr_df["salary_mean"].max(skipna=True),
                "mean_salary": curr_df["salary_mean"].mean(skipna=True),
                "count": len(curr_df)
            }
         

    
        


    def vacancies_by_city_stats(self, df, top_n=10):
    
        city_counts = df["city"].fillna("Не указано").value_counts().head(top_n)
        return city_counts

    def key_skills_stats(self, df, top_n=20):

        all_skills = []

        for skills_list in df.get("key_skills", []):
            if not skills_list:
                continue
            all_skills.extend(skills_list)
        skill_counts = pd.Series(all_skills).value_counts().head(top_n)
        return skill_counts


    def plot_salary_distribution(self, df: pd.DataFrame):
 
        df_prepared = self._prepare_salary_columns(df)

        
        df_prepared = df_prepared.dropna(subset=["salary_currency", "salary_mean"])

        if df_prepared.empty:
            print("Нет данных с валидной зарплатой для построения распределения.")
            return
        
        currencies = df_prepared["salary_currency"].unique()
        #print(currencies)
        for curr in currencies:
            curr_df = df_prepared[df_prepared["salary_currency"] == curr].copy()
            if curr_df.empty:
                continue

            curr_df = curr_df.sort_values("salary_mean")
            plt.figure(figsize=(12, 5))
            plt.plot(curr_df["salary_mean"].values, marker='o', linestyle='-',
                     label=f"{curr} - {len(curr_df)} вакансий")
            plt.title(f"Распределение средней зарплаты - валюта: {curr}")
            plt.xlabel("Вакансии (отсортированы по salary_mean)")
            plt.ylabel(f"Средняя зарплата ({curr})")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
    
    def plot_vacancies_by_city(self, df, top_n=10):
        city_counts = self.vacancies_by_city_stats(df, top_n)
        plt.figure(figsize=(10,6))
        sns.barplot(x=city_counts.values, y=city_counts.index, palette="viridis")
        plt.xlabel("Количество вакансий")
        plt.ylabel("Город")
        plt.title(f"Топ {top_n} городов по количеству вакансий")
        plt.tight_layout()
        plt.show()
    
    def plot_key_skills(self, df, top_n=20):
        skill_counts = self.key_skills_stats(df, top_n)
        plt.figure(figsize=(10,6))
        sns.barplot(x=skill_counts.values, y=skill_counts.index, palette="magma")
        plt.xlabel("Частота")
        plt.ylabel("Навык")
        plt.title(f"Топ {top_n} ключевых навыков")
        plt.tight_layout()
        plt.show()

    def plot_salary_by_city(self, df, top_n=10):


        df = self._prepare_salary_columns(df)

 
        df = df.dropna(subset=["salary_currency", "salary_mean"])

        currencies = df["salary_currency"].unique()

        if len(currencies) == 0:
            print("Нет данных с валютой.")
            return

        for curr in currencies:
            curr_df = df[df["salary_currency"] == curr].copy()

            if curr_df.empty:
                continue

            curr_df["city"] = curr_df["city"].fillna("Не указано")

    
            def agg_city(g):
                combined = pd.concat([g["salary_from"].dropna(), g["salary_to"].dropna()])
                return pd.Series({
                    "min_salary": combined.min(skipna=True),
                    "mean_salary": g["salary_mean"].mean(skipna=True),
                    "max_salary": combined.max(skipna=True),
                    "count": len(g)
                })

            city_stats = curr_df.groupby("city").apply(agg_city)

            city_stats = city_stats.dropna(subset=["mean_salary"])
            city_stats = city_stats.sort_values("mean_salary", ascending=False).head(top_n)

            if city_stats.empty:
                continue

            plt.figure(figsize=(12, 6))
            plt.plot(city_stats.index, city_stats["min_salary"], marker="o", label="Min")
            plt.plot(city_stats.index, city_stats["mean_salary"], marker="o", label="Mean")
            plt.plot(city_stats.index, city_stats["max_salary"], marker="o", label="Max")

            plt.xticks(rotation=45, ha="right")
            plt.xlabel("Город")
            plt.ylabel(f"Зарплата ({curr})")
            plt.title(f"Статистика зарплат по городам ({curr}) - ТОП {top_n}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

