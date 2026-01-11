"""
JMeter Integration Endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import os
import tempfile
import shutil

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.jmeter_service import JMeterService
from app.services.file_service import FileService
from app.core.kafka import notify_test_execution_result

router = APIRouter()


@router.post("/execute")
async def execute_jmeter(
    jmx_file: UploadFile = File(...),
    properties: Optional[Dict[str, str]] = None,
    environment: Optional[Dict[str, str]] = None,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute JMeter script"""
    jmeter_service = JMeterService()
    file_service = FileService()
    
    # Save uploaded JMX file temporarily
    temp_dir = tempfile.mkdtemp()
    jmx_file_path = os.path.join(temp_dir, jmx_file.filename)
    
    try:
        # Validate file type
        if not jmx_file.filename.endswith('.jmx'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be JMeter script (.jmx)"
            )
        
        # Save file
        content = await jmx_file.read()
        with open(jmx_file_path, 'wb') as f:
            f.write(content)
        
        # Validate JMX file
        validation = await jmeter_service.validate_jmx_file(jmx_file_path)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JMX file: {validation.get('error', 'Unknown error')}"
            )
        
        # Execute JMeter
        result = await jmeter_service.execute_jmeter_script(
            jmx_file_path=jmx_file_path,
            output_dir=temp_dir,
            properties=properties,
            environment=environment,
        )
        
        # Send notification
        if background_tasks:
            background_tasks.add_task(
                notify_test_execution_result,
                test_id=jmx_file.filename,
                test_type="jmeter",
                status="success" if result["success"] else "failed",
                result=result.get("parsed_results", {}),
                project_id=None,
            )
        
        # Cleanup temporary files in background
        if background_tasks:
            background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        
        return {
            "success": result["success"],
            "execution_id": jmx_file.filename,
            "results": result.get("parsed_results", {}),
            "jtl_file": result.get("jtl_file"),
            "html_report": result.get("html_report"),
        }
    except HTTPException:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.error(f"Error executing JMeter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute JMeter: {str(e)}"
        )


@router.post("/parse-jmx")
async def parse_jmx_file(
    jmx_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Parse JMX file to extract test plan information"""
    jmeter_service = JMeterService()
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    jmx_file_path = os.path.join(temp_dir, jmx_file.filename)
    
    try:
        content = await jmx_file.read()
        with open(jmx_file_path, 'wb') as f:
            f.write(content)
        
        # Parse JMX
        result = await jmeter_service.parse_jmx_file(jmx_file_path)
        
        return result
    except Exception as e:
        logger.error(f"Error parsing JMX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse JMX: {str(e)}"
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/validate-jmx")
async def validate_jmx(
    jmx_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate JMX file"""
    jmeter_service = JMeterService()
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    jmx_file_path = os.path.join(temp_dir, jmx_file.filename)
    
    try:
        content = await jmx_file.read()
        with open(jmx_file_path, 'wb') as f:
            f.write(content)
        
        # Validate
        result = await jmeter_service.validate_jmx_file(jmx_file_path)
        
        return result
    except Exception as e:
        logger.error(f"Error validating JMX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate JMX: {str(e)}"
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/parse-jtl")
async def parse_jtl_file(
    jtl_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Parse JTL result file"""
    jmeter_service = JMeterService()
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    jtl_file_path = os.path.join(temp_dir, jtl_file.filename)
    
    try:
        content = await jtl_file.read()
        with open(jtl_file_path, 'wb') as f:
            f.write(content)
        
        # Parse JTL
        result = await jmeter_service.parse_jtl_file(jtl_file_path)
        
        return result
    except Exception as e:
        logger.error(f"Error parsing JTL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse JTL: {str(e)}"
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

