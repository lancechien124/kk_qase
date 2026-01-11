"""
AI Service for OpenAI integration
"""
from typing import Optional, List, Dict, Any
from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger


class AIService:
    """AI service for chat and test case generation"""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if not settings.AI_ENABLED:
            logger.warning("AI is disabled in configuration")
            return
        
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return
        
        try:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
            )
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def is_enabled(self) -> bool:
        """Check if AI is enabled and configured"""
        return settings.AI_ENABLED and self.client is not None
    
    async def chat(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Chat with AI
        
        Args:
            prompt: User prompt
            conversation_id: Optional conversation ID for context
            system_prompt: Optional system prompt
            model: Model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        
        Returns:
            AI response content
        """
        if not self.is_enabled():
            raise Exception("AI service is not enabled or configured")
        
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # TODO: Load conversation history if conversation_id is provided
            # This would require storing conversation history in database or Redis
            
            # Add user message
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content
            logger.info(f"AI chat response generated (model: {model})")
            return content
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            raise
    
    async def generate_test_case(
        self,
        requirement: str,
        project_id: str,
        case_type: str = "functional",  # functional or api
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate test case from requirement
        
        Args:
            requirement: Requirement description
            project_id: Project ID
            case_type: Type of test case (functional or api)
            context: Optional context (API definition, existing cases, etc.)
        
        Returns:
            Generated test case data
        """
        if not self.is_enabled():
            raise Exception("AI service is not enabled or configured")
        
        # Build prompt based on case type
        if case_type == "functional":
            prompt = self._build_functional_case_prompt(requirement, context)
        elif case_type == "api":
            prompt = self._build_api_case_prompt(requirement, context)
        else:
            raise ValueError(f"Unsupported case type: {case_type}")
        
        # Call AI
        response = await self.chat(
            prompt=prompt,
            system_prompt=self._get_system_prompt(case_type),
            temperature=0.7,
        )
        
        # Parse and format response
        return self._parse_test_case_response(response, case_type)
    
    async def generate_api_test_case(
        self,
        api_definition: Dict[str, Any],
        user_prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """
        Generate API test case from API definition
        
        Args:
            api_definition: API definition data
            user_prompt: Optional user prompt
            conversation_id: Optional conversation ID
        
        Returns:
            Generated test case content
        """
        if not self.is_enabled():
            raise Exception("AI service is not enabled or configured")
        
        # Build prompt
        prompt = self._build_api_test_case_prompt(api_definition, user_prompt)
        
        # Call AI
        response = await self.chat(
            prompt=prompt,
            conversation_id=conversation_id,
            system_prompt=self._get_api_test_case_system_prompt(),
        )
        
        return response
    
    async def generate_test_data(
        self,
        data_type: str,
        count: int = 1,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate test data
        
        Args:
            data_type: Type of data (e.g., "user", "email", "phone")
            count: Number of data items to generate
            constraints: Optional constraints
        
        Returns:
            List of generated test data
        """
        if not self.is_enabled():
            raise Exception("AI service is not enabled or configured")
        
        prompt = f"""
Generate {count} test data items of type: {data_type}
Constraints: {constraints or {}}

Return as JSON array format.
"""
        
        response = await self.chat(
            prompt=prompt,
            system_prompt="You are a test data generator. Generate realistic test data in JSON format.",
            temperature=0.8,
        )
        
        # Parse JSON response
        try:
            import json
            data = json.loads(response)
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            # If not JSON, try to extract JSON from markdown
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                return data if isinstance(data, list) else [data]
            raise ValueError("Failed to parse AI response as JSON")
    
    def _build_functional_case_prompt(
        self,
        requirement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for functional case generation"""
        prompt = f"""
Generate a functional test case based on the following requirement:

Requirement: {requirement}

Please generate a test case with:
1. Test case name
2. Preconditions
3. Test steps (detailed)
4. Expected results
5. Priority

Format the output in a structured way.
"""
        return prompt
    
    def _build_api_case_prompt(
        self,
        requirement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for API case generation"""
        prompt = f"""
Generate an API test case based on the following requirement:

Requirement: {requirement}

Please generate a test case with:
1. Test case name
2. Request method and path
3. Request parameters/body
4. Expected response status code
5. Expected response body structure
6. Assertions

Format the output in a structured way.
"""
        return prompt
    
    def _build_api_test_case_prompt(
        self,
        api_definition: Dict[str, Any],
        user_prompt: Optional[str] = None,
    ) -> str:
        """Build prompt for API test case generation from API definition"""
        api_info = f"""
API Information:
- Name: {api_definition.get('name', '')}
- Method: {api_definition.get('method', '')}
- Path: {api_definition.get('path', '')}
- Description: {api_definition.get('description', '')}
"""
        
        if user_prompt:
            prompt = f"""
{api_info}

User request: {user_prompt}

Generate an API test case based on the above API definition and user request.
"""
        else:
            prompt = f"""
{api_info}

Generate a comprehensive API test case for the above API definition.
Include:
1. Test case name
2. Request parameters/body
3. Expected response
4. Assertions
"""
        return prompt
    
    def _get_system_prompt(self, case_type: str) -> str:
        """Get system prompt for case generation"""
        if case_type == "functional":
            return """You are a test case generation assistant. 
Generate comprehensive functional test cases based on requirements.
Format your response in a clear, structured way."""
        elif case_type == "api":
            return """You are an API test case generation assistant.
Generate comprehensive API test cases based on API definitions.
Format your response in a clear, structured way."""
        return "You are a test case generation assistant."
    
    def _get_api_test_case_system_prompt(self) -> str:
        """Get system prompt for API test case generation"""
        return """You are an API test case generation assistant.
Generate test cases based on API definitions and user requirements.
Format your response in Markdown format with clear structure."""
    
    def _parse_test_case_response(
        self,
        response: str,
        case_type: str,
    ) -> Dict[str, Any]:
        """Parse AI response into test case structure"""
        # TODO: Implement intelligent parsing of AI response
        # This should extract structured data from the response
        return {
            "raw_response": response,
            "parsed": False,  # Indicates parsing is not yet implemented
        }
    
    async def check_if_generate_case(self, user_input: str) -> bool:
        """
        Check if user wants to generate test case
        
        Args:
            user_input: User input text
        
        Returns:
            True if user wants to generate case, False otherwise
        """
        if not self.is_enabled():
            return False
        
        prompt = f"""
As a test case generation assistant, determine: Does the user want to generate a test case?

User input: {user_input}

Only return a single boolean value:
- Yes → true
- No → false
- Do not return any other text or explanation
"""
        
        try:
            response = await self.chat(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more deterministic output
            )
            
            # Check if response contains "true"
            return "true" in response.lower()
        except Exception as e:
            logger.error(f"Error checking if generate case: {e}")
            return False
    
    async def save_conversation(
        self,
        conversation_id: str,
        role: str,  # "user" or "assistant"
        content: str,
    ):
        """Save conversation message"""
        # TODO: Implement conversation storage in database or Redis
        # This would allow maintaining conversation context
        pass
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> List[Dict[str, str]]:
        """Get conversation history"""
        # TODO: Implement conversation history retrieval
        return []

