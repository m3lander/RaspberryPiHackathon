#!/usr/bin/env python3
"""
eBay Item Recognition Voice Assistant

A voice-activated assistant that helps identify items for eBay listings.
Say "Hey Pi" to activate, then show an item for detailed description.

Usage:
    python main.py

Prerequisites:
    1. Set up .env file with API keys (see env.template)
    2. Train the "Hey Pi" wake word (run train_wakeword.py)
    3. Create the ElevenLabs agent (see SETUP_AGENT.md)
    4. Connect USB camera (or Pi Camera 3)
"""

import os
import sys
import signal
import time
from typing import Optional

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


def check_environment():
    """Check that all required environment variables are set."""
    required = {
        "ELEVENLABS_API_KEY": "ElevenLabs API key",
        "ELEVENLABS_AGENT_ID": "ElevenLabs Agent ID", 
        "GOOGLE_API_KEY": "Google Gemini API key"
    }
    
    missing = []
    for var, description in required.items():
        if not os.getenv(var):
            missing.append(f"  - {var}: {description}")
    
    if missing:
        print("❌ Missing required environment variables:")
        print("\n".join(missing))
        print("\nCreate a .env file from env.template and fill in the values.")
        return False
    
    return True


def check_wake_word_file():
    """Check if the wake word reference file exists."""
    ref_file = os.getenv("WAKE_WORD_REF", "hotword_refs/hey_pi_ref.json")
    
    if not os.path.exists(ref_file):
        print(f"❌ Wake word file not found: {ref_file}")
        print("\nRun the training script first:")
        print("    python train_wakeword.py")
        return False
    
    return True


def get_camera():
    """Get the appropriate camera based on configuration."""
    camera_type = os.getenv("CAMERA_TYPE", "usb").lower()
    
    if camera_type == "pi":
        from camera.pi_camera import PiCamera
        return PiCamera()
    else:
        from camera.usb_camera import USBCamera
        camera_index = int(os.getenv("USB_CAMERA_INDEX", 0))
        return USBCamera(camera_index)


# Global references for cleanup
conversation = None
mic_stream = None
camera = None


def cleanup():
    """Clean up resources."""
    global conversation, mic_stream, camera
    
    if conversation:
        try:
            conversation.end_session()
        except Exception:
            pass
    
    if camera:
        try:
            camera.release()
        except Exception:
            pass
    
    print("\nCleanup complete.")


def signal_handler(sig, frame):
    """Handle interrupt signal gracefully."""
    print("\n\nReceived interrupt signal, shutting down...")
    cleanup()
    sys.exit(0)


def create_conversation(elevenlabs, agent_id, requires_auth):
    """Create a new conversation instance with the client tool."""
    from elevenlabs.conversational_ai.conversation import Conversation, ClientTools
    from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
    
    # Register client tools
    client_tools = ClientTools()
    client_tools.register("identify_cash", identify_cash_tool_handler)
    client_tools.register("identify_item", identify_item_tool_handler)
    client_tools.register("read_packaging", read_packaging_tool_handler)
    client_tools.register("describe_image", describe_image_tool_handler)
    
    return Conversation(
        client=elevenlabs,
        agent_id=agent_id,
        requires_auth=requires_auth,
        audio_interface=DefaultAudioInterface(),
        client_tools=client_tools,
        # Callbacks
        callback_agent_response=lambda response: print(f"🤖 Agent: {response}"),
        callback_agent_response_correction=lambda orig, corrected: print(f"🤖 Agent: {corrected}"),
        callback_user_transcript=lambda transcript: print(f"👤 User: {transcript}"),
    )


def identify_cash_tool_handler(parameters: dict) -> str:
    """
    Client tool handler called by ElevenLabs when the agent invokes identify_cash.
    The parameters dict comes from the agent (can be empty for this tool).
    """
    print(f"\n🔧 identify_cash tool called with: {parameters}")
    return identify_cash_tool()


def identify_cash_tool() -> str:
    """
    Client tool that captures an image and identifies banknotes.
    This is called by the ElevenLabs agent when the user asks about cash.
    """
    global camera
    
    print("📸 Capturing image...")
    
    if camera is None:
        return "Sorry, the camera is not available. Please check the camera connection."
    
    # Capture image
    image_bytes = camera.capture()
    
    if image_bytes is None:
        return "Sorry, I couldn't capture an image. Please check the camera."
    
    print(f"📸 Captured {len(image_bytes)} bytes")
    
    # Analyze with Gemini
    print("🔍 Analyzing image with Gemini...")
    
    try:
        from tools.cash_recognition import identify_cash
        result = identify_cash(image_bytes=image_bytes)
        
        print(f"💰 Result: {result}")
        
        return result
    except Exception as e:
        print(f"❌ Error identifying cash: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I had trouble identifying the cash: {str(e)}"


def identify_item_tool_handler(parameters: dict) -> str:
    """
    Client tool handler called by ElevenLabs when the agent invokes identify_item.
    The parameters dict comes from the agent (can be empty for this tool).
    """
    print(f"\n🔧 identify_item tool called with: {parameters}")
    return identify_item_tool()


def identify_item_tool() -> str:
    """
    Client tool that captures an image and identifies e-commerce items.
    This is called by the ElevenLabs agent when the user asks about an item for eBay.
    """
    global camera

    print("📸 Capturing image...")

    if camera is None:
        return "Sorry, the camera is not available. Please check the camera connection."

    # Capture image
    image_bytes = camera.capture()

    if image_bytes is None:
        return "Sorry, I couldn't capture an image. Please check the camera."

    print(f"📸 Captured {len(image_bytes)} bytes")

    # Analyze with Gemini
    print("🔍 Analyzing item with Gemini...")

    try:
        from tools.item_recognition import identify_item
        result = identify_item(image_bytes=image_bytes)

        print(f"🏷️ Result: {result}")

        return result
    except Exception as e:
        print(f"❌ Error identifying item: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I had trouble identifying the item: {str(e)}"


def read_packaging_tool_handler(parameters: dict) -> str:
    """
    Client tool handler called by ElevenLabs when the agent invokes read_packaging.
    The parameters dict comes from the agent (can be empty for this tool).
    """
    print(f"\n🔧 read_packaging tool called with: {parameters}")
    return read_packaging_tool()


def read_packaging_tool() -> str:
    """
    Client tool that captures an image and reads text from packaging.
    This is called by the ElevenLabs agent when the user asks about labels/ingredients.
    """
    global camera
    
    print("📸 Capturing image...")
    
    if camera is None:
        return "Sorry, the camera is not available. Please check the camera connection."
    
    # Capture image
    image_bytes = camera.capture()
    
    if image_bytes is None:
        return "Sorry, I couldn't capture an image. Please check the camera."
    
    print(f"📸 Captured {len(image_bytes)} bytes")
    
    # Analyze with Gemini
    print("🔍 Reading packaging with Gemini...")
    
    try:
        from tools.packaging_reader import read_packaging
        result = read_packaging(image_bytes=image_bytes)
        
        print(f"📦 Result: {result}")
        
        return result
    except Exception as e:
        print(f"❌ Error reading packaging: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I had trouble reading the packaging: {str(e)}"


def describe_image_tool_handler(parameters: dict) -> str:
    """
    Client tool handler called by ElevenLabs when the agent invokes describe_image.
    The parameters dict comes from the agent (can be empty for this tool).
    """
    print(f"\n🔧 describe_image tool called with: {parameters}")
    return describe_image_tool()


def describe_image_tool() -> str:
    """
    Client tool that captures an image and provides a detailed visual description.
    This is called by the ElevenLabs agent when the user asks for a general description
    of what they're looking at.
    """
    global camera
    
    print("📸 Capturing image...")
    
    if camera is None:
        return "Sorry, the camera is not available. Please check the camera connection."
    
    # Capture image
    image_bytes = camera.capture()
    
    if image_bytes is None:
        return "Sorry, I couldn't capture an image. Please check the camera."
    
    print(f"📸 Captured {len(image_bytes)} bytes")
    
    # Analyze with VisualAnalysis
    print("🔍 Analyzing image with VisualAnalysis...")
    
    try:
        import sys
        import os
        # Add src directory to path to import VisualAnalysis
        src_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        from VisualAnalysis.analysis import describe_image
        result = describe_image(image_bytes=image_bytes)
        
        print(f"👁️ Result: {result}")
        
        return result
    except Exception as e:
        print(f"❌ Error describing image: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I had trouble describing the image: {str(e)}"


def start_mic_stream():
    """Start the microphone stream for wake word detection."""
    global mic_stream
    
    from eff_word_net.streams import SimpleMicStream
    
    try:
        mic_stream = SimpleMicStream(
            window_length_secs=1.5,
            sliding_window_secs=0.75,
        )
        mic_stream.start_stream()
        print("🎤 Microphone stream started")
        return True
    except Exception as e:
        print(f"❌ Error starting microphone: {e}")
        mic_stream = None
        return False


def stop_mic_stream():
    """Stop the microphone stream."""
    global mic_stream
    mic_stream = None
    print("🎤 Microphone stream stopped")


def main():
    """Main application loop."""
    global conversation, mic_stream, camera
    
    print("\n" + "=" * 60)
    print("🏷️ eBay Item Recognition Voice Assistant")
    print("=" * 60)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check environment
    print("\n📋 Checking configuration...")
    
    if not check_environment():
        sys.exit(1)
    print("✅ Environment variables set")
    
    if not check_wake_word_file():
        sys.exit(1)
    print("✅ Wake word file found")
    
    # Initialize camera
    print("\n📷 Initializing camera...")
    camera = get_camera()
    
    if not camera.is_available():
        camera_type = os.getenv("CAMERA_TYPE", "usb").lower()
        print("❌ Camera not available!")
        if camera_type == "pi":
            print("   Check that:")
            print("   1. Pi Camera ribbon cable is connected properly")
            print("   2. Camera is enabled in raspi-config")
            print("   3. picamera2 is installed: sudo apt install python3-picamera2")
        else:
            print("   Check that your USB camera is connected.")
        sys.exit(1)
    print("✅ Camera ready")
    
    # Initialize ElevenLabs
    print("\n🎙️ Initializing ElevenLabs...")
    from elevenlabs.client import ElevenLabs
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    
    elevenlabs = ElevenLabs(api_key=api_key)
    print("✅ ElevenLabs client ready")
    
    # Initialize wake word detector
    print("\n👂 Initializing wake word detector...")
    from eff_word_net.engine import HotwordDetector
    from eff_word_net.audio_processing import Resnet50_Arc_loss
    
    ref_file = os.getenv("WAKE_WORD_REF", "hotword_refs/hey_pi_ref.json")
    threshold = float(os.getenv("WAKE_WORD_THRESHOLD", "0.7"))
    
    base_model = Resnet50_Arc_loss()
    hotword_detector = HotwordDetector(
        hotword="hey_pi",
        model=base_model,
        reference_file=ref_file,
        threshold=threshold,
        relaxation_time=2
    )
    print("✅ Wake word detector ready")
    
    # Start microphone
    if not start_mic_stream():
        print("❌ Could not start microphone")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Ready! Say 'Hey Pi' to start a conversation")
    print("=" * 60)
    print("\nListening for wake word...")
    
    convai_active = False
    
    while True:
        if not convai_active:
            try:
                # Make sure mic stream is active
                if mic_stream is None:
                    time.sleep(1)
                    start_mic_stream()
                    continue
                
                # Get audio frame and check for wake word
                frame = mic_stream.getFrame()
                result = hotword_detector.scoreFrame(frame)
                
                if result is None:
                    # No voice activity
                    continue
                
                if result["match"]:
                    print(f"\n🎯 Wake word detected! (confidence: {result['confidence']:.2f})")
                    
                    # Stop mic stream to avoid conflicts
                    stop_mic_stream()
                    
                    # Start conversation
                    print("📞 Starting conversation...")
                    convai_active = True
                    
                    try:
                        # Create conversation
                        conversation = create_conversation(
                            elevenlabs,
                            agent_id,
                            requires_auth=bool(api_key)
                        )
                        
                        # Start session
                        conversation.start_session()
                        
                        # Wait for session to end
                        conversation_id = conversation.wait_for_session_end()
                        print(f"\n📞 Conversation ended (ID: {conversation_id})")
                        
                    except Exception as e:
                        print(f"❌ Conversation error: {e}")
                    
                    finally:
                        # Cleanup
                        convai_active = False
                        conversation = None
                        print("\n" + "-" * 40)
                        
                        # Restart mic stream
                        time.sleep(1)
                        start_mic_stream()
                        print("\n🎧 Listening for wake word...")
                    
            except Exception as e:
                print(f"❌ Error in wake word detection: {e}")
                mic_stream = None
                time.sleep(1)
                start_mic_stream()


if __name__ == "__main__":
    main()
