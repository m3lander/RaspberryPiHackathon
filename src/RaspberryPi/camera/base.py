"""
Abstract base class for camera implementations.
Allows easy swapping between USB camera and Pi Camera.
"""

from abc import ABC, abstractmethod
from typing import Optional
import base64


class CameraCapture(ABC):
    """Abstract base class for camera capture implementations."""
    
    @abstractmethod
    def capture(self) -> Optional[bytes]:
        """
        Capture an image from the camera.
        
        Returns:
            bytes: JPEG image data, or None if capture failed
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the camera is available and working.
        
        Returns:
            bool: True if camera is ready
        """
        pass
    
    def capture_base64(self) -> Optional[str]:
        """
        Capture an image and return as base64 encoded string.
        Useful for sending to APIs like Gemini.
        
        Returns:
            str: Base64 encoded JPEG image, or None if capture failed
        """
        image_bytes = self.capture()
        if image_bytes:
            return base64.b64encode(image_bytes).decode('utf-8')
        return None
    
    def save_capture(self, filepath: str) -> bool:
        """
        Capture an image and save to file.
        
        Args:
            filepath: Path to save the image
            
        Returns:
            bool: True if saved successfully
        """
        image_bytes = self.capture()
        if image_bytes:
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                return True
            except IOError as e:
                print(f"Error saving image: {e}")
        return False
