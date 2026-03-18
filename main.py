from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import Base, engine, seed_demo_data
from routes import router


app = FastAPI(
    title="Build Web App API",
    version="1.0.0",
    description="Turn rough product ideas into traceable, reusable planning briefs in minutes.",
)

Base.metadata.create_all(bind=engine)
seed_demo_data()


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <title>Build Web App API</title>
      <style>
        body { background:#0b1020; color:#e6ecff; font-family:Inter,Arial,sans-serif; margin:0; padding:24px; }
        .card { background:#141a2f; border:1px solid #283252; border-radius:12px; padding:16px; margin-bottom:16px; }
        h1,h2 { margin:0 0 12px 0; }
        a { color:#8ab4ff; }
        code { background:#1d2542; padding:2px 6px; border-radius:6px; }
        ul { line-height:1.7; }
      </style>
    </head>
    <body>
      <div class='card'>
        <h1>Build Web App API</h1>
        <p>Turn rough product ideas into traceable, reusable planning briefs in minutes.</p>
      </div>
      <div class='card'>
        <h2>Endpoints</h2>
        <ul>
          <li><code>GET /health</code></li>
          <li><code>POST /plan</code> and <code>POST /api/plan</code></li>
          <li><code>POST /insights</code> and <code>POST /api/insights</code></li>
          <li><code>GET /dossiers</code> and <code>GET /api/dossiers</code></li>
          <li><code>GET /dossiers/{artifact_id}</code> and <code>GET /api/dossiers/{artifact_id}</code></li>
        </ul>
      </div>
      <div class='card'>
        <h2>Tech Stack</h2>
        <p>FastAPI + SQLAlchemy + PostgreSQL-ready models + DigitalOcean Serverless Inference (anthropic-claude-4.6-sonnet).</p>
        <p><a href='/docs'>OpenAPI Docs</a> · <a href='/redoc'>ReDoc</a></p>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
