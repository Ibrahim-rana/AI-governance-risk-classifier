"""
FastAPI router for evaluation module.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import os

from ..evaluation.evaluator import run_evaluation, EvaluationResult

router = APIRouter()

# Store latest evaluation
_latest_eval = None


@router.post("/run", response_model=EvaluationResult)
async def trigger_evaluation(run_baseline: bool = True):
    """Run the evaluation pipeline against the 20-case dataset."""
    global _latest_eval
    try:
        from ..evaluation.evaluator import load_dataset
        dataset = load_dataset()
        if not dataset:
            raise HTTPException(status_code=404, detail="Evaluation dataset not found")
            
        result = run_evaluation(dataset, run_baseline=run_baseline)
        _latest_eval = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/results", response_model=EvaluationResult)
async def get_latest_results():
    """Get the latest evaluation results without running again."""
    if _latest_eval is None:
        raise HTTPException(status_code=404, detail="No evaluation has been run yet")
    return _latest_eval
