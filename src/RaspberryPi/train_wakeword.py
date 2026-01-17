#!/usr/bin/env python3
"""
Wake Word Training Script for "Hey Pi"

This script helps you train a custom wake word using EfficientWord-Net.

Prerequisites:
1. You need 4+ audio files of "Hey Pi" in the hotword_training_audio/ folder
   (MP3, M4A, or WAV format - MP3/M4A will be auto-converted to WAV)
2. Install dependencies: pip install EfficientWord-Net librosa tflite-runtime

Usage:
    python train_wakeword.py

The script will generate hotword_refs/hey_pi_ref.json
"""

import os
import sys
import subprocess
import glob


def check_audio_files():
    """Check if training audio files exist."""
    audio_dir = "../../assets/hotword_training_audio"
    
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        return [], []
    
    # Look for audio files (various formats)
    audio_extensions = ('.wav', '.mp3', '.m4a', '.ogg', '.flac')
    all_files = [
        f for f in os.listdir(audio_dir) 
        if f.lower().endswith(audio_extensions)
    ]
    
    wav_files = [f for f in all_files if f.lower().endswith('.wav')]
    non_wav_files = [f for f in all_files if not f.lower().endswith('.wav')]
    
    return wav_files, non_wav_files


def convert_to_wav(audio_dir="hotword_training_audio"):
    """Convert non-WAV audio files to 16kHz mono WAV format."""
    non_wav_extensions = ('.mp3', '.m4a', '.ogg', '.flac')
    converted = []
    
    for ext in non_wav_extensions:
        pattern = os.path.join(audio_dir, f"*{ext}")
        files = glob.glob(pattern)
        
        for input_file in files:
            # Create output filename
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.wav"
            
            # Skip if WAV already exists
            if os.path.exists(output_file):
                print(f"  ⏭️  Skipping {os.path.basename(input_file)} (WAV exists)")
                continue
            
            print(f"  🔄 Converting {os.path.basename(input_file)}...")
            
            try:
                # Use ffmpeg to convert to 16kHz mono WAV
                cmd = [
                    "ffmpeg", "-y", "-i", input_file,
                    "-ar", "16000",  # 16kHz sample rate
                    "-ac", "1",      # Mono
                    output_file
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                converted.append(output_file)
                print(f"  ✅ Created {os.path.basename(output_file)}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to convert {os.path.basename(input_file)}: {e}")
            except FileNotFoundError:
                print("  ❌ ffmpeg not found! Install with: sudo apt-get install ffmpeg")
                return []
    
    return converted


def generate_with_elevenlabs():
    """Instructions for generating audio with ElevenLabs."""
    print("\n" + "=" * 60)
    print("OPTION A: Generate 'Hey Pi' audio with ElevenLabs TTS")
    print("=" * 60)
    print("""
1. Go to: https://elevenlabs.io/app/speech-synthesis/text-to-speech

2. Type: Hey Pi

3. Generate with 4 DIFFERENT voices:
   - Select a voice (e.g., "Rachel")
   - Click "Generate"
   - Download the audio
   - Repeat with 3 more different voices
   
4. Save the files to: hotword_training_audio/
   (MP3 format is fine - they will be auto-converted to WAV)

5. Run this script again to train the wake word
""")


def record_yourself():
    """Instructions for recording your own audio."""
    print("\n" + "=" * 60)
    print("OPTION B: Record yourself saying 'Hey Pi'")
    print("=" * 60)
    print("""
1. Record yourself saying "Hey Pi" clearly, 4 separate times

2. Tips for good recordings:
   - Use a quiet room
   - Speak naturally (not too fast, not too slow)
   - Make each recording about 1-2 seconds long
   - Try slight variations in tone

3. Save the files to: hotword_training_audio/
   (MP3, M4A, or WAV format)

4. Run this script again to train the wake word
""")


def train_wakeword():
    """Run the EfficientWord-Net training."""
    print("\n" + "=" * 60)
    print("Training 'Hey Pi' Wake Word")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("hotword_refs", exist_ok=True)
    
    # Run the training command
    cmd = [
        sys.executable, "-m", "eff_word_net.generate_reference",
        "--input-dir", "hotword_training_audio",
        "--output-dir", "hotword_refs", 
        "--wakeword", "hey_pi",
        "--model-type", "resnet_50_arc"
    ]
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        # Check if output file was created
        output_file = "hotword_refs/hey_pi_ref.json"
        if os.path.exists(output_file):
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Wake word trained!")
            print("=" * 60)
            print(f"\nGenerated: {output_file}")
            print("\nYou can now run the main application:")
            print("    python main.py")
            return True
        else:
            print("\n❌ Training completed but output file not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ EfficientWord-Net not installed!")
        print("   Install with: pip install EfficientWord-Net librosa tflite-runtime")
        return False


def main():
    print("\n🎤 Hey Pi - Wake Word Training")
    print("=" * 60)
    
    # Check for existing audio files
    wav_files, non_wav_files = check_audio_files()
    total_files = len(wav_files) + len(non_wav_files)
    
    if total_files < 4:
        print(f"\n⚠️  Found {total_files} audio file(s), need at least 4")
        print("\nYou need to create training audio first.")
        print("\nChoose an option:")
        print("  A) Generate audio using ElevenLabs TTS (recommended)")
        print("  B) Record yourself saying 'Hey Pi'")
        
        choice = input("\nEnter A or B: ").strip().upper()
        
        if choice == 'A':
            generate_with_elevenlabs()
        else:
            record_yourself()
        
        print("\n" + "-" * 60)
        print("After creating the audio files, run this script again.")
        return
    
    print(f"\n✅ Found {total_files} audio files:")
    for f in wav_files:
        print(f"   - {f} (WAV)")
    for f in non_wav_files:
        print(f"   - {f} (will convert to WAV)")
    
    # Convert non-WAV files to WAV
    if non_wav_files:
        print("\n🔄 Converting audio files to WAV format (16kHz mono)...")
        converted = convert_to_wav()
        
        # Recheck WAV files
        wav_files, _ = check_audio_files()
        print(f"\n✅ Now have {len(wav_files)} WAV files ready for training")
    
    if len(wav_files) < 4:
        print(f"\n❌ Need at least 4 WAV files, but only have {len(wav_files)}")
        print("   Make sure audio conversion succeeded.")
        return
    
    print("\nReady to train!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm == 'y':
        train_wakeword()
    else:
        print("Training cancelled.")


if __name__ == "__main__":
    main()
