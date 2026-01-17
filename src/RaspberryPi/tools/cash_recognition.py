"""
Cash/Banknote Recognition using Google Gemini.
Analyzes images to identify banknotes and their denominations.
"""

import os
import base64
from typing import Optional
import google.generativeai as genai


# Prompt for banknote recognition
BANKNOTE_PROMPT = """Analyze this image and identify all banknotes/paper currency visible.

For each banknote you can see, provide:
1. The denomination (e.g., £20, $50, €10)
2. The currency name (e.g., British Pound Sterling, US Dollar, Euro)
3. Any notable features visible (e.g., "polymer note", "showing the Queen's portrait side")

If multiple notes are visible:
- List each one separately
- Provide the total value at the end

Format your response conversationally, as if speaking to someone who cannot see the image.
For example: "I can see a twenty pound note, it's a polymer note showing the Queen's portrait. That's twenty pounds total."

If no banknotes are visible in the image, say: "I don't see any banknotes in this image. Please hold the notes in front of the camera and try again."

If the image is blurry or unclear, mention that and suggest adjustments.
"""


class CashRecognizer:
    """Recognizes banknotes in images using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the cash recognizer.
        
        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Use gemini-2.0-flash-exp (current as of Jan 2026)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze_image_bytes(self, image_bytes: bytes) -> str:
        """
        Analyze image bytes for banknotes.
        
        Args:
            image_bytes: JPEG image data
            
        Returns:
            str: Description of banknotes found
        """
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # Generate response
            response = self.model.generate_content([BANKNOTE_PROMPT, image_part])
            return response.text
            
        except Exception as e:
            return f"Sorry, I had trouble analyzing the image: {str(e)}"
    
    def analyze_image_file(self, filepath: str) -> str:
        """
        Analyze an image file for banknotes.
        
        Args:
            filepath: Path to image file
            
        Returns:
            str: Description of banknotes found
        """
        try:
            with open(filepath, 'rb') as f:
                image_bytes = f.read()
            return self.analyze_image_bytes(image_bytes)
        except FileNotFoundError:
            return f"Sorry, I couldn't find the image file: {filepath}"
        except Exception as e:
            return f"Sorry, I had trouble reading the image: {str(e)}"
    
    def analyze_base64(self, image_base64: str) -> str:
        """
        Analyze a base64 encoded image for banknotes.
        
        Args:
            image_base64: Base64 encoded image data
            
        Returns:
            str: Description of banknotes found
        """
        try:
            image_bytes = base64.b64decode(image_base64)
            return self.analyze_image_bytes(image_bytes)
        except Exception as e:
            return f"Sorry, I had trouble decoding the image: {str(e)}"


# Global instance for easy access
_recognizer: Optional[CashRecognizer] = None


def get_recognizer() -> CashRecognizer:
    """Get or create the global cash recognizer instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = CashRecognizer()
    return _recognizer


def identify_cash(image_bytes: Optional[bytes] = None, 
                  image_path: Optional[str] = None,
                  camera=None) -> str:
    """
    Identify cash in an image. Convenience function for use as a tool.
    
    Args:
        image_bytes: Raw image bytes (optional)
        image_path: Path to image file (optional)
        camera: Camera instance to capture from (optional)
        
    Returns:
        str: Description of banknotes found
    """
    recognizer = get_recognizer()
    
    # If camera provided, capture image
    if camera is not None:
        image_bytes = camera.capture()
        if image_bytes is None:
            return "Sorry, I couldn't capture an image from the camera. Please check the camera connection."
    
    # Analyze based on what was provided
    if image_bytes is not None:
        return recognizer.analyze_image_bytes(image_bytes)
    elif image_path is not None:
        return recognizer.analyze_image_file(image_path)
    else:
        return "No image provided. Please provide an image to analyze."


if __name__ == "__main__":
    # Quick test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cash_recognition.py <image_path>")
        print("       Analyzes an image file for banknotes")
        sys.exit(1)
    
    image_path = sys.argv[1]
    print(f"Analyzing {image_path}...")
    
    try:
        result = identify_cash(image_path=image_path)
        print("\nResult:")
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure GOOGLE_API_KEY environment variable is set")
