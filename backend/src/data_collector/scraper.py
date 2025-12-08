import os
import uuid
from datetime import date

import pandas as pd
import serpapi
from dotenv import load_dotenv
load_dotenv(dotenv_path="/Users/tim/Desktop/test_task/backend/src/.env", override=True)


class Scraper:
    def __init__(self):
        pass
        
    def scrape_from_id(self, app_id, country):
        # TODO: add parameters validation
        params = {
        "engine": "apple_reviews",
        "product_id": app_id,
        "country": country,
        "api_key": os.getenv("SERP_API")
        }

        search = serpapi.search(params)
        processed_results = self.preprocess_data(search, app_id)
        return processed_results

    def scrape_from_url(self, url, country, until, max_items):
        pass

    def preprocess_data(self, data, app_id):
        # TODO: add clustering in insights generation
        # TODO: add unique checks and edit check to collect and store only unique reviews
        if data.get("search_metadata").get("status") != "Success":
            return "Error"
        reviews = data.get("reviews")
        dataset = pd.DataFrame(columns=["app_id", "title","text", "rating", "review_date", "author_id"])
        for review in reviews:
            new_row = {
                "app_id": app_id,
                "title": review.get("title"),
                "text": review.get("text"),
                "rating": review.get("rating"),
                "review_date": review.get("review_date"),
                "author_id": review.get("author").get("author_id")
            }
            dataset.loc[len(dataset)] = new_row
        return dataset

if __name__ == "__main__":
    scraper = Scraper()
    results = scraper.scrape_from_id(app_id=284882215, country="us")
    print(results)