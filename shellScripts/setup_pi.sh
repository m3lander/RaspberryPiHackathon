#!/bin/bash
# Raspberry Pi Setup Script for Cash Recognition Assistant
# Run this on your Raspberry Pi to install all dependencies
#
# PREREQUISITES:
# 1. Python 3.11 installed via pyenv (see README.md Step 5)
# 2. Project files copied to ~/AccessibilityHackathon
#
# USAGE:
#   cd ~/AccessibilityHackathon
#   chmod +x setup_pi.sh
#   ./setup_pi.sh

set -e

echo ""
echo "=========================================="
echo "  Cash Recognition Assistant - Pi Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "   Make sure you're in the AccessibilityHackathon directory"
    echo ""
    echo "   Run: cd ~/AccessibilityHackathon"
    exit 1
fi

# Update system
echo "📦 Step 1/6: Updating system packages..."
sudo apt-get update

# Install system dependencies
echo ""
echo "📦 Step 2/6: Installing system dependencies..."
sudo apt-get install -y \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libasound-dev \
    libsndfile1-dev \
    python3-pip \
    python3-venv \
    ffmpeg \
    mpv \
    alsa-utils \
    libcap-dev \
    python3-picamera2

# Check Python version
echo ""
echo "🐍 Step 3/6: Checking Python version..."

# Try to use Python 3.11 from pyenv if available
if [ -f "$HOME/.pyenv/versions/3.11.9/bin/python" ]; then
    PYTHON_CMD="$HOME/.pyenv/versions/3.11.9/bin/python"
    echo "   ✅ Found Python 3.11.9 via pyenv"
elif [ -f "$HOME/.pyenv/versions/3.11.10/bin/python" ]; then
    PYTHON_CMD="$HOME/.pyenv/versions/3.11.10/bin/python"
    echo "   ✅ Found Python 3.11.10 via pyenv"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "   ✅ Found Python 3.11"
else
    # Check if system Python is 3.13 (incompatible with tflite-runtime)
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$PYTHON_VERSION" = "3.13" ]; then
        echo "   ❌ Error: Python 3.13 detected"
        echo ""
        echo "   The wake word library (tflite-runtime) requires Python 3.11."
        echo "   Please install Python 3.11 via pyenv first."
        echo ""
        echo "   Quick install commands:"
        echo ""
        echo "   # Install pyenv dependencies"
        echo "   sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \\"
        echo "     libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \\"
        echo "     libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev"
        echo ""
        echo "   # Install pyenv"
        echo "   curl https://pyenv.run | bash"
        echo ""
        echo "   # Add to shell"
        echo "   echo 'export PYENV_ROOT=\"\$HOME/.pyenv\"' >> ~/.bashrc"
        echo "   echo 'command -v pyenv >/dev/null || export PATH=\"\$PYENV_ROOT/bin:\$PATH\"' >> ~/.bashrc"
        echo "   echo 'eval \"\$(pyenv init -)\"' >> ~/.bashrc"
        echo "   source ~/.bashrc"
        echo ""
        echo "   # Install Python 3.11 (takes 5-10 minutes)"
        echo "   pyenv install 3.11.9"
        echo ""
        echo "   Then run this script again: ./setup_pi.sh"
        exit 1
    else
        PYTHON_CMD="python3"
        echo "   ✅ Using system Python: $PYTHON_VERSION"
    fi
fi

# Create virtual environment
echo ""
echo "🐍 Step 4/6: Creating Python virtual environment..."
$PYTHON_CMD -m venv .venv
source .venv/bin/activate

echo "   Python version: $(python --version)"

# Upgrade pip
pip install --upgrade pip --quiet

# Install Python dependencies
echo ""
echo "📦 Step 5/6: Installing Python packages..."
echo "   This may take a few minutes..."

pip install --quiet tflite-runtime
pip install --quiet librosa EfficientWord-Net
pip install --quiet "elevenlabs[pyaudio]"
pip install --quiet google-generativeai opencv-python-headless python-dotenv

# Create .env from template if it doesn't exist
echo ""
echo "📝 Step 6/6: Setting up configuration..."

if [ ! -f .env ]; then
    cp env.template .env
    echo "   Created .env from template"
else
    echo "   .env already exists (not overwriting)"
fi

# Create directories if they don't exist
mkdir -p hotword_training_audio
mkdir -p hotword_refs

echo ""
echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Configure audio device:"
echo "     Run: aplay -l"
echo "     Note your USB headphones card number (e.g., 3)"
echo "     Then create ~/.asoundrc (see README.md Step 7)"
echo ""
echo "  2. Test audio:"
echo "     speaker-test -c 2 -t wav -D hw:3,0"
echo "     (Replace 3 with your card number)"
echo ""
echo "  3. Add API keys:"
echo "     nano .env"
echo ""
echo "  4. Train wake word:"
echo "     source .venv/bin/activate"
echo "     python train_wakeword.py"
echo ""
echo "  5. Create ElevenLabs agent:"
echo "     See SETUP_AGENT.md"
echo ""
echo "  6. Test camera + Gemini:"
echo "     python test_camera_gemini.py"
echo ""
echo "  7. Run the assistant:"
echo "     python main.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""
