"""
OpenAI API Client Module
------------------------
Provides integration with OpenAI's public API for use across multiple projects.
"""

from openai import OpenAI
import sys
import os
from typing import List, Dict, Any, Optional, Union
from api_key_manager import get_api_key

class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self, api_key=None):
        """Initialize the OpenAI client with API key."""
        try:
            # Use provided API key or get from the api_key_manager
            self.api_key = api_key or get_api_key()
            self.client = OpenAI(api_key=self.api_key)
            print("OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if client is connected and authenticated."""
        if not self.client:
            return False
            
        # Test connection by listing models (will fail if API key is invalid)
        try:
            self.list_models()
            return True
        except:
            return False
    
    def list_models(self) -> List[str]:
        """Get a list of available models from the API."""
        if not self.client:
            return []
            
        try:
            models_response = self.client.models.list()
            if hasattr(models_response, 'data'):
                return [model.id for model in models_response.data]
            return []
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    def list_filtered_models(self, filter_terms=None) -> List[str]:
        """Get filtered list of relevant text generation models."""
        if filter_terms is None:
            filter_terms = ["gpt-4", "gpt-3.5", "gpt-4o", "text-davinci", 
                            "claude", "gemma", "llama", "mistral"]
            
        all_models = self.list_models()
        
        # Filter for models containing any of the specified terms
        relevant_models = [
            model for model in all_models
            if any(term in model.lower() for term in filter_terms)
        ]
        
        # If we found relevant models, return them sorted
        if relevant_models:
            return sorted(relevant_models)
            
        # If no models match our filter, return all models
        if all_models:
            return sorted(all_models)
            
        # If no models at all, return default list
        return self.get_default_models()
    
    def get_default_models(self) -> List[str]:
        """Return a list of default models when API listing fails."""
        return [
            "gpt-4o-mini", 
            "gpt-3.5-turbo", 
            "gpt-4",
            "gpt-4o",
            "text-davinci-003"
        ]
    
    def detect_api_provider(self) -> str:
        """Try to detect which API provider we're using based on available models."""
        try:
            models = self.list_models()
            
            # Look for characteristic models to identify provider
            if any("claude" in model.lower() for model in models):
                return "Anthropic"
            elif any("llama" in model.lower() for model in models):
                return "Meta AI"
            elif any("gemma" in model.lower() for model in models):
                return "Google"
            elif any("mistral" in model.lower() for model in models):
                return "Mistral AI"
            elif any("gpt-4" in model.lower() or "gpt-3.5" in model.lower() for model in models):
                return "OpenAI"
            else:
                # If we can get models but can't identify provider
                return "Unknown API Provider"
        except:
            # If we can't get models at all
            return "API Provider"
    
    def completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        stream: bool = True
    ) -> Union[Any, str]:
        """Generate a completion using the specified parameters."""
        if not self.client:
            raise ConnectionError("OpenAI client not initialized")
        
        # Create base parameters
        params = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        # Add parameters conditionally based on model type
        if "search" not in model.lower():
            # Standard models support all parameters
            params.update({
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty
            })
        else:
            # Search models only support a subset of parameters
            params["temperature"] = temperature
            params["max_tokens"] = max_tokens
        
        try:
            return self.client.chat.completions.create(**params)
        except Exception as e:
            raise Exception(f"Error during completion: {str(e)}")
    
    def generate_completion_with_streaming(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        stream: bool = True,
        fallback_to_simpler_model: bool = True
    ) -> str:
        """Generate completion with streaming support and optional fallback."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        full_response = ""
        
        try:
            if stream:
                # Streaming mode
                stream_resp = self.completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    stream=True
                )
                
                for chunk in stream_resp:
                    if chunk.choices[0].delta.content:
                        content_chunk = chunk.choices[0].delta.content
                        print(content_chunk, end="", flush=True)
                        full_response += content_chunk
                
                print("\n")  # Add a newline at the end
            else:
                # Non-streaming mode
                response = self.completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    stream=False
                )
                full_response = response.choices[0].message.content
                print(full_response)
            
            return full_response
            
        except Exception as e:
            error_msg = f"Error generating completion: {str(e)}"
            print(error_msg)
            
            # Try fallback to simpler model if enabled
            if fallback_to_simpler_model:
                try:
                    print("Trying with fallback model gpt-3.5-turbo...")
                    fallback_params = {
                        "messages": messages,
                        "model": "gpt-3.5-turbo",
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": stream
                    }
                    
                    if stream:
                        stream_resp = self.client.chat.completions.create(**fallback_params)
                        
                        fallback_response = ""
                        print("\nFallback Response:")
                        for chunk in stream_resp:
                            if chunk.choices[0].delta.content:
                                content_chunk = chunk.choices[0].delta.content
                                print(content_chunk, end="", flush=True)
                                fallback_response += content_chunk
                        
                        print("\n")
                        return fallback_response
                    else:
                        response = self.client.chat.completions.create(**fallback_params)
                        return response.choices[0].message.content
                        
                except Exception as fallback_error:
                    print(f"Fallback also failed: {str(fallback_error)}")
                    return "Error: Failed to generate content, even with fallback model."
            
            return "Error: " + error_msg
    
    def generate_variations(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        custom_params: Dict[str, Any],
        num_versions: int = 1,
        stream: bool = True
    ) -> List[str]:
        """Generate multiple variations of output with parameter adjustments."""
        versions = []
        
        # Use provided parameters or generate variations if multiple versions
        if num_versions > 1:
            # Create variations around the custom parameters
            params_list = []
            base_params = custom_params.copy()
            
            # Version 1: Use exact custom parameters
            params_list.append(base_params.copy())
            
            # Version 2: Slightly more random
            if num_versions >= 2:
                params2 = base_params.copy()
                params2["temperature"] = min(2.0, base_params.get("temperature", 0.7) * 1.2)
                params2["top_p"] = min(1.0, base_params.get("top_p", 1.0) * 1.1)
                params_list.append(params2)
            
            # Version 3: Slightly more focused
            if num_versions >= 3:
                params3 = base_params.copy()
                params3["temperature"] = max(0.1, base_params.get("temperature", 0.7) * 0.8)
                params3["presence_penalty"] = min(2.0, base_params.get("presence_penalty", 0.0) + 0.2)
                params_list.append(params3)
        else:
            # Just use the custom parameters directly
            params_list = [custom_params]
        
        for i, param_set in enumerate(params_list):
            try:
                print(f"\n--- Generating Version {i+1} with {model} ---")
                if num_versions > 1:
                    print(f"Parameter variation: Temperature={param_set.get('temperature', 0.7)}, "
                          f"Top-p={param_set.get('top_p', 1.0)}")
                
                version = self.generate_completion_with_streaming(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=model,
                    temperature=param_set.get("temperature", 0.7),
                    max_tokens=param_set.get("max_tokens", 1000),
                    top_p=param_set.get("top_p", 1.0),
                    presence_penalty=param_set.get("presence_penalty", 0.0),
                    frequency_penalty=param_set.get("frequency_penalty", 0.0),
                    stream=stream
                )
                
                versions.append(version)
                
            except Exception as e:
                print(f"\nError generating version {i+1}: {str(e)}")
                versions.append(f"Error generating content: {str(e)}")
        
        return versions


# Helper functions for interactive parameter selection

def get_param_input(param_name: str, default_value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Helper function to get a parameter input with validation."""
    while True:
        try:
            value_str = input(f"Enter {param_name} ({min_val}-{max_val}, default {default_value}): ")
            if not value_str.strip():
                return default_value
            value = float(value_str)
            if min_val <= value <= max_val:
                return value
            print(f"Value must be between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")

def get_int_input(param_name: str, default_value: int, min_val: int = 1, max_val: int = 4000) -> int:
    """Helper function to get an integer parameter input with validation."""
    while True:
        try:
            value_str = input(f"Enter {param_name} ({min_val}-{max_val}, default {default_value}): ")
            if not value_str.strip():
                return default_value
            value = int(value_str)
            if min_val <= value <= max_val:
                return value
            print(f"Value must be between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid integer")

def select_model(client: OpenAIClient, default_model: str = "gpt-3.5-turbo") -> str:
    """Select a model from the available models."""
    # Get filtered list of models
    available_models = client.list_filtered_models()
    
    if not available_models:
        print(f"No models available. Using default model: {default_model}")
        return default_model
    
    # Try to pick the best default model from what's available
    if "gpt-4o" in available_models:
        suggested_default = "gpt-4o"
    elif "gpt-4" in available_models:
        suggested_default = "gpt-4"
    elif "gpt-3.5-turbo" in available_models:
        suggested_default = "gpt-3.5-turbo"
    elif available_models:  # If we have any models, use the first one
        suggested_default = available_models[0]
    else:
        suggested_default = default_model
    
    print("\nAvailable models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")
    
    try:
        choice = input(f"\nSelect model number (1-{len(available_models)}, default: {suggested_default}): ")
        if choice.strip() and choice.isdigit() and 1 <= int(choice) <= len(available_models):
            return available_models[int(choice) - 1]
        else:
            # If invalid selection or empty, use default (but ensure it's in available_models)
            if suggested_default in available_models:
                return suggested_default
            return available_models[0]
    except:
        # On any error, return the suggested default
        if suggested_default in available_models:
            return suggested_default
        return available_models[0]

def get_custom_parameters() -> Dict[str, Any]:
    """Get customized parameters from the user."""
    print("\n=== LLM Parameter Customization ===")
    print("Press Enter to keep default values or input custom values.")
    
    params = {}
    
    # Temperature (randomness)
    params["temperature"] = get_param_input("temperature", 0.7, 0.0, 2.0)
    
    # Top P (nucleus sampling)
    params["top_p"] = get_param_input("top_p", 1.0, 0.0, 1.0)
    
    # Presence Penalty
    params["presence_penalty"] = get_param_input("presence_penalty", 0.0, -2.0, 2.0)
    
    # Frequency Penalty
    params["frequency_penalty"] = get_param_input("frequency_penalty", 0.0, -2.0, 2.0)
    
    # Max tokens
    params["max_tokens"] = get_int_input("max_tokens", 1000, 100, 4000)
    
    return params

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


# Simple test function to verify functionality
def main():
    """Test the OpenAI client functionality."""
    print("OpenAI Client Module - Test Function")
    
    client = OpenAIClient()
    if not client.is_connected():
        print("Failed to connect to OpenAI API. Exiting.")
        return
    
    provider = client.detect_api_provider()
    print(f"Connected to {provider} API")
    
    # Get models
    models = client.list_filtered_models()
    print(f"Found {len(models)} models")
    
    # Let user select a model
    model = select_model(client)
    print(f"Selected model: {model}")
    
    # Test prompt
    system_prompt = "You are a helpful assistant."
    user_prompt = "Explain why the sky is blue in one short paragraph."
    
    print("\nTesting completion with default parameters...")
    client.generate_completion_with_streaming(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model
    )

if __name__ == "__main__":
    main()