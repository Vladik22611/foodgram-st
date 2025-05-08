import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os


def check_table_empty(conn):
    """Проверяет, пуста ли таблица ingredient"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM recipes_ingredient")
        return cur.fetchone()[0] == 0


def load_ingredients():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        # Загружаем данные только если таблица пуста
        if check_table_empty(conn):
            # Чтение JSON
            df = pd.read_json("/app/data/ingredients.json")

            # Подготовка данных
            data = [(row["name"], row["measurement_unit"]) for _,
                    row in df.iterrows()]

            # Быстрая вставка
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    "INSERT INTO recipes_ingredient (name, measurement_unit) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    data,
                )
                conn.commit()

            print(f"Добавлено {len(data)} записей")
        else:
            print("Таблица уже содержит данные, пропускаем заполнение")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    load_ingredients()
