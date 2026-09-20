# LegitsIQ-AI-Forecast

## Setup
```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

## Frontend
```bash
cd frontend && npm install && npm run dev
```

## Environment Variables
- `GROQ_API_KEY` — Free API key from https://console.groq.com
- `GROQ_MODEL` — Default: `openai/gpt-oss-120b`
