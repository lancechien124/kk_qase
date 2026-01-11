"""
JMeter Schemas
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class JMXGenerateRequest(BaseModel):
    """Request to generate JMX file"""
    scenario_name: str
    api_definitions: List[Dict[str, Any]]
    thread_group_config: Optional[Dict[str, Any]] = None


class JMXGenerateResponse(BaseModel):
    """Response with generated JMX content"""
    jmx_content: str
    filename: str


class JMeterExecutionRequest(BaseModel):
    """Request to execute JMeter script"""
    jmx_file_path: str
    properties: Optional[Dict[str, str]] = None
    environment: Optional[Dict[str, str]] = None


class JMeterExecutionResponse(BaseModel):
    """Response from JMeter execution"""
    success: bool
    execution_id: str
    results: Dict[str, Any]
    jtl_file: Optional[str] = None
    html_report: Optional[str] = None

