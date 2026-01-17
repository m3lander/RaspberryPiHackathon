"""
E-Commerce Item Recognition using Google Gemini.
Analyzes images to identify items for eBay listings including brand, size, color, and condition.
"""

import os
import base64
from typing import Optional
import google.generativeai as genai


# Prompt for e-commerce item recognition
ECOMMERCE_ITEM_PROMPT = """Analyze this image and identify the item for an eBay listing.

Provide the following details in a conversational, natural way:

1. **Item Type/Name** - What is this item? (e.g., "men's jacket", "smartphone", "handbag")

2. **Brand** - Any visible logos, labels, or brand names

3. **Size/Dimensions** - Size tags (S/M/L/XL), numeric sizes, or estimated physical dimensions

4. **Color(s)** - Primary color and any secondary colors or patterns

5. **Condition** - Rate as one of:
   - New with tags (NWT)
   - New without tags (NWOT)
   - Like new/Excellent
   - Good (minor wear)
   - Fair (noticeable wear)
   - Poor (significant damage)

6. **Visible Defects/Wear** - Be specific about any:
   - Stains, marks, or discoloration
   - Scratches, dents, or cracks
   - Tears, holes, or fraying
   - Missing buttons, zippers, or parts
   - Fading or pilling

7. **Manufacturer/Model** - For electronics or branded items:
   - Model numbers
   - Version or generation
   - Serial numbers (if visible)

8. **Material** - If identifiable:
   - Fabric type (cotton, polyester, leather, wool)
   - Metal type (stainless steel, aluminum)
   - Other materials

9. **Special Features** - Notable details:
   - Number of pockets
   - Patterns (stripes, plaid, floral)
   - Button style, zipper type
   - Hardware color (gold, silver)
   - Lining details

Format your response conversationally, as if describing the item to someone who cannot see it.
For example: "This is a men's navy blue blazer from Ralph Lauren. It's a size Large and appears to be in excellent condition. The material looks like wool blend. I can see two front pockets and gold-colored buttons. There's a small fabric pull on the left sleeve, but otherwise no visible defects."

If the item is unclear or the image is blurry, mention that and suggest adjustments.
If you cannot identify certain details, say so honestly rather than guessing.
"""


class ItemRecognizer:
    """Recognizes e-commerce items in images using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the item recognizer.

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
        Analyze image bytes for e-commerce items.

        Args:
            image_bytes: JPEG image data

        Returns:
            str: Description of item for eBay listing
        """
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode('utf-8')
            }

            # Generate response
            response = self.model.generate_content([ECOMMERCE_ITEM_PROMPT, image_part])
            return response.text

        except Exception as e:
            return f"Sorry, I had trouble analyzing the image: {str(e)}"

    def analyze_image_file(self, filepath: str) -> str:
        """
        Analyze an image file for e-commerce items.

        Args:
            filepath: Path to image file

        Returns:
            str: Description of item for eBay listing
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
        Analyze a base64 encoded image for e-commerce items.

        Args:
            image_base64: Base64 encoded image data

        Returns:
            str: Description of item for eBay listing
        """
        try:
            image_bytes = base64.b64decode(image_base64)
            return self.analyze_image_bytes(image_bytes)
        except Exception as e:
            return f"Sorry, I had trouble decoding the image: {str(e)}"


# Global instance for easy access
_recognizer: Optional[ItemRecognizer] = None


def get_recognizer() -> ItemRecognizer:
    """Get or create the global item recognizer instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = ItemRecognizer()
    return _recognizer


def identify_item(image_bytes: Optional[bytes] = None,
                  image_path: Optional[str] = None,
                  camera=None) -> str:
    """
    Identify an item in an image. Convenience function for use as a tool.

    Args:
        image_bytes: Raw image bytes (optional)
        image_path: Path to image file (optional)
        camera: Camera instance to capture from (optional)

    Returns:
        str: Description of item for eBay listing
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
        print("Usage: python item_recognition.py <image_path>")
        print("       Analyzes an image file for e-commerce item details")
        sys.exit(1)

    image_path = sys.argv[1]
    print(f"Analyzing {image_path}...")

    try:
        result = identify_item(image_path=image_path)
        print("\nResult:")
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure GOOGLE_API_KEY environment variable is set")
