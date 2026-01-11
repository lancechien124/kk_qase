"""
JMeter Service for script execution and result parsing
"""
import subprocess
import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import asyncio

from app.core.config import settings
from app.core.logging import logger


class JMeterService:
    """JMeter execution service"""
    
    def __init__(self):
        self.jmeter_home = settings.JMETER_HOME
        self.jmeter_bin = os.path.join(self.jmeter_home, "bin", "jmeter")
        self._validate_jmeter_installation()
    
    def _validate_jmeter_installation(self):
        """Validate JMeter installation"""
        if not os.path.exists(self.jmeter_home):
            logger.warning(f"JMeter home not found: {self.jmeter_home}")
        if not os.path.exists(self.jmeter_bin):
            logger.warning(f"JMeter binary not found: {self.jmeter_bin}")
    
    async def execute_jmeter_script(
        self,
        jmx_file_path: str,
        output_dir: Optional[str] = None,
        jtl_output: Optional[str] = None,
        log_output: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute JMeter script
        
        Args:
            jmx_file_path: Path to JMX file
            output_dir: Output directory for results
            jtl_output: Path to JTL output file
            log_output: Path to log output file
            properties: JMeter properties to set
            environment: Environment variables
        
        Returns:
            Dict with execution result
        """
        try:
            # Create temporary directory if not provided
            if not output_dir:
                output_dir = tempfile.mkdtemp()
            
            # Set default JTL and log paths
            if not jtl_output:
                jtl_output = os.path.join(output_dir, "result.jtl")
            if not log_output:
                log_output = os.path.join(output_dir, "jmeter.log")
            
            # Build JMeter command
            cmd = [
                self.jmeter_bin,
                "-n",  # Non-GUI mode
                "-t", jmx_file_path,  # Test plan file
                "-l", jtl_output,  # Log file (JTL)
                "-j", log_output,  # JMeter log file
                "-e",  # Generate HTML report
                "-o", os.path.join(output_dir, "html_report"),  # HTML report output
            ]
            
            # Add properties
            if properties:
                for key, value in properties.items():
                    cmd.extend(["-J", f"{key}={value}"])
            
            # Set environment variables
            env = os.environ.copy()
            if environment:
                env.update(environment)
            
            # Execute JMeter (run in executor to avoid blocking)
            logger.info(f"Executing JMeter: {' '.join(cmd)}")
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    cwd=self.jmeter_home,
                )
            )
            
            stdout, stderr = await loop.run_in_executor(
                None,
                process.communicate
            )
            
            # Parse results
            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "jtl_file": jtl_output if os.path.exists(jtl_output) else None,
                "log_file": log_output if os.path.exists(log_output) else None,
                "html_report": os.path.join(output_dir, "html_report") if os.path.exists(os.path.join(output_dir, "html_report")) else None,
            }
            
            # Parse JTL file if exists
            if result["jtl_file"]:
                result["parsed_results"] = await self.parse_jtl_file(result["jtl_file"])
            
            return result
        except Exception as e:
            logger.error(f"Error executing JMeter: {e}")
            raise
    
    async def parse_jtl_file(self, jtl_file_path: str) -> Dict[str, Any]:
        """
        Parse JMeter JTL result file
        
        Args:
            jtl_file_path: Path to JTL file
        
        Returns:
            Parsed results dictionary
        """
        try:
            results = {
                "total_samples": 0,
                "success_count": 0,
                "error_count": 0,
                "total_time": 0,
                "min_response_time": float('inf'),
                "max_response_time": 0,
                "avg_response_time": 0,
                "samples": [],
            }
            
            if not os.path.exists(jtl_file_path):
                return results
            
            # Parse JTL file (CSV format)
            with open(jtl_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Skip header if present
                start_idx = 0
                if lines and 'timeStamp' in lines[0]:
                    start_idx = 1
                
                for line in lines[start_idx:]:
                    if not line.strip():
                        continue
                    
                    # Parse CSV line
                    parts = line.strip().split(',')
                    if len(parts) < 5:
                        continue
                    
                    try:
                        timestamp = int(parts[0])
                        elapsed = int(parts[1])
                        label = parts[2]
                        response_code = parts[3]
                        response_message = parts[4] if len(parts) > 4 else ""
                        success = response_code.startswith('2') or response_code == "200"
                        
                        results["total_samples"] += 1
                        if success:
                            results["success_count"] += 1
                        else:
                            results["error_count"] += 1
                        
                        results["total_time"] += elapsed
                        results["min_response_time"] = min(results["min_response_time"], elapsed)
                        results["max_response_time"] = max(results["max_response_time"], elapsed)
                        
                        results["samples"].append({
                            "timestamp": timestamp,
                            "elapsed": elapsed,
                            "label": label,
                            "response_code": response_code,
                            "response_message": response_message,
                            "success": success,
                        })
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing JTL line: {line}, error: {e}")
                        continue
            
            # Calculate average
            if results["total_samples"] > 0:
                results["avg_response_time"] = results["total_time"] / results["total_samples"]
                results["success_rate"] = results["success_count"] / results["total_samples"]
                results["error_rate"] = results["error_count"] / results["total_samples"]
            else:
                results["avg_response_time"] = 0
                results["success_rate"] = 0
                results["error_rate"] = 0
            
            if results["min_response_time"] == float('inf'):
                results["min_response_time"] = 0
            
            return results
        except Exception as e:
            logger.error(f"Error parsing JTL file: {e}")
            raise
    
    async def generate_jmx_from_api_scenario(
        self,
        scenario_id: str,
        project_id: str,
        environment_id: Optional[str] = None,
    ) -> str:
        """
        Generate JMX file from API scenario
        
        Args:
            scenario_id: API scenario ID
            project_id: Project ID
            environment_id: Optional environment ID
        
        Returns:
            Path to generated JMX file
        """
        # TODO: Implement JMX generation from API scenario
        # This should convert ApiScenario to JMeter TestPlan XML
        # For now, return a placeholder
        raise NotImplementedError("JMX generation from API scenario not yet implemented")
    
    async def parse_jmx_file(self, jmx_file_path: str) -> Dict[str, Any]:
        """
        Parse JMX file to extract test plan information
        
        Args:
            jmx_file_path: Path to JMX file
        
        Returns:
            Parsed JMX information
        """
        try:
            tree = ET.parse(jmx_file_path)
            root = tree.getroot()
            
            # Extract test plan information
            test_plan = root.find('.//TestPlan')
            if test_plan is None:
                raise ValueError("Invalid JMX file: TestPlan not found")
            
            result = {
                "test_plan_name": test_plan.get("testname", ""),
                "thread_groups": [],
                "samplers": [],
            }
            
            # Extract thread groups
            thread_groups = root.findall('.//ThreadGroup')
            for tg in thread_groups:
                tg_info = {
                    "name": tg.get("testname", ""),
                    "num_threads": tg.find(".//stringProp[@name='ThreadGroup.num_threads']").text if tg.find(".//stringProp[@name='ThreadGroup.num_threads']") is not None else "1",
                    "ramp_time": tg.find(".//stringProp[@name='ThreadGroup.ramp_time']").text if tg.find(".//stringProp[@name='ThreadGroup.ramp_time']") is not None else "1",
                }
                result["thread_groups"].append(tg_info)
            
            # Extract HTTP samplers
            http_samplers = root.findall('.//HTTPSamplerProxy')
            for sampler in http_samplers:
                sampler_info = {
                    "name": sampler.get("testname", ""),
                    "domain": sampler.find(".//stringProp[@name='HTTPSampler.domain']").text if sampler.find(".//stringProp[@name='HTTPSampler.domain']") is not None else "",
                    "path": sampler.find(".//stringProp[@name='HTTPSampler.path']").text if sampler.find(".//stringProp[@name='HTTPSampler.path']") is not None else "",
                    "method": sampler.find(".//stringProp[@name='HTTPSampler.method']").text if sampler.find(".//stringProp[@name='HTTPSampler.method']") is not None else "GET",
                }
                result["samplers"].append(sampler_info)
            
            return result
        except Exception as e:
            logger.error(f"Error parsing JMX file: {e}")
            raise
    
    async def generate_html_report(
        self,
        jtl_file_path: str,
        output_dir: str,
    ) -> str:
        """
        Generate HTML report from JTL file
        
        Args:
            jtl_file_path: Path to JTL file
            output_dir: Output directory for HTML report
        
        Returns:
            Path to generated HTML report
        """
        try:
            cmd = [
                self.jmeter_bin,
                "-g", jtl_file_path,  # Generate report from JTL
                "-o", output_dir,  # Output directory
            ]
            
            logger.info(f"Generating HTML report: {' '.join(cmd)}")
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.jmeter_home,
                )
            )
            
            stdout, stderr = await loop.run_in_executor(
                None,
                process.communicate
            )
            
            if process.returncode != 0:
                logger.error(f"Error generating HTML report: {stderr.decode('utf-8', errors='ignore')}")
                raise Exception(f"Failed to generate HTML report: {stderr.decode('utf-8', errors='ignore')}")
            
            return output_dir
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise
    
    async def validate_jmx_file(self, jmx_file_path: str) -> Dict[str, Any]:
        """
        Validate JMX file
        
        Args:
            jmx_file_path: Path to JMX file
        
        Returns:
            Validation result
        """
        try:
            # Try to parse the JMX file
            tree = ET.parse(jmx_file_path)
            root = tree.getroot()
            
            # Check if it's a valid JMeter test plan
            if root.tag != "jmeterTestPlan":
                return {
                    "valid": False,
                    "error": "Not a valid JMeter test plan file"
                }
            
            # Check for TestPlan element
            test_plan = root.find('.//TestPlan')
            if test_plan is None:
                return {
                    "valid": False,
                    "error": "TestPlan element not found"
                }
            
            return {
                "valid": True,
                "test_plan_name": test_plan.get("testname", ""),
            }
        except ET.ParseError as e:
            return {
                "valid": False,
                "error": f"XML parse error: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

