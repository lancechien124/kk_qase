"""
JMeter JMX Generation Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import tempfile
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.logging import logger
from app.models.user import User
from app.services.jmeter_parser import JMeterJMXGenerator
from app.schemas.jmeter import JMXGenerateRequest, JMXGenerateResponse

router = APIRouter()


@router.post("/generate-jmx", response_model=JMXGenerateResponse)
async def generate_jmx_from_scenario(
    request: JMXGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate JMX file from API scenario"""
    generator = JMeterJMXGenerator()
    
    try:
        jmx_content = generator.generate_jmx_from_api_scenario(
            scenario_name=request.scenario_name,
            api_definitions=request.api_definitions,
            thread_group_config=request.thread_group_config or {},
        )
        
        return JMXGenerateResponse(
            jmx_content=jmx_content,
            filename=f"{request.scenario_name}.jmx"
        )
    except Exception as e:
        logger.error(f"Error generating JMX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate JMX: {str(e)}"
        )


@router.post("/generate-jmx/download")
async def download_generated_jmx(
    request: JMXGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and download JMX file"""
    generator = JMeterJMXGenerator()
    
    try:
        jmx_content = generator.generate_jmx_from_api_scenario(
            scenario_name=request.scenario_name,
            api_definitions=request.api_definitions,
            thread_group_config=request.thread_group_config or {},
        )
        
        filename = f"{request.scenario_name}.jmx"
        
        return Response(
            content=jmx_content.encode('utf-8'),
            media_type="application/xml",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            }
        )
    except Exception as e:
        logger.error(f"Error generating JMX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate JMX: {str(e)}"
        )

