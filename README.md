# NYC 311 Analytics Agent

AI-powered analytics over NYC 311 service request data. This project provides a web UI (React + Vite) and API (FastAPI) with streaming chat so you can ask questions about the dataset in natural language.

---

## Prerequisites

- **Python 3.12**
- **Node.js** (18+ or 22 recommended; frontend Docker uses Node 22)
- **DeepSeek API key** (used by the backend for the LLM)
- **NYC 311 dataset**: CSV file `311_Service_Requests_from_2010_to_Present.csv` (see [Where to get the data](#where-to-get-the-data) below)

---

## Quick start

1. **Backend**: From the project root, run:
   ```bash
   cd backend
   python -m venv venv
   ```
   Activate the venv: **Windows** `.\venv\Scripts\activate` (or `venv\Scripts\activate.bat`), **macOS/Linux** `source venv/bin/activate`. Then:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```
   Edit `.env` and set `DEEPSEEK_API_KEY` and `DATA_PATH` (path to the 311 CSV). Then:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

2. **Frontend**: In a new terminal, from the project root:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

All backend commands (uvicorn, pytest) must be run from the **backend/** directory. All frontend commands must be run from the **frontend/** directory so paths and modules resolve correctly.

---

## Backend setup and run

**Directory**: `backend/`

### 1. Create and activate virtual environment

```bash
python -m venv venv
```

- **Windows**: `.\venv\Scripts\activate` or `venv\Scripts\activate.bat`
- **macOS/Linux**: `source venv/bin/activate`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment variables

- Copy `backend/.env.example` to `backend/.env`.
- **Required**:
  - `DEEPSEEK_API_KEY` – your DeepSeek API key for the LLM.
  - `DATA_PATH` – path to the 311 CSV (absolute or relative to the backend directory). Example: `DATA_PATH=./data/311_Service_Requests_from_2010_to_Present.csv`
- **Optional**: `LOG_LEVEL=INFO` (default).

Relative paths in `DATA_PATH` are resolved from the **backend** directory.

### 4. Data

Create a `data/` folder (e.g. under `backend/`), place `311_Service_Requests_from_2010_to_Present.csv` there, and set `DATA_PATH` in `.env` to point to it.

### 5. Run the backend

- **Local dev with frontend** (recommended): start on port **8001** so the frontend dev proxy works:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8001
  ```
  The frontend proxies `/api` to `http://localhost:8001`.

- **Backend only / API docs**: 
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
  Then open [http://localhost:8000/docs](http://localhost:8000/docs).

### Optional: Docker (backend)

From `backend/`:

```bash
docker build -t nyc311-backend .
```

Run with port mapping and env (and ensure the container can access the CSV, e.g. mount a volume or set `DATA_PATH` to a path inside the container):

```bash
docker run -p 8001:8000 -e DEEPSEEK_API_KEY=your_key -e DATA_PATH=/app/data/dataset.csv -v /path/to/your/data:/app/data nyc311-backend
```

The default CMD uses port 8000 inside the container.

---

## Frontend setup and run

**Directory**: `frontend/`

### 1. Install dependencies

```bash
npm install
```

### 2. Run

- **Dev**: `npm run dev` – Vite runs on port **3000**. Ensure the backend is running on **8001** so `/api` is proxied.
- **Build**: `npm run build` – output in `dist/`.
- **Preview**: `npm run preview` – test the production build locally (may not proxy to backend unless configured).

### Optional: Docker (frontend)

From `frontend/`:

```bash
docker build -t nyc311-frontend .
```

The production image uses nginx and proxies `/api` to `http://backend:8000`. For a full stack you would run both containers (e.g. with Docker Compose or a shared network) with the backend service named `backend`.

---

## Running the full app locally

1. Start the backend (from `backend/`): `uvicorn app.main:app --host 0.0.0.0 --port 8001`
2. Start the frontend (from `frontend/`): `npm run dev`
3. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment variables reference

### Backend

| Variable           | Required | Description                                              |
| ------------------ | -------- | -------------------------------------------------------- |
| `DEEPSEEK_API_KEY` | Yes      | DeepSeek API key for the LLM.                            |
| `DATA_PATH`        | Yes      | Path to `311_Service_Requests_from_2010_to_Present.csv`.  |
| `LOG_LEVEL`        | No       | e.g. `INFO` (default).                                   |

**Optional/advanced**: Other settings in `backend/app/config.py` (e.g. `CORS_ORIGINS`, `LLM_MODEL`, `LLM_TEMPERATURE`) can be overridden via environment variables if needed.

### Frontend

No environment variables are required for local dev; the API is at `/api` and is proxied to the backend.

---

## Project structure

- **backend/** – FastAPI app (`app/main.py`), DuckDB loader, agent, API routes under `/api` (e.g. `/api/health`, `/api/chat`).
- **frontend/** – Vite + React app; dev server on port 3000, proxy `/api` to backend.

---

## API docs

When the backend is running, Swagger UI is available at:

- [http://localhost:8001/docs](http://localhost:8001/docs) (when using port 8001 for local dev)
- [http://localhost:8000/docs](http://localhost:8000/docs) (when using port 8000)

---

## Port summary

| Service                    | Port |
| -------------------------- | ---- |
| Backend (local dev + frontend) | 8001 |
| Backend (Docker / standalone)  | 8000 (inside container or when not using frontend proxy) |
| Frontend dev                  | 3000 |
| Frontend production (Docker nginx) | 80   |

---

## Testing (backend)

From `backend/`:

```bash
pytest
```

For verbose output: `pytest -v`.

Requires dependencies from `backend/requirements.txt` (pytest, pytest-asyncio). Tests are in `backend/tests/` (e.g. `test_api.py`, `test_db.py`, `test_agent.py`).

---

## Troubleshooting

- **"Backend unavailable" in the UI** – The backend is not running, or the frontend proxy target is wrong. Ensure the backend is on **port 8001** when using `npm run dev` (see `frontend/vite.config.ts`).

- **"Database not loaded. Check server logs." in chat** – The backend started but the dataset was not found. The app still runs (the lifespan in `backend/app/main.py` catches `FileNotFoundError`). Fix: set `DATA_PATH` in `.env` to the correct path to `311_Service_Requests_from_2010_to_Present.csv` (relative to the backend directory or absolute), restart the backend, and check logs for "Dataset not found at ...".

- **Health check** – `GET /api/health` returns `db_connected` and `rows_loaded`. If `db_connected` is false, the dataset failed to load.

---

## Where to get the data

The backend expects the NYC 311 service requests dataset as a CSV file named **311_Service_Requests_from_2010_to_Present.csv**. You can obtain it from [NYC Open Data](https://opendata.cityofnewyork.us/) (search for "311 Service Requests"). Download the CSV and place it where `DATA_PATH` in your `.env` points (e.g. `backend/data/`). The file can be large; ensure you have enough disk space.

---

## Screenshots

Screenshots of the application are in the `screenshots/` folder. If you prefer not to commit screenshots, add `screenshots/` to `.gitignore`.

---

## Optional: Docker Compose

If you add a `docker-compose.yml` (e.g. backend on port 8000, frontend nginx proxying `/api` to `backend:8000`), you can document: `docker-compose up --build` and a one-line description of the services.
