"""
Visual Analysis module for detailed image descriptions.
Provides general-purpose image analysis using Google Gemini.
"""

import os
import base64
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

# Prompt for detailed image description
DETAILED_DESCRIPTION_PROMPT = """Give a very detailed description of the image given to you. 
Include anything that could be beneficial like brands or logos and sizes of the item.
Describe colors, shapes, text, objects, people, settings, and any other relevant details.
Be thorough and specific."""


class VisualAnalyzer:
    """Provides detailed visual analysis of images using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the visual analyzer.
        
        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Use gemini-2.0-flash-exp (current as of Jan 2026)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def describe_image_bytes(self, image_bytes: bytes) -> str:
        """
        Provide a detailed description of an image from bytes.
        
        Args:
            image_bytes: JPEG image data
            
        Returns:
            str: Detailed description of the image
        """
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # Generate response
            response = self.model.generate_content([DETAILED_DESCRIPTION_PROMPT, image_part])
            return response.text
            
        except Exception as e:
            return f"Sorry, I had trouble analyzing the image: {str(e)}"
    
    def describe_image_file(self, filepath: str) -> str:
        """
        Provide a detailed description of an image from a file.
        
        Args:
            filepath: Path to image file
            
        Returns:
            str: Detailed description of the image
        """
        try:
            with open(filepath, 'rb') as f:
                image_bytes = f.read()
            return self.describe_image_bytes(image_bytes)
        except FileNotFoundError:
            return f"Sorry, I couldn't find the image file: {filepath}"
        except Exception as e:
            return f"Sorry, I had trouble reading the image: {str(e)}"
    
    def extract_search_terms(self, description: str) -> str:
        """
        Converts image description into compact search terms.
        
        Args:
            description: Detailed image description
            
        Returns:
            str: Compact search-friendly description
        """
        try:
            prompt = "Given the very detailed description, output a more compact description suitable for search purposes in a search engine. Your response must be a single sentence."
            response = self.model.generate_content([prompt, description])
            return response.text
        except Exception as e:
            return f"Sorry, I had trouble extracting search terms: {str(e)}"


# Global instance for easy access
_analyzer: Optional[VisualAnalyzer] = None


def get_analyzer() -> VisualAnalyzer:
    """Get or create the global visual analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = VisualAnalyzer()
    return _analyzer


def describe_image(image_bytes: Optional[bytes] = None,
                   image_path: Optional[str] = None,
                   camera=None) -> str:
    """
    Provide a detailed description of an image. Convenience function for use as a tool.
    
    Args:
        image_bytes: Raw image bytes (optional)
        image_path: Path to image file (optional)
        camera: Camera instance to capture from (optional)
        
    Returns:
        str: Detailed description of the image
    """
    analyzer = get_analyzer()
    
    # If camera provided, capture image
    if camera is not None:
        image_bytes = camera.capture()
        if image_bytes is None:
            return "Sorry, I couldn't capture an image from the camera. Please check the camera connection."
    
    # Analyze based on what was provided
    if image_bytes is not None:
        return analyzer.describe_image_bytes(image_bytes)
    elif image_path is not None:
        return analyzer.describe_image_file(image_path)
    else:
        return "No image provided. Please provide an image to analyze."


# Legacy function names for backward compatibility
def show_and_tell(image_bytes: Optional[bytes] = None,
                  image_path: Optional[str] = None,
                  camera=None) -> str:
    """
    Legacy function name - same as describe_image.
    Describes the image in detail.
    """
    return describe_image(image_bytes=image_bytes, image_path=image_path, camera=camera)


if __name__ == "__main__":
    # Quick test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <image_path>")
        print("       Provides detailed description of an image")
        sys.exit(1)
    
    image_path = sys.argv[1]
    print(f"Analyzing {image_path}...")
    
    try:
        result = describe_image(image_path=image_path)
        print("\nDescription:")
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure GOOGLE_API_KEY environment variable is set")    