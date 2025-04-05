from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from app.core.xai.shap_explainer import SHAPExplainer
from app.schemas.explanation import ExplanationRequest, ExplanationResponse
from app.tasks.explanations import generate_explanation
from loguru import logger

router = APIRouter()

@router.post("/explain", response_model=ExplanationResponse)
async def explain_prediction(
    request: ExplanationRequest,
    background_tasks: BackgroundTasks
):
    """Generate model explanations using specified XAI methods."""
    try:
        # Start async explanation task
        task = generate_explanation.delay(
            model_name=request.model_name,
            data_id=request.data_id,
            instance_index=request.instance_index,
            methods=request.methods
        )
        
        return ExplanationResponse(
            task_id=task.id,
            status="processing",
            message="Explanation generation started"
        )
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=ExplanationResponse)
async def get_explanation_status(task_id: str):
    """Get the status of an explanation generation task."""
    try:
        task = generate_explanation.AsyncResult(task_id)
        
        if task.ready():
            if task.successful():
                return ExplanationResponse(
                    task_id=task_id,
                    status="completed",
                    result=task.get()
                )
            else:
                return ExplanationResponse(
                    task_id=task_id,
                    status="failed",
                    message=str(task.result)
                )
        
        return ExplanationResponse(
            task_id=task_id,
            status="processing",
            message="Explanation generation in progress"
        )
    except Exception as e:
        logger.error(f"Error checking explanation status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
