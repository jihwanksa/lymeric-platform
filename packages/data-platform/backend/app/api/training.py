"""ML Training API endpoints"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
import uuid

from app.core.database import get_db
from app.services.training_service import TrainingService, training_jobs, run_training_job

router = APIRouter()


class TrainingRequest(BaseModel):
    """Training configuration"""
    property: str  # tg, ffv, tc, density, rg
    method: str = 'basic'  # basic, optuna, autogluon
    n_estimators: Optional[int] = 100
    max_depth: Optional[int] = None
    min_samples_split: int = 2
    n_trials: Optional[int] = 50  # For Optuna
    time_limit: Optional[int] = 300  # For AutoGluon (seconds)


class TrainingResponse(BaseModel):
    """Training job response"""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Training job status"""
    job_id: str
    status: str  # pending, running, completed, failed
    result: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/start", response_model=TrainingResponse)
async def start_training(
    config: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a training job
    
    Methods:
    - basic: Random Forest with fixed hyperparameters
    - optuna: Random Forest with Optuna optimization (50 trials)
    - autogluon: AutoML with AutoGluon (5 min time limit)
    """
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job
    training_jobs[job_id] = {
        'status': 'pending',
        'config': config.dict()
    }
    
    # Start background training
    background_tasks.add_task(
        run_training_job,
        job_id,
        db,
        config.dict()
    )
    
    return TrainingResponse(
        job_id=job_id,
        status='pending',
        message=f'Training job started with {config.method} method'
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get training job status"""
    if job_id not in training_jobs:
        return JobStatusResponse(
            job_id=job_id,
            status='not_found'
        )
    
    job = training_jobs[job_id]
    
    # Extract result without model object (not JSON serializable)
    result = None
    if job['status'] == 'completed' and 'result' in job:
        result = {k: v for k, v in job['result'].items() if k not in ['model', 'predictor']}
    
    return JobStatusResponse(
        job_id=job_id,
        status=job['status'],
        result=result,
        error=job.get('error')
    )
