import os
import ast
import numpy as np
from fastapi import FastAPI, APIRouter,Body
from data_collector.scraper import Scraper
from database_manager.manager import DatabaseManager
from database_manager.embedder import EmbeddingsGenerator
from metrics_calculator.calculator import MetricsCalculator
from review_analyzer.analyzer import Analyzer
import pandas as pd

router = APIRouter()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
connection_string = (db_user, db_password, db_name, db_host, db_port)

db_manager = DatabaseManager(connection_string=connection_string)
embedder = EmbeddingsGenerator()
analyzer = Analyzer()
scraper = Scraper()
calculator = MetricsCalculator()


def serialize_insights(insights):
    serialized = []
    for insight in insights:
        serialized.append({
            "cluster_id": int(insight["cluster_id"]),            
            "size": int(insight["size"]),                        
            "percent": float(insight["percent"]),                
            "keywords": [str(k) for k in insight["keywords"]],   
            "examples": [str(e) for e in insight["examples"]]    
        })
    return serialized


@router.post("/generate")
def generate(payload: dict = Body(...)):
    app_id = int(payload.get("app_id"))
    country = str(payload.get("country"))
    results = scraper.scrape_from_id(app_id=app_id, country=country)
    if results.empty:
        return {"error": "No reviews fetched"}

    # Sentiment analysis
    sentiments = results["text"].apply(lambda t: analyzer.sentiment_analysis(t))
    results["sentiment_label"] = sentiments.apply(lambda x: x[0])
    results["sentiment_score"] = sentiments.apply(lambda x: x[1])

    # Embeddings
    embeddings = embedder.embed_texts(results["text"].tolist())
    results["embedding"] = embeddings

    # Load new data into DB
    db_manager.load_data(results)

    # Extract all data for metrics
    extracted_data = db_manager.extract_data()
    avg_rating = calculator.calculate_rating_avarage(extracted_data)
    rating_dist = calculator.calculate_rating_distribution(extracted_data)

    # Cluster negative reviews
    negative_reviews = extracted_data[extracted_data["sentiment_label"].isin(["Very Negative", "Negative"])]
    if not negative_reviews.empty:
        neg_texts = negative_reviews["text"].tolist()
        neg_embeddings = negative_reviews["embedding"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        ).tolist()
        labels = analyzer.generate_cluster_labels(np.array(neg_embeddings))
        insights = analyzer.generate_insights(neg_texts, labels)
    else:
        insights = []

    return {
        "avg_rating": float(avg_rating),
        "rating_distribution": {int(k): float(v) for k,v in rating_dist.items()},
        "negative_insights": serialize_insights(insights)
    }


@router.get("/download_reviews")
def download_reviews():
    extracted_data: pd.DataFrame = db_manager.extract_data()
    if "embedding" in extracted_data.columns:
        extracted_data = extracted_data.drop(columns=["embedding"])

    data = extracted_data.to_dict(orient="records")
    return {
        "count": len(data),
        "reviews": data
    }
