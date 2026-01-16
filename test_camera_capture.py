#!/usr/bin/env python3
"""
Quick camera test - captures an image and saves it so you can see what the camera sees.
Useful for debugging when Gemini says "I don't see any banknotes".
"""

import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("📷 Camera Capture Test")
    print("=" * 40)
    
    # Get camera
    camera_type = os.getenv("CAMERA_TYPE", "usb").lower()
    
    if camera_type == "pi":
        from camera.pi_camera import PiCamera
        camera = PiCamera()
    else:
        from camera.usb_camera import USBCamera
        camera_index = int(os.getenv("USB_CAMERA_INDEX", 0))
        camera = USBCamera(camera_index)
    
    if not camera.is_available():
        print("❌ Camera not available!")
        if camera_type == "pi":
            print("   Check that:")
            print("   1. Pi Camera ribbon cable is connected properly")
            print("   2. picamera2 is installed for SYSTEM Python:")
            print("      sudo apt install python3-picamera2")
            print("   3. Test with: python3 -c \"from picamera2 import Picamera2; print('OK')\"")
        else:
            print("   Check that your USB camera is connected.")
        return
    
    print("✅ Camera found")
    print("\n📸 Capturing image...")
    
    image_bytes = camera.capture()
    
    if image_bytes is None:
        print("❌ Failed to capture image!")
        return
    
    # Save the image
    output_file = "camera_test.jpg"
    with open(output_file, 'wb') as f:
        f.write(image_bytes)
    
    print(f"✅ Captured {len(image_bytes)} bytes")
    print(f"✅ Saved to: {output_file}")
    print("")
    print("Now you can view this image to see what the camera sees!")
    print("Copy it to your computer:")
    print(f"   scp user@yourpi.local:~/AccessibilityHackathon/{output_file} .")
    
    camera.release()

if __name__ == "__main__":
    main()
