#!/usr/bin/env python3
"""
Full Flow Test Script

Tests the complete pipeline without wake word:
1. Camera capture
2. Gemini analysis
3. ElevenLabs TTS output

This is useful for testing before the wake word is trained.

Usage:
    python test_full_flow.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def test_environment():
    """Check environment variables."""
    print("=" * 50)
    print("Checking Environment")
    print("=" * 50)
    
    checks = {
        "ELEVENLABS_API_KEY": bool(os.getenv("ELEVENLABS_API_KEY")),
        "ELEVENLABS_AGENT_ID": bool(os.getenv("ELEVENLABS_AGENT_ID")),
        "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
    }
    
    all_ok = True
    for var, ok in checks.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {var}")
        if not ok:
            all_ok = False
    
    return all_ok


def test_camera():
    """Test camera capture."""
    print("\n" + "=" * 50)
    print("Testing Camera")
    print("=" * 50)
    
    camera_type = os.getenv("CAMERA_TYPE", "usb")
    print(f"  Camera type: {camera_type}")
    
    if camera_type == "pi":
        from src.RaspberryPi.camera.pi_camera import PiCamera
        camera = PiCamera()
    else:
        from src.RaspberryPi.camera.usb_camera import USBCamera
        camera_index = int(os.getenv("USB_CAMERA_INDEX", 0))
        print(f"  Camera index: {camera_index}")
        camera = USBCamera(camera_index)
    
    if not camera.is_available():
        print("  ❌ Camera not available")
        return None, None
    
    print("  ✅ Camera available")
    
    print("  📸 Capturing image...")
    image_bytes = camera.capture()
    
    if image_bytes is None:
        print("  ❌ Failed to capture")
        return camera, None
    
    print(f"  ✅ Captured {len(image_bytes)} bytes")
    
    # Save for reference
    with open("test_flow_capture.jpg", "wb") as f:
        f.write(image_bytes)
    print("  💾 Saved to test_flow_capture.jpg")
    
    return camera, image_bytes


def test_gemini(image_bytes):
    """Test Gemini analysis."""
    print("\n" + "=" * 50)
    print("Testing Gemini Analysis")
    print("=" * 50)
    
    from src.RaspberryPi.tools.cash_recognition import CashRecognizer
    
    print("  🔍 Analyzing image...")
    
    try:
        recognizer = CashRecognizer()
        result = recognizer.analyze_image_bytes(image_bytes)
        
        print("\n  📝 Gemini says:")
        print("  " + "-" * 40)
        for line in result.split('\n'):
            print(f"  {line}")
        print("  " + "-" * 40)
        
        return result
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def test_elevenlabs_tts(text):
    """Test ElevenLabs text-to-speech."""
    print("\n" + "=" * 50)
    print("Testing ElevenLabs TTS")
    print("=" * 50)
    
    from elevenlabs.client import ElevenLabs
    import subprocess
    import tempfile
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    try:
        client = ElevenLabs(api_key=api_key)
        
        # Use a shorter text for test
        test_text = text[:200] if len(text) > 200 else text
        
        print(f"  🎙️ Generating speech for: '{test_text[:50]}...'")
        
        audio = client.text_to_speech.convert(
            text=test_text,
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            model_id="eleven_turbo_v2"
        )
        
        print("  ✅ Audio generated")
        print("  🔊 Playing...")
        
        # Save audio to temp file and play with mpv
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            for chunk in audio:
                f.write(chunk)
            temp_path = f.name
        
        subprocess.run(["mpv", "--no-video", temp_path], check=True, capture_output=True)
        os.unlink(temp_path)  # Clean up temp file
        
        print("  ✅ Playback complete")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_agent_connection():
    """Test connection to ElevenLabs agent."""
    print("\n" + "=" * 50)
    print("Testing Agent Connection")
    print("=" * 50)
    
    from elevenlabs.client import ElevenLabs
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    
    if not agent_id:
        print("  ⚠️ ELEVENLABS_AGENT_ID not set")
        print("  Create an agent first - see SETUP_AGENT.md")
        return False
    
    print(f"  Agent ID: {agent_id[:20]}...")
    
    try:
        client = ElevenLabs(api_key=api_key)
        # Just verify we can create client - actual connection happens on session start
        print("  ✅ ElevenLabs client created")
        print("  ℹ️ Full agent test requires running main.py with wake word")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("\n🔬 Cash Recognition - Full Flow Test")
    print("=" * 50)
    print("This tests all components without wake word detection")
    print("=" * 50)
    
    # Test environment
    if not test_environment():
        print("\n❌ Fix environment variables first")
        print("   Copy env.template to .env and fill in values")
        sys.exit(1)
    
    # Test camera
    camera, image_bytes = test_camera()
    
    if image_bytes is None:
        print("\n❌ Camera test failed")
        if camera:
            camera.release()
        sys.exit(1)
    
    # Test Gemini
    result = test_gemini(image_bytes)
    
    if result is None:
        print("\n❌ Gemini test failed")
        camera.release()
        sys.exit(1)
    
    # Test TTS
    print("\n🔊 Testing text-to-speech...")
    print("   (This will play audio through your speakers/headphones)")
    
    confirm = input("   Play audio? (y/n): ").strip().lower()
    if confirm == 'y':
        test_elevenlabs_tts(result)
    
    # Test agent connection
    test_agent_connection()
    
    # Cleanup
    camera.release()
    
    print("\n" + "=" * 50)
    print("✅ Full Flow Test Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Train the 'Hey Pi' wake word: python train_wakeword.py")
    print("  2. Create ElevenLabs agent: see SETUP_AGENT.md")
    print("  3. Run the full app: python main.py")


if __name__ == "__main__":
    main()
