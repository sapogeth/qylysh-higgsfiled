"""
Colab API Client - Connect local Flask app to Google Colab GPU
"""

import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class ColabClient:
    """Client for connecting to Colab-hosted generation API"""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize Colab client
        
        Args:
            api_url: Colab API endpoint (e.g., https://abc123.ngrok.io)
                    If not provided, reads from COLAB_API_URL env var
        """
        self.api_url = api_url or os.getenv('COLAB_API_URL')
        if not self.api_url:
            raise ValueError(
                "Colab API URL not configured. "
                "Set COLAB_API_URL environment variable or pass api_url parameter"
            )
        
        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test if Colab API is reachable"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.ok:
                data = response.json()
                print(f"✓ Connected to Colab API")
                print(f"  Device: {data.get('device', 'unknown')}")
                print(f"  GPU: {data.get('gpu', 'none')}")
            else:
                raise ConnectionError(f"Health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Cannot connect to Colab API at {self.api_url}\n"
                f"Make sure:\n"
                f"  1. Colab notebook is running\n"
                f"  2. ngrok tunnel is active\n"
                f"  3. COLAB_API_URL is correct\n"
                f"Error: {e}"
            )
    
    def generate_single(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        ref_image: Optional[Image.Image] = None,
        ip_adapter_scale: Optional[float] = None
    ) -> Image.Image:
        """
        Generate a single image using Colab GPU
        
        Args:
            prompt: Text prompt for generation
            negative_prompt: Negative prompt (what to avoid)
            ref_image: Optional reference image for IP-Adapter
            ip_adapter_scale: IP-Adapter strength (0.0-1.0)
        
        Returns:
            PIL Image
        """
        
        # Prepare request payload
        payload = {
            'prompt': prompt,
            'negative_prompt': negative_prompt
        }
        
        # Add reference image if provided
        if ref_image is not None:
            # Convert image to base64
            buffered = BytesIO()
            ref_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            payload['ref_image_base64'] = img_base64
            payload['ip_adapter_scale'] = ip_adapter_scale or 0.6
        
        # Send request to Colab
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=120  # 2 minutes timeout for generation
            )
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success'):
                raise RuntimeError(f"Generation failed: {result.get('error', 'Unknown error')}")
            
            # Decode image from base64
            img_data = base64.b64decode(result['image_base64'])
            image = Image.open(BytesIO(img_data))
            
            return image
            
        except requests.exceptions.Timeout:
            raise TimeoutError(
                "Colab generation timed out (>2 minutes). "
                "This might happen if the model needs to load. Try again."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Colab API request failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Colab API is currently available"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.ok
        except:
            return False


# Example usage
if __name__ == "__main__":
    # Test the Colab client
    import sys
    
    if not os.getenv('COLAB_API_URL'):
        print("Error: COLAB_API_URL not set in .env file")
        print("\nAdd this line to your .env file:")
        print("  COLAB_API_URL=https://your-ngrok-url.ngrok.io")
        sys.exit(1)
    
    print("Testing Colab connection...")
    try:
        client = ColabClient()
        
        # Test generation
        print("\nGenerating test image...")
        test_prompt = "Aldar Kose walking across golden steppe, 2D illustration"
        image = client.generate_single(test_prompt)
        
        # Save test image
        output_path = "test_colab_output.png"
        image.save(output_path)
        print(f"✓ Test successful! Image saved to: {output_path}")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
