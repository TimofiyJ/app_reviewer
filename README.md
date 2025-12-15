# Review analysis test task

## How to run
1. Navigate to backend folder `cd backend`
2. Create `.env` file and fill the values based on `example.env`
3. Run `docker compose build --no-cache && docker compose up -d`

## Explanation of the solution
The solution consists of 5 modules:
- data_collector: scraper that uses SerpAPI to get reviews for specified App id from App Store. This external API is chosen for its reliability, free trial. Apify API was considered, but it has limited availability for free usage that doesn't include API calls
- database_manager: separate module that is responsible for processing and doing I/O operations for database (PostgreSQL + pgvector). Database is added to be able to store the reviews and analyze them in perspective with even bigger functionalities. Embedder is separate class that is responsible just for embedding. Database  manager performs additional check during loading operation to not collect duplicates
- metrics_calculator: module responsible for calculating rating avarage and distribution
- review_analyzer: performs sentiment analysis using `tabularisai/multilingual-sentiment-analysis` model from HuggingFace, embeds the reviews and creates clusters to allow gather more insight information and find potential connections between reviews (for example, 20% of bad reviews are connected to login functionality, other 30% is payment, etc.), after clusters are computed we extract keywords based on cosine similarity of their embeddings to embedded cluster (full text)
- app: backend based on FastAPI.

## TODO:
- Input parameters validation for endpoints and methods of classes
- Add LLM actionable insight (and key phrase extraction)
- Make clustering optional
- Make visualization of results using Streamlit
