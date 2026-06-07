# HandwritOCR — Python Backend

## Quick Start

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

cp .env.example .env

# Run the server
uvicorn app.main:app --reload --port 8000
```

## With Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/samples/upload` | Upload handwriting samples |
| POST | `/api/generate` | Start handwriting generation |
| GET | `/api/download/{task_id}` | Download generated file |
| WS | `/ws/progress/{task_id}` | Real-time progress updates |

## Architecture

- **FastAPI** — Async REST API + WebSocket
- **OpenCV + Pillow** — Image processing & style extraction
- **ReportLab** — Server-side PDF generation
- **Celery + Redis** — Async task queue for generation jobs
- **Docker Compose** — Multi-container deployment
