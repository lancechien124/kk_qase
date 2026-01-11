"""
JMeter Script Parser - Convert API scenarios to JMX format
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logging import logger


class JMeterJMXGenerator:
    """Generate JMX files from API scenarios"""
    
    def __init__(self):
        self.ns = {
            'jmeter': 'http://www.apache.org/licenses/LICENSE-2.0',
        }
    
    def generate_jmx_from_api_scenario(
        self,
        scenario_name: str,
        api_definitions: List[Dict[str, Any]],
        thread_group_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate JMX file from API scenario
        
        Args:
            scenario_name: Scenario name
            api_definitions: List of API definitions
            thread_group_config: Thread group configuration
        
        Returns:
            JMX XML content as string
        """
        # Create root element
        root = ET.Element("jmeterTestPlan", version="1.2", properties="5.0", jmeter="5.6")
        
        # Create hash tree
        hash_tree = ET.SubElement(root, "hashTree")
        
        # Create test plan
        test_plan = self._create_test_plan(scenario_name)
        hash_tree.append(test_plan)
        
        # Create test plan hash tree
        test_plan_hash_tree = ET.SubElement(hash_tree, "hashTree")
        
        # Create thread group
        thread_group = self._create_thread_group(
            scenario_name,
            thread_group_config or {}
        )
        test_plan_hash_tree.append(thread_group)
        
        # Create thread group hash tree
        thread_group_hash_tree = ET.SubElement(test_plan_hash_tree, "hashTree")
        
        # Add API definitions as HTTP samplers
        for api_def in api_definitions:
            http_sampler = self._create_http_sampler(api_def)
            thread_group_hash_tree.append(http_sampler)
            
            # Add hash tree for sampler
            sampler_hash_tree = ET.SubElement(thread_group_hash_tree, "hashTree")
            
            # Add assertion if expected response is provided
            if api_def.get("expected_response"):
                assertion = self._create_response_assertion(api_def)
                sampler_hash_tree.append(assertion)
                ET.SubElement(sampler_hash_tree, "hashTree")
        
        # Convert to string
        xml_str = ET.tostring(root, encoding='unicode')
        # Pretty print
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def _create_test_plan(self, name: str) -> ET.Element:
        """Create TestPlan element"""
        test_plan = ET.Element("TestPlan", guiclass="TestPlanGui", testclass="TestPlan", testname=name, enabled="true")
        
        # Add properties
        bool_prop = ET.SubElement(test_plan, "boolProp", name="TestPlan.functional_mode")
        bool_prop.text = "false"
        
        bool_prop = ET.SubElement(test_plan, "boolProp", name="TestPlan.serialize_threadgroups")
        bool_prop.text = "false"
        
        element_prop = ET.SubElement(test_plan, "elementProp", name="TestPlan.arguments", elementType="Arguments", guiclass="ArgumentsPanel", testclass="Arguments", testname="User Defined Variables", enabled="true")
        collection_prop = ET.SubElement(element_prop, "collectionProp", name="Arguments.arguments")
        
        string_prop = ET.SubElement(test_plan, "stringProp", name="TestPlan.user_define_classpath")
        string_prop.text = ""
        
        return test_plan
    
    def _create_thread_group(
        self,
        name: str,
        config: Dict[str, Any]
    ) -> ET.Element:
        """Create ThreadGroup element"""
        thread_group = ET.Element(
            "ThreadGroup",
            guiclass="ThreadGroupGui",
            testclass="ThreadGroup",
            testname=name,
            enabled="true"
        )
        
        # Number of threads
        string_prop = ET.SubElement(thread_group, "stringProp", name="ThreadGroup.on_sample_error")
        string_prop.text = "continue"
        
        element_prop = ET.SubElement(thread_group, "elementProp", name="ThreadGroup.main_controller", elementType="LoopController", guiclass="LoopControllerGui", testclass="LoopController", testname="Loop Controller", enabled="true")
        bool_prop = ET.SubElement(element_prop, "boolProp", name="LoopController.continue_forever")
        bool_prop.text = "false"
        
        string_prop = ET.SubElement(element_prop, "stringProp", name="LoopController.loops")
        string_prop.text = str(config.get("loops", 1))
        
        string_prop = ET.SubElement(thread_group, "stringProp", name="ThreadGroup.num_threads")
        string_prop.text = str(config.get("num_threads", 1))
        
        string_prop = ET.SubElement(thread_group, "stringProp", name="ThreadGroup.ramp_time")
        string_prop.text = str(config.get("ramp_time", 1))
        
        bool_prop = ET.SubElement(thread_group, "boolProp", name="ThreadGroup.scheduler")
        bool_prop.text = "false"
        
        string_prop = ET.SubElement(thread_group, "stringProp", name="ThreadGroup.duration")
        string_prop.text = ""
        
        string_prop = ET.SubElement(thread_group, "stringProp", name="ThreadGroup.delay")
        string_prop.text = ""
        
        return thread_group
    
    def _create_http_sampler(self, api_def: Dict[str, Any]) -> ET.Element:
        """Create HTTPSamplerProxy element"""
        sampler = ET.Element(
            "HTTPSamplerProxy",
            guiclass="HttpTestSampleGui",
            testclass="HTTPSamplerProxy",
            testname=api_def.get("name", "HTTP Request"),
            enabled="true"
        )
        
        # Domain
        element_prop = ET.SubElement(sampler, "elementProp", name="HTTPsampler.Arguments", elementType="Arguments", guiclass="HTTPArgumentsPanel", testclass="Arguments", testname="User Defined Variables", enabled="true")
        collection_prop = ET.SubElement(element_prop, "collectionProp", name="Arguments.arguments")
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.domain")
        string_prop.text = api_def.get("domain", "")
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.port")
        string_prop.text = str(api_def.get("port", ""))
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.protocol")
        string_prop.text = api_def.get("protocol", "https")
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.contentEncoding")
        string_prop.text = ""
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.path")
        string_prop.text = api_def.get("path", "")
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.method")
        string_prop.text = api_def.get("method", "GET")
        
        bool_prop = ET.SubElement(sampler, "boolProp", name="HTTPSampler.follow_redirects")
        bool_prop.text = "true"
        
        bool_prop = ET.SubElement(sampler, "boolProp", name="HTTPSampler.auto_redirects")
        bool_prop.text = "false"
        
        bool_prop = ET.SubElement(sampler, "boolProp", name="HTTPSampler.use_keepalive")
        bool_prop.text = "true"
        
        bool_prop = ET.SubElement(sampler, "boolProp", name="HTTPSampler.DO_MULTIPART_POST")
        bool_prop.text = "false"
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.embedded_url_re")
        string_prop.text = ""
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.connect_timeout")
        string_prop.text = ""
        
        string_prop = ET.SubElement(sampler, "stringProp", name="HTTPSampler.response_timeout")
        string_prop.text = ""
        
        return sampler
    
    def _create_response_assertion(self, api_def: Dict[str, Any]) -> ET.Element:
        """Create ResponseAssertion element"""
        assertion = ET.Element(
            "ResponseAssertion",
            guiclass="AssertionGui",
            testclass="ResponseAssertion",
            testname="Response Assertion",
            enabled="true"
        )
        
        collection_prop = ET.SubElement(assertion, "collectionProp", name="Asserion.test_strings")
        string_prop = ET.SubElement(collection_prop, "stringProp")
        string_prop.text = api_def.get("expected_response", "")
        
        string_prop = ET.SubElement(assertion, "stringProp", name="Assertion.custom_message")
        string_prop.text = ""
        
        string_prop = ET.SubElement(assertion, "stringProp", name="Assertion.test_field")
        string_prop.text = "Assertion.response_data"
        
        bool_prop = ET.SubElement(assertion, "boolProp", name="Assertion.assume_success")
        bool_prop.text = "false"
        
        int_prop = ET.SubElement(assertion, "intProp", name="Assertion.test_type")
        int_prop.text = "2"  # Contains
        
        return assertion

