"""
Packaging/Label Reader using Google Gemini.
Analyzes images to read text from packaging, labels, and medication boxes.
"""

import os
import base64
from typing import Optional
import google.generativeai as genai


# Prompt for reading packaging
PACKAGING_PROMPT = """Analyze this image and read all text visible on the packaging, label, or box.

Focus on identifying and clearly stating:

1. PRODUCT NAME - What is this product called?
2. KEY INFORMATION based on product type:
   - For FOOD: List ingredients, allergens (VERY IMPORTANT - call these out clearly), 
     nutritional info, cooking instructions, serving suggestions
   - For MEDICATION: Drug name, dosage, active ingredients, warnings, 
     how to take it, what it's for
   - For OTHER PRODUCTS: Main purpose, instructions for use, warnings

3. EXPIRY DATE - If visible, mention when this expires

4. ALLERGEN WARNINGS - Call out any allergy information prominently 
   (e.g., "CONTAINS: wheat, milk, eggs" or "May contain traces of nuts")

Format your response conversationally, as if speaking to someone who cannot see the label.
Be thorough but organized - read the most important information first.

Example for food:
"This is a pack of Tesco Chicken Tikka Masala. The ingredients include chicken, 
tomatoes, cream, and various spices. Important allergen warning: this contains 
milk and may contain traces of nuts. To cook, microwave for 4 minutes. 
Best before March 2026."

Example for medication:
"This is Ibuprofen 400mg tablets. Take one tablet up to three times daily with food.
Do not exceed 3 tablets in 24 hours. Warning: do not take if you have asthma or 
are allergic to aspirin. Keep out of reach of children."

If the image is blurry or text is not readable, say so and suggest adjustments.
If no packaging or labels are visible, say: "I don't see any packaging or labels 
in this image. Please hold the item closer to the camera."
"""


class PackagingReader:
    """Reads text from packaging and labels using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the packaging reader.
        
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
        Analyze image bytes to read packaging text.
        
        Args:
            image_bytes: JPEG image data
            
        Returns:
            str: Description of text found on packaging
        """
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # Generate response
            response = self.model.generate_content([PACKAGING_PROMPT, image_part])
            return response.text
            
        except Exception as e:
            return f"Sorry, I had trouble reading the packaging: {str(e)}"
    
    def analyze_image_file(self, filepath: str) -> str:
        """
        Analyze an image file to read packaging text.
        
        Args:
            filepath: Path to image file
            
        Returns:
            str: Description of text found on packaging
        """
        try:
            with open(filepath, 'rb') as f:
                image_bytes = f.read()
            return self.analyze_image_bytes(image_bytes)
        except FileNotFoundError:
            return f"Sorry, I couldn't find the image file: {filepath}"
        except Exception as e:
            return f"Sorry, I had trouble reading the image: {str(e)}"


# Global instance for easy access
_reader: Optional[PackagingReader] = None


def get_reader() -> PackagingReader:
    """Get or create the global packaging reader instance."""
    global _reader
    if _reader is None:
        _reader = PackagingReader()
    return _reader


def read_packaging(image_bytes: Optional[bytes] = None, 
                   image_path: Optional[str] = None,
                   camera=None) -> str:
    """
    Read text from packaging in an image. Convenience function for use as a tool.
    
    Args:
        image_bytes: Raw image bytes (optional)
        image_path: Path to image file (optional)
        camera: Camera instance to capture from (optional)
        
    Returns:
        str: Description of text found on packaging
    """
    reader = get_reader()
    
    # If camera provided, capture image
    if camera is not None:
        image_bytes = camera.capture()
        if image_bytes is None:
            return "Sorry, I couldn't capture an image from the camera. Please check the camera connection."
    
    # Analyze based on what was provided
    if image_bytes is not None:
        return reader.analyze_image_bytes(image_bytes)
    elif image_path is not None:
        return reader.analyze_image_file(image_path)
    else:
        return "No image provided. Please provide an image to analyze."


if __name__ == "__main__":
    # Quick test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python packaging_reader.py <image_path>")
        print("       Reads text from packaging in an image")
        sys.exit(1)
    
    image_path = sys.argv[1]
    print(f"Reading packaging from {image_path}...")
    
    try:
        result = read_packaging(image_path=image_path)
        print("\nResult:")
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure GOOGLE_API_KEY environment variable is set")
