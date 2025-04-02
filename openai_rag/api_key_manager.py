import subprocess
import sys

def get_api_key():
    """
    Retrieves the OpenAI API key from 1Password using the CLI.
    
    Returns:
        str: The retrieved API key
    
    Raises:
        SystemExit: If there's an error retrieving the API key
    """
    try:
        print("Retrieving API key from 1Password...")
        result = subprocess.run(['op', 'item', 'get', 'kai6acv6nldojqwzbgc5ddvggy', '--reveal'], 
                               capture_output=True, text=True, check=True)
        
        # The output with --reveal flag is different, likely not JSON
        # We need to extract the API key from the output
        output = result.stdout.strip()
        print(f"Raw output received, length: {len(output)}")
        
        # Assuming the API key is in the output
        # Extract based on expected format - this may need adjustment
        lines = output.split('\n')
        api_key = None
        
        # Loop through lines to find the password/API key
        for line in lines:
            if 'password:' in line.lower():
                # Extract the API key part after "password:"
                api_key = line.split(':', 1)[1].strip()
                break
        
        if not api_key:
            # If we couldn't find it with the above method, try using the whole output
            # (assuming the output is just the API key)
            if output.startswith('sk-'):
                api_key = output
        
        if not api_key:
            print("Could not extract API key from 1Password output")
            print("Raw output format (first 10 chars):", output[:10] + "...")
            sys.exit(1)
        
        print(f"API key retrieved successfully (starts with: {api_key[:5]}...)")
        return api_key
        
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving API key from 1Password: {e}")
        print(f"Command stderr: {e.stderr}")
        print(f"Return code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    # Test the function if this file is run directly
    api_key = get_api_key()
    print(f"API key retrieved and ready for use (first 5 chars: {api_key[:5]}...)")