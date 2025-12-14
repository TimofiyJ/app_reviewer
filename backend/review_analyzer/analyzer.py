import requests
import json
import hdbscan
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from itertools import chain
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_distances


class Analyzer:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.sentiment_pipe = pipeline(
            "text-classification", 
            model="tabularisai/multilingual-sentiment-analysis",
            truncation=True,
            max_length=512
        )

    def sentiment_analysis(self, text):
        result = self.sentiment_pipe(text)[0] 
        sentiment = result["label"]
        score = float(result["score"])
        return sentiment, score

    def generate_cluster_labels(self, embeddings):
        distance_matrix = cosine_distances(embeddings)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=3,
            metric="precomputed"
        )
        labels = clusterer.fit_predict(distance_matrix)
        return labels

    def extract_keywords(self, texts, top_n=5, ngram_range=(1,3)):
        """
        Extract top-N keywords/phrases from a list of texts using embeddings.
        
        texts: List[str] - input reviews
        top_n: int - number of keywords
        ngram_range: tuple - min and max n-grams
        """
        if not texts:
            return []

        # 1. Build candidate phrases 
        candidates = set()
        for text in texts:
            words = text.lower().split()
            for n in range(ngram_range[0], ngram_range[1]+1):
                candidates.update([" ".join(words[i:i+n]) for i in range(len(words)-n+1)])

        candidates = list(candidates)

        # 2. Encode full text (cluster-level embedding)
        cluster_embedding = self.model.encode([" ".join(texts)], convert_to_numpy=True)

        # 3. Encode candidate phrases
        candidate_embeddings = self.model.encode(candidates, convert_to_numpy=True)

        # 4. Compute similarity (cosine)
        candidate_embeddings /= np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
        cluster_embedding /= np.linalg.norm(cluster_embedding, axis=1, keepdims=True)
        sims = candidate_embeddings @ cluster_embedding.T
        sims = sims.flatten()

        # 5. Pick top-N
        top_indices = sims.argsort()[::-1][:top_n]
        keywords = [candidates[i] for i in top_indices]
        return keywords

    def generate_insights(self, reviews, labels, top_n_keywords=5, top_n_examples=3):
        insights = []
        total_reviews = len(reviews)
        for cluster_id in set(labels):
            if cluster_id == -1:
                continue
            cluster_reviews = [r for r, l in zip(reviews, labels) if l == cluster_id]
            cluster_size = len(cluster_reviews)
            cluster_pct = cluster_size / total_reviews * 100
            keywords = self.extract_keywords(cluster_reviews, top_n=top_n_keywords)
            example_reviews = cluster_reviews[:top_n_examples]
            insights.append({
                "cluster_id": cluster_id,
                "size": cluster_size,
                "percent": round(cluster_pct, 2),
                "keywords": keywords,
                "examples": example_reviews
            })
        return insights


if __name__ == "__main__":
    a = Analyzer()
    print(a.sentiment_analysis("I love tennis"))
