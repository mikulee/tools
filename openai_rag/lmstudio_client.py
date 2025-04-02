"""
LM Studio Client Module
-----------------------
Provides integration with local LM Studio API server.
This module can be reused across multiple projects.
"""

import sys
import json
import requests
import threading
import time
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
import httpx

# Increase default timeout settings
DEFAULT_CONNECT_TIMEOUT = 30  # seconds to establish connection
DEFAULT_READ_TIMEOUT = 300    # seconds to wait for response
DEFAULT_WRITE_TIMEOUT = 30    # seconds to send data

# Default configuration settings - You need to adjust these to your LM Studio server
DEFAULT_LM_STUDIO_URL = "http://localhost:1234/v1"  # Default local URL for LM Studio
LOCAL_API_KEY = "lm-studio-local-key"  # This can be any string for local LM Studio
KEEPALIVE_INTERVAL = 20  # seconds between keepalive pings

class LMStudioClient:
    """Client for interacting with LM Studio local API server."""
    
    def __init__(self, api_url: str = DEFAULT_LM_STUDIO_URL, api_key: str = LOCAL_API_KEY):
        """Initialize the LM Studio client."""
        self.api_url = api_url
        self.api_key = api_key
        self.client = None
        self.connected = False
        self.keepalive_thread = None
        self.stop_keepalive = threading.Event()
        self.completion_active = False  # Flag to track active completion
        self.last_activity = time.time()
        self.connect()
    
    def connect(self) -> bool:
        """Connect to the LM Studio API server."""
        try:
            print(f"Connecting to LM Studio at {self.api_url}")
            
            # Create custom httpx client with longer timeouts
            timeout_settings = httpx.Timeout(
                connect=DEFAULT_CONNECT_TIMEOUT,
                read=DEFAULT_READ_TIMEOUT,
                write=DEFAULT_WRITE_TIMEOUT,
                pool=DEFAULT_CONNECT_TIMEOUT
            )
            
            transport = httpx.HTTPTransport(retries=2)
            
            http_client = httpx.Client(
                timeout=timeout_settings,
                transport=transport
            )
            
            # Create OpenAI client with our custom httpx client
            self.client = OpenAI(
                base_url=self.api_url,
                api_key=self.api_key,
                http_client=http_client
            )
            
            # Test connection with a simple request with retry logic
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        f"{self.api_url}/models", 
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=10
                    )
                    response.raise_for_status()
                    break
                except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                    if attempt < max_retries - 1:
                        print(f"Connection attempt {attempt+1} failed: {str(e)}")
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise
            
            self.connected = True
            self.last_activity = time.time()
            print(f"Successfully connected to LM Studio server at {self.api_url}")
            
            # Start keepalive thread
            self.start_keepalive()
            
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error: Cannot connect to LM Studio at {self.api_url}")
            print("Make sure LM Studio is running and the API server is enabled.")
            self.client = None
            self.connected = False
            return False
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error connecting to LM Studio: {str(e)}")
            if "401" in str(e):
                print("Authentication error. Make sure the LM Studio API doesn't require authentication,")
                print("or provide the correct API key if it does.")
            self.client = None
            self.connected = False
            return False
            
        except Exception as e:
            print(f"Error connecting to LM Studio: {str(e)}")
            print("Make sure LM Studio is running and the API server is enabled.")
            self.client = None
            self.connected = False
            return False
    
    def start_keepalive(self):
        """Start a background thread to periodically ping the server."""
        if self.keepalive_thread and self.keepalive_thread.is_alive():
            return  # Already running
            
        self.stop_keepalive.clear()
        self.keepalive_thread = threading.Thread(
            target=self._keepalive_worker, 
            daemon=True
        )
        self.keepalive_thread.start()
        print("Keepalive mechanism started for LM Studio connection")
    
    def _keepalive_worker(self):
        """Background worker that sends periodic pings to keep connection alive."""
        while not self.stop_keepalive.is_set():
            try:
                if self.connected and not self.completion_active:
                    time_since_activity = time.time() - self.last_activity
                    
                    if time_since_activity > KEEPALIVE_INTERVAL:
                        response = requests.get(
                            f"{self.api_url}/models", 
                            headers={"Authorization": f"Bearer {self.api_key}"},
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            sys.stdout.write(".")
                            sys.stdout.flush()
                            self.last_activity = time.time()
                        else:
                            print(f"\nKeepalive ping returned status code: {response.status_code}")
                            self.connected = False
                            self.connect()
            except Exception as e:
                print(f"\nKeepalive ping failed: {str(e)[:100]}...")
                if not self.completion_active:
                    self.connected = False
                
            short_interval = 5
            self.stop_keepalive.wait(short_interval)
    
    def stop_keepalive(self):
        """Stop the keepalive background thread."""
        if self.keepalive_thread and self.keepalive_thread.is_alive():
            self.stop_keepalive.set()
            self.keepalive_thread.join(timeout=1.0)
            print("\nKeepalive mechanism stopped")
    
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.connected
    
    def __del__(self):
        """Clean up resources when object is destroyed."""
        self.stop_keepalive.set()
        if hasattr(self, 'keepalive_thread') and self.keepalive_thread:
            self.keepalive_thread.join(timeout=1.0)
    
    def list_models(self) -> List[str]:
        """Get available models from LM Studio."""
        if not self.is_connected():
            return []
            
        try:
            self.last_activity = time.time()
            response = requests.get(
                f"{self.api_url}/models", 
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            if "data" in data and isinstance(data["data"], list):
                return [model.get("id", "unknown") for model in data["data"] if "id" in model]
            
            print("Unexpected response format from LM Studio models endpoint")
            return []
            
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    def completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        stream: bool = True
    ) -> Union[str, Any]:
        """Generate a completion using the specified parameters with better error handling."""
        if not self.is_connected():
            raise ConnectionError("Not connected to LM Studio")
        
        # Update last activity time
        self.last_activity = time.time()
        
        # Set completion active flag
        self.completion_active = True
        
        params = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            # No timeout parameter here - we're using the httpx client's timeout settings
        }
        
        # Add optional parameters if they might be supported
        if top_p != 1.0:
            params["top_p"] = top_p
        if presence_penalty != 0.0:
            params["presence_penalty"] = presence_penalty
        if frequency_penalty != 0.0:
            params["frequency_penalty"] = frequency_penalty
        
        try:
            # For streaming, we need to catch errors during iteration
            if stream:
                # Just get the stream object, errors will be caught during iteration
                return self.client.chat.completions.create(**params)
            else:
                # For non-streaming, we can catch errors directly
                return self.client.chat.completions.create(**params)
        except Exception as e:
            # Check if this is a timeout error
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                print("\nTimeout error during completion. This could be because:")
                print("1. The model is taking too long to generate a response")
                print("2. The server is overloaded")
                print("3. The connection is unstable")
            else:
                print(f"\nError during completion: {str(e)}")
            
            # Re-raise so the caller can handle it
            raise
        finally:
            # Clear the completion active flag if not streaming
            # (For streaming, this will be cleared after iteration)
            if not stream:
                self.completion_active = False
                # Update the last activity time
                self.last_activity = time.time()
    
    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        stream: bool = True,
        max_retries: int = 3
    ) -> str:
        """Generate completion with streaming or non-streaming support and robust retry logic."""
        if not self.is_connected():
            print("Error: Not connected to LM Studio server, attempting to reconnect")
            self.connect()
            if not self.is_connected():
                return "Error: Not connected to LM Studio server and reconnection failed"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        full_response = ""
        
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                if stream:
                    if retry_count > 0:
                        print(f"\nRetry attempt {retry_count}/{max_retries}...")
                    else:
                        print(f"Starting streaming completion with model: {model}")
                        print("This may take a while for longer content. Please be patient...")
                    
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
                    
                    if stream_resp is None:
                        print("Error: Received None response from API")
                        return "Error: Failed to get response from LM Studio API"
                    
                    chunk_timeout = 30
                    last_chunk_time = time.time()
                    chunk_received = False
                    
                    try:
                        for chunk in stream_resp:
                            chunk_received = True
                            last_chunk_time = time.time()
                            self.last_activity = last_chunk_time
                            
                            if hasattr(chunk, 'choices') and chunk.choices:
                                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                                    if chunk.choices[0].delta.content:
                                        content_chunk = chunk.choices[0].delta.content
                                        print(content_chunk, end="", flush=True)
                                        full_response += content_chunk
                        
                        break
                            
                    except Exception as chunk_error:
                        if not chunk_received or not full_response:
                            print(f"\nError during streaming: {str(chunk_error)}")
                            retry_count += 1
                            
                            if retry_count <= max_retries:
                                print("Reconnecting and retrying...")
                                self.connect()
                                continue
                            else:
                                return f"Error after {max_retries} retries: {str(chunk_error)}"
                        else:
                            print(f"\n\nStream ended unexpectedly: {str(chunk_error)}")
                            print("Returning partial response.")
                            return full_response + "\n\n[Note: Response was cut off due to a connection issue]"
                    
                    print("\n")
                    
                else:
                    if retry_count > 0:
                        print(f"\nRetry attempt {retry_count}/{max_retries}...")
                    else:
                        print(f"Starting non-streaming completion with model: {model}")
                        print("This may take a while for longer content. Please be patient...")
                    
                    self.completion_active = True
                    progress_thread = threading.Thread(
                        target=self._show_progress_animation,
                        daemon=True
                    )
                    progress_thread.start()
                    
                    try:
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
                        
                        self.completion_active = False
                        progress_thread.join(timeout=1.0)
                        
                        sys.stdout.write("\r                      \r")
                        sys.stdout.flush()
                        
                        if response is None:
                            print("Error: Received None response from API")
                            retry_count += 1
                            
                            if retry_count <= max_retries:
                                print("Reconnecting and retrying...")
                                self.connect()
                                continue
                            else:
                                return f"Error after {max_retries} retries: Failed to get response from API"
                        
                        if hasattr(response, 'choices') and response.choices:
                            if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                                full_response = response.choices[0].message.content
                                print(full_response)
                                break
                            else:
                                print("Error: Response missing expected message.content structure")
                                retry_count += 1
                                
                                if retry_count <= max_retries:
                                    print("Reconnecting and retrying...")
                                    self.connect()
                                    continue
                                else:
                                    return "Error: Unexpected response format from LM Studio API after multiple retries"
                        else:
                            print("Error: Response format not as expected")
                            retry_count += 1
                            
                            if retry_count <= max_retries:
                                print("Reconnecting and retrying...")
                                self.connect()
                                continue
                            else:
                                return "Error: Unexpected response format from LM Studio API after multiple retries"
                            
                    except Exception as e:
                        self.completion_active = False
                        if progress_thread.is_alive():
                            progress_thread.join(timeout=1.0)
                        
                        print(f"\nError during non-streaming completion: {str(e)}")
                        retry_count += 1
                        
                        if retry_count <= max_retries:
                            print("Reconnecting and retrying...")
                            self.connect()
                            continue
                        else:
                            return f"Error after {max_retries} retries: {str(e)}"
                
                break
                
            except Exception as e:
                error_msg = f"Error generating completion: {str(e)}"
                print(error_msg, file=sys.stderr)
                
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"Retry {retry_count}/{max_retries}: Reconnecting and trying again...")
                    self.connect()
                else:
                    print(f"Failed after {max_retries} retries.")
                    if not full_response:
                        return f"Error: {error_msg}"
                    else:
                        return full_response + "\n\n[Note: Response was cut off due to errors after multiple retries]"
        
        return full_response

    def _show_progress_animation(self):
        """Show an animation while waiting for non-streaming completion."""
        progress_indicators = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        idx = 0
        
        while self.completion_active:
            sys.stdout.write(f"\r{progress_indicators[idx]} Generating response... ")
            sys.stdout.flush()
            idx = (idx + 1) % len(progress_indicators)
            time.sleep(0.1)
        
        sys.stdout.write("\r                      \r")
        sys.stdout.flush()

# Helper functions to customize parameters interactively

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

def select_model(client: LMStudioClient) -> str:
    """Select a model from the available models."""
    available_models = client.list_models()
    
    if not available_models:
        print("No models available through the API listing. Let's try another approach.")
        model_name = input("Enter the name of your loaded model in LM Studio: ")
        if model_name.strip():
            return model_name
        return "default"
    
    print("\nAvailable models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")
    
    try:
        choice = input(f"\nSelect model number (1-{len(available_models)}): ")
        if choice.strip() and choice.isdigit() and 1 <= int(choice) <= len(available_models):
            return available_models[int(choice) - 1]
        else:
            print(f"Using first available model: {available_models[0]}")
            return available_models[0]
    except:
        print("Could not select model from list.")
        model_name = input("Enter your LM Studio model name manually (default: default): ")
        return model_name.strip() if model_name.strip() else "default"

def customize_parameters() -> Dict[str, Any]:
    """Get customized parameters from the user."""
    print("\n=== LLM Parameter Customization ===")
    print("Press Enter to keep default values or input custom values.")
    
    params = {}
    
    params["temperature"] = get_param_input("temperature", 0.7, 0.0, 2.0)
    params["top_p"] = get_param_input("top_p", 1.0, 0.0, 1.0)
    params["presence_penalty"] = get_param_input("presence_penalty", 0.0, -2.0, 2.0)
    params["frequency_penalty"] = get_param_input("frequency_penalty", 0.0, -2.0, 2.0)
    params["max_tokens"] = get_int_input("max_tokens", 2000, 100, 8000)
    
    return params

# Simple test function
if __name__ == "__main__":
    print("Testing LM Studio Client...")
    
    url = input(f"Enter LM Studio server URL (default: {DEFAULT_LM_STUDIO_URL}): ")
    url = url.strip() if url.strip() else DEFAULT_LM_STUDIO_URL
    
    client = LMStudioClient(api_url=url)
    if not client.is_connected():
        print("Could not connect to LM Studio. Exiting.")
        sys.exit(1)
        
    model = select_model(client)
    print(f"Selected model: {model}")
    
    response = client.generate_completion(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say hello and tell me what you can do in one sentence.",
        model=model
    )
    
    print("Test complete!")