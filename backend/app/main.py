import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, institution, evidence, blockchain, audit, feedback, anomalies, scores, dashboard

Base.metadata.create_all(bind=engine)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app = FastAPI(
    title="BlockAccred API",
    description="Academic Prototype - Not an Official NBA System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(institution.router)
app.include_router(evidence.router)
app.include_router(blockchain.router)
app.include_router(audit.router)
app.include_router(feedback.router)
app.include_router(anomalies.router)
app.include_router(scores.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"app": "BlockAccred", "label": "Academic Prototype - Not an Official NBA System", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
