import pandas as pd
import os
from sqlalchemy import create_engine

class DatabaseManager:
    def __init__(self, connection_string):
        db_user, db_password, db_name, db_host, db_port = connection_string
        self.engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')


    def load_data(self, data: pd.DataFrame, table="reviews"):
        return data.to_sql(table, self.engine, if_exists='append', index=False)

    def extract_data(self, table="reviews"):
        query = f"""
            SELECT 
                app_id,
                title,
                text,
                rating,
                review_date,
                author_id
            FROM {table};
        """
        return pd.read_sql(query, self.engine)

if __name__ == "__main__":
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_USER")
    db_host = os.getenv("DB_USER")
    db_port = os.getenv("DB_USER")
    connection_string = (db_user, db_password, db_name, db_host, db_port)
    db_manager = DatabaseManager(connection_string=connection_string)
