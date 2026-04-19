"""
Main FastAPI application entrypoint.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api import assessment, documents, evaluation, reports
from app.retrieval.ingestion import get_collection_stats

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Governance Risk Classifier API",
    description="A compliance decision-support API for evaluating AI use cases against EU AI Act and GDPR.",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assessment.router, prefix="/api", tags=["Assessment"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.on_event("startup")
async def startup_event():
    """Run verification checks on startup."""
    print("Starting AI Governance Risk Classifier...")
    stats = get_collection_stats()
    print(f"Vector Database Stats: {stats}")
    if stats.get("total_chunks", 0) == 0:
        print("Warning: Vector database is empty. Please trigger document ingestion.")


@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "online",
        "service": "AI Governance Risk Classifier",
        "message": "Welcome to the API. Access /docs for Swagger documentation."
    }
