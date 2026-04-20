# Alex

Alex is an informational financial planning advisor SaaS built with Next.js, FastAPI, Clerk, OpenRouter, Terraform, GitHub Actions, and GCP.

## Structure

- `frontend/` Next.js application with Clerk auth
- `backend/` FastAPI API for portfolios, retirement planning, and AI analysis
- `terraform/` GCP infrastructure
- `.github/workflows/` CI/CD workflows

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- The backend auto-creates tables on startup for a minimal V1 workflow.
- Production deployment expects GCP Cloud Run and Cloud SQL.
- The app is informational and educational only, not a regulated advisory product.

