#!/usr/bin/env python3
"""
eBay Item Recognition Voice Assistant

A keyboard-controlled assistant that helps identify items for eBay listings.
Press 'a' to start a conversation, 's' to cancel/no.

Usage:
    python main.py

Prerequisites:
    1. Set up .env file with API keys (see env.template)
    2. Create the ElevenLabs agent (see SETUP_AGENT.md)
    3. Connect USB camera (or Pi Camera 3)
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
        "GOOGLE_API_KEY": "Google Gemini API key",
        "ASTEROID_API_KEY": "Asteroid API key"
    }
    
    missing = []
    for var, description in required.items():
        if not os.getenv(var):
            missing.append(f"  - {var}: {description}")

    if not (os.getenv("ASTEROID_AGENT_ID") or os.getenv("AGENT_ID") or os.getenv("AGENT_PROFILE_ID")):
        missing.append(
            "  - ASTEROID_AGENT_ID/AGENT_ID/AGENT_PROFILE_ID: Asteroid Agent ID"
        )
    
    if missing:
        print("❌ Missing required environment variables:")
        print("\n".join(missing))
        print("\nCreate a .env file from env.template and fill in the values.")
        return False
    
    return True


def get_camera():
    """Get the appropriate camera based on configuration."""
    camera_type = os.getenv("CAMERA_TYPE", "usb").lower()
    
    if camera_type == "pi":
        from RaspberryPi.camera.pi_camera import PiCamera
        return PiCamera()
    else:
        from RaspberryPi.camera.usb_camera import USBCamera
        camera_index = int(os.getenv("USB_CAMERA_INDEX", 0))
        return USBCamera(camera_index)


# Global references for cleanup
conversation = None
camera = None


def cleanup():
    """Clean up resources."""
    global conversation, camera
    
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
    client_tools.register("create_listing", create_listing_tool_handler)
    
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
        from tools.geminiProductRecogniser import geminiProductRecogniser
        result = geminiProductRecogniser(image_bytes=image_bytes)
        
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
        from RaspberryPi.tools.item_recognition import identify_item
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


def create_listing_tool_handler(parameters: dict) -> str:
    """
    Client tool handler called by ElevenLabs when the agent invokes create_listing.
    The parameters dict may contain image_url if an external image URL is provided.
    """
    print(f"\n🔧 create_listing tool called with: {parameters}")
    image_url = parameters.get("image_url") if parameters else None
    return create_listing_tool(image_url=image_url)


def create_listing_tool(image_url: Optional[str] = None) -> str:
    """
    Client tool that captures an image, extracts item details, and creates an eBay listing
    using the Asteroid agent.
    """
    global camera

    print("📸 Capturing image for listing...")

    if camera is None:
        return "Sorry, the camera is not available. Please check the camera connection."

    # Capture image
    image_bytes = camera.capture()

    if image_bytes is None:
        return "Sorry, I couldn't capture an image. Please check the camera."

    print(f"📸 Captured {len(image_bytes)} bytes")

    # Extract structured item details with Gemini
    print("🔍 Extracting item details with Gemini...")

    try:
        from RaspberryPi.tools.item_recognition import get_item_details_for_listing
        item_details = get_item_details_for_listing(image_bytes=image_bytes)

        if "error" in item_details and item_details["error"]:
            print(f"❌ Error extracting details: {item_details['error']}")
            return f"Sorry, I had trouble analyzing the item: {item_details['error']}"

        print(f"🏷️ Item details: {item_details}")

        # Now send to Asteroid agent to create the listing
        print("🚀 Sending to Asteroid agent to create eBay listing...")

        from RaspberryPi.tools.asteroid_agent import create_ebay_listing
        result = create_ebay_listing(
            title=item_details.get("title", ""),
            price=item_details.get("price", ""),
            condition=item_details.get("condition", ""),
            description=item_details.get("description", ""),
            image_url=image_url
        )

        print(f"✅ Asteroid result: {result}")

        return result

    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, the Asteroid SDK is not installed. Please run: pip install asteroid-odyssey"
    except Exception as e:
        print(f"❌ Error creating listing: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I had trouble creating the listing: {str(e)}"


def get_key_input():
    """Get keyboard input without blocking."""
    import select
    import sys
    import tty
    import termios
    
    # Check if there's input available
    if select.select([sys.stdin], [], [], 0)[0]:
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            key = sys.stdin.read(1)
            return key.lower()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return None


def main():
    """Main application loop."""
    global conversation, camera
    
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
    
    print("\n" + "=" * 60)
    print("🎉 Ready! Press 'a' to start, 's' to cancel")
    print("=" * 60)
    print("\n⌨️  Waiting for key press...")
    print("   [a] = Start conversation")
    print("   [s] = Cancel/No")
    print("   [Ctrl+C] = Exit")
    
    convai_active = False
    
    while True:
        if not convai_active:
            try:
                # Check for keyboard input
                key = get_key_input()
                
                if key == 'a':
                    print("\n🎯 Start key pressed!")
                    
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
                        print("\n⌨️  Waiting for key press...")
                        print("   [a] = Start conversation")
                        print("   [s] = Cancel/No")
                        print("   [Ctrl+C] = Exit")
                
                elif key == 's':
                    print("\n❌ Cancel key pressed")
                
                # Small sleep to prevent busy waiting
                time.sleep(0.1)
                    
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(1)


if __name__ == "__main__":
    main()
