"""
LLM Client Factory Module
------------------------
Provides a unified interface to select and use different LLM API providers.
"""

import sys
from typing import Optional, Union, Dict, Any

# Import both client types
from openai_client import OpenAIClient, get_custom_parameters as openai_get_params
from lmstudio_client import LMStudioClient, customize_parameters as lmstudio_get_params
from lmstudio_client import DEFAULT_LM_STUDIO_URL

class LLMClientFactory:
    """Factory class to select and initialize appropriate LLM client"""
    
    @staticmethod
    def create_client(api_type: str = None, api_url: str = None) -> Union[OpenAIClient, LMStudioClient, None]:
        """
        Create and return the appropriate client based on user selection or parameters.
        
        Args:
            api_type: Type of API to use ('openai' or 'lmstudio')
            api_url: API URL for LM Studio (only used if api_type is 'lmstudio')
            
        Returns:
            Initialized client object or None if initialization fails
        """
        # If no API type provided, ask user
        if not api_type:
            api_type = LLMClientFactory.get_api_selection()
        
        # Initialize the selected client type
        if api_type.lower() == 'openai':
            print("Initializing OpenAI client with public API...")
            client = OpenAIClient()
            if not client.is_connected():
                print("Failed to connect to OpenAI API. Check your API key and internet connection.")
                return None
            return client
            
        elif api_type.lower() == 'lmstudio':
            print("Initializing LM Studio client with local API...")
            
            # If no API URL provided, ask for it
            if not api_url:
                url = input(f"Enter LM Studio server URL (default: {DEFAULT_LM_STUDIO_URL}): ")
                api_url = url.strip() if url.strip() else DEFAULT_LM_STUDIO_URL
            
            client = LMStudioClient(api_url=api_url)
            if not client.is_connected():
                print("Failed to connect to LM Studio. Make sure the server is running.")
                return None
            return client
            
        else:
            print(f"Unknown API type: {api_type}")
            return None
    
    @staticmethod
    def get_api_selection() -> str:
        """
        Prompt user to select which API to use.
        
        Returns:
            String with API choice ('openai' or 'lmstudio')
        """
        print("\n=== LLM API Selection ===")
        print("1. OpenAI (Public API - requires API key)")
        print("2. LM Studio (Local API - requires running LM Studio)")
        
        while True:
            choice = input("\nSelect API type (1-2): ")
            
            if choice == "1":
                return "openai"
            elif choice == "2":
                return "lmstudio"
            else:
                print("Invalid selection. Please enter 1 or 2.")
    
    @staticmethod
    def select_model(client: Union[OpenAIClient, LMStudioClient], model_name: Optional[str] = None) -> str:
        """
        Select a model from the client's available models.
        
        Args:
            client: The LLM client (OpenAI or LM Studio)
            model_name: Optional pre-selected model name
            
        Returns:
            Selected model name
        """
        if model_name:
            return model_name
            
        # Use the appropriate select_model function based on client type
        if isinstance(client, OpenAIClient):
            from openai_client import select_model
            return select_model(client)
        elif isinstance(client, LMStudioClient):
            from lmstudio_client import select_model
            return select_model(client)
        else:
            return "gpt-3.5-turbo"  # Default fallback
    
    @staticmethod
    def get_custom_parameters(client: Union[OpenAIClient, LMStudioClient]) -> Dict[str, Any]:
        """
        Get custom parameters for the specific client type.
        
        Args:
            client: The LLM client (OpenAI or LM Studio)
            
        Returns:
            Dictionary of parameters
        """
        # Use the appropriate parameter customization function based on client type
        if isinstance(client, OpenAIClient):
            return openai_get_params()
        elif isinstance(client, LMStudioClient):
            return lmstudio_get_params()
        else:
            # Return default parameters if client type is unknown
            return {
                "temperature": 0.7,
                "top_p": 1.0,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "max_tokens": 2000
            }
    
    @staticmethod
    def customize_system_prompt(default_prompt: str) -> str:
        """Allow user to customize a system prompt."""
        print("\n=== System Prompt Customization ===")
        print("Current system prompt:")
        print(default_prompt)
        customize = input("\nWould you like to customize this prompt? (y/n, default n): ")
        
        if customize.lower() == 'y':
            print("\nEnter your custom system prompt (type 'END' on a new line when done):")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            custom_prompt = "\n".join(lines)
            return custom_prompt if custom_prompt.strip() else default_prompt
        
        return default_prompt

    @staticmethod
    def get_openai_client_class():
        """Get the OpenAI client class for type checking."""
        from openai_client import OpenAIClient
        return OpenAIClient

    @staticmethod
    def get_lmstudio_client_class():
        """Get the LM Studio client class for type checking."""
        from lmstudio_client import LMStudioClient
        return LMStudioClient