#!/usr/bin/env python3
"""
Test script for Camera + Gemini integration.
Run this to verify camera capture and Gemini banknote recognition work together.

Usage:
    python test_camera_gemini.py

Make sure to:
1. Set GOOGLE_API_KEY environment variable
2. Have USB camera connected
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_camera():
    """Test USB camera capture."""
    print("=" * 50)
    print("Testing USB Camera")
    print("=" * 50)
    
    from camera.usb_camera import USBCamera, list_available_cameras
    
    # List available cameras
    print("\nSearching for available cameras...")
    cameras = list_available_cameras()
    
    if not cameras:
        print("❌ No cameras found!")
        print("   Make sure your USB camera is connected.")
        return None
    
    print(f"✅ Found cameras at indices: {cameras}")
    
    # Get camera index from env or use first available
    camera_index = int(os.getenv("USB_CAMERA_INDEX", cameras[0]))
    print(f"\nUsing camera at index {camera_index}")
    
    # Create camera and test capture
    camera = USBCamera(camera_index)
    
    if not camera.is_available():
        print(f"❌ Camera at index {camera_index} is not available")
        return None
    
    print("✅ Camera is available")
    
    # Capture test image
    print("\nCapturing test image...")
    image_bytes = camera.capture()
    
    if image_bytes is None:
        print("❌ Failed to capture image")
        return None
    
    print(f"✅ Captured image: {len(image_bytes)} bytes")
    
    # Save test image
    test_path = "test_capture.jpg"
    with open(test_path, 'wb') as f:
        f.write(image_bytes)
    print(f"✅ Saved to {test_path}")
    
    return image_bytes


def test_gemini(image_bytes: bytes):
    """Test Gemini banknote recognition."""
    print("\n" + "=" * 50)
    print("Testing Gemini Banknote Recognition")
    print("=" * 50)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set!")
        print("   Set it with: export GOOGLE_API_KEY=your_key_here")
        return False
    
    print("✅ GOOGLE_API_KEY is set")
    
    from tools.cash_recognition import CashRecognizer
    
    print("\nInitializing Gemini...")
    try:
        recognizer = CashRecognizer(api_key)
        print("✅ Gemini initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini: {e}")
        return False
    
    print("\nAnalyzing image for banknotes...")
    print("(This may take a few seconds)")
    
    try:
        result = recognizer.analyze_image_bytes(image_bytes)
        print("\n" + "-" * 50)
        print("GEMINI RESPONSE:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        return False


def test_full_pipeline():
    """Test the complete camera + Gemini pipeline."""
    print("\n" + "=" * 50)
    print("Testing Full Pipeline")
    print("=" * 50)
    
    from camera.usb_camera import USBCamera
    from tools.cash_recognition import identify_cash
    
    camera_index = int(os.getenv("USB_CAMERA_INDEX", 0))
    camera = USBCamera(camera_index)
    
    print("\nRunning identify_cash with camera...")
    result = identify_cash(camera=camera)
    
    print("\n" + "-" * 50)
    print("RESULT:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    camera.release()
    return True


def main():
    print("\n🔍 Cash Recognition System - Camera + Gemini Test")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  GOOGLE_API_KEY not set. Gemini tests will fail.")
        print("   Set it with: export GOOGLE_API_KEY=your_key_here")
    
    # Test camera
    image_bytes = test_camera()
    
    if image_bytes is None:
        print("\n❌ Camera test failed. Fix camera issues before continuing.")
        sys.exit(1)
    
    # Test Gemini with captured image
    if os.getenv("GOOGLE_API_KEY"):
        gemini_ok = test_gemini(image_bytes)
        
        if gemini_ok:
            # Test full pipeline
            test_full_pipeline()
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. If camera works: ✅")
    print("2. If Gemini works: ✅") 
    print("3. Now set up the wake word and ElevenLabs agent")
    print("\nTo test with a banknote:")
    print("   Hold a £5, £10, £20, or £50 note in front of the camera")
    print("   and run this script again.")


if __name__ == "__main__":
    main()
