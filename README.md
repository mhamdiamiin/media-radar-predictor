# TanitWeb Media Radar

TanitWeb Media Radar collects news articles from Mosaique FM, enriches them with NLP, groups related stories, scores emerging trends, and exposes the results through an API and dashboard.

## Project layout

- `run_pipeline.py`: scheduled ingestion and analysis pipeline.
- `app/`: scraping, NLP, clustering, scoring, and alert logic.
- `api test/main.py`: lightweight FastAPI API used by the React dashboard.
- `backend/main.py`: alternate FastAPI API with `/api/...` routes.
- `frontend/`: main React/Vite frontend.
- `dashboard/`: Streamlit dashboard prototype kept for testing and reference.

## Requirements

- Python 3.10 or newer
- Node.js 20 or newer for the frontend
- A running MongoDB instance, locally or remotely
- A Mistral API key for category classification and score review

The NLP models download the first time they are used. The French spaCy model must be installed separately.

## Python setup

From the repository root in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download fr_core_news_md
```

If PowerShell blocks activation, run the commands from an activated terminal or use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the repository root:

```dotenv
MONGODB_URL=mongodb://localhost:27017/
MISTRAL_API_KEY=your_mistral_api_key
```

The default database is `media_radar`. The application uses the `articles` and `alerts` collections. Do not commit `.env` or API keys.

## Run the Python services

Start the scheduled ingestion and analysis pipeline:

```powershell
python run_pipeline.py
```

Run the Streamlit dashboard prototype when needed for testing:

```powershell
streamlit run dashboard/app.py
```

Run the lightweight API used by the main `frontend/`:

```powershell
python "api test/main.py"
```

It listens on `http://localhost:8000` and provides `/stats`, `/articles`, and `/alerts`.

The alternate API can be started with:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Its endpoints are under `/api`, including `/api/stats`, `/api/articles`, `/api/alerts`, and `/api/clusters`.

## Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`. Start the API before opening the frontend. The `frontend/` directory contains its `package-lock.json`, so use `npm install` there.

## Processing flow

1. Fetch new article URLs from the Mosaique FM sitemap.
2. Scrape pending article pages and store their metadata in MongoDB.
3. Run sentiment analysis, keyword extraction, entity recognition, and multilingual embeddings.
4. Cluster related articles and classify repeated or emerging topics.
5. Calculate trend scores and optionally review them with Mistral.
6. Create alerts for articles above the configured trend threshold.

Thresholds and source settings live in `app/config.py`.

## Notes

- The pipeline uses external Mosaique FM, Hugging Face, Google Trends, and Mistral services.
- The first NLP run can be slow because model files are downloaded and loaded locally.
- MongoDB must be reachable before importing modules that initialize the database connection.
- The Streamlit dashboard is a prototype and reads MongoDB directly. The main React frontend reads from the API.
