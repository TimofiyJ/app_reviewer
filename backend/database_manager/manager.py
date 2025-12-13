import pandas as pd
import os
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, Text, Date, String, Float
)
from pgvector.sqlalchemy import Vector

class DatabaseManager:
    def __init__(self, connection_string, vector_dim: int = 384):
        db_user, db_password, db_name, db_host, db_port = connection_string
        self.engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        self.metadata = MetaData()
        self.vector_dim = vector_dim
        self.reviews_table = Table(
            "reviews",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("app_id", Integer, nullable=True),
            Column("title", Text, nullable=True),
            Column("text", Text, nullable=True),
            Column("rating", Integer, nullable=True),
            Column("review_date", Date, nullable=True),
            Column("author_id", String, nullable=True),
            Column("sentiment_label", String, nullable=True),
            Column("sentiment_score", Float, nullable=True),
            Column("embedding", Vector(self.vector_dim), nullable=True),
            extend_existing=True,
        )
        self.metadata.create_all(self.engine)

    def load_data(self, data: pd.DataFrame, table="reviews"):
        if data.empty:
            return 0  # nothing to insert

        # 1. Extract existing reviews for the same app_ids
        app_ids = data["app_id"].unique().tolist()
        query = f"""
            SELECT app_id, author_id
            FROM {table}
            WHERE app_id IN %(app_ids)s
        """
        existing = pd.read_sql(query, self.engine, params={"app_ids": tuple(app_ids)})

        # 2. Filter out duplicates
        if not existing.empty:
            merged = data.merge(
                existing,
                on=["app_id", "author_id"],
                how="left",
                indicator=True
            )
            data_to_insert = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
        else:
            data_to_insert = data

        # 3. Insert only new reviews
        if not data_to_insert.empty:
            data_to_insert.to_sql(table, self.engine, if_exists="append", index=False)
            return len(data_to_insert)
        else:
            return 0

    def extract_data(self, table: str = "reviews") -> pd.DataFrame:
        query = f"""
            SELECT 
                id,
                app_id,
                title,
                text,
                rating,
                review_date,
                author_id,
                sentiment_label,
                sentiment_score,
                embedding
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
