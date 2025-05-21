#!/bin/bash

set -e

# ===== CONFIGURATION =====
PROJECT_DIR="MyKivyApp"
APP_NAME="MyKivyApp"
PACKAGE_NAME="mykivyapp"
PACKAGE_DOMAIN="org.example"
REQUIREMENTS="python3,kivy"
ANDROID_NDK_PATH="/home/uidc1098/android/platform/android-ndk-r25b"

# ===== SCRIPT DIR =====
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# ===== CHECK IF PROJECT_DIR IS A FILE =====
if [ -e "$PROJECT_DIR" ] && [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: $PROJECT_DIR exists as a file. Please delete or rename it first."
    exit 1
fi

# ===== CREATE PROJECT DIR =====
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
else
    echo "Project directory already exists: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"


# ===== SYSTEM DEPENDENCIES =====
echo "Installing system dependencies..."
sudo apt update && sudo apt install -y \
    python3 python3-pip python3-venv python3-setuptools \
    git zip unzip openjdk-17-jdk libffi-dev libssl-dev \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libreadline-dev libsqlite3-dev libgdbm-dev \
    libbz2-dev libexpat1-dev liblzma-dev libgmp-dev

# ===== PYTHON TOOLS =====
echo "Installing Python tools..."
pip install --upgrade pip
pip install cython
pip install buildozer

# ===== INITIALIZE BUILDOZER =====
if [ ! -f "buildozer.spec" ]; then
    echo "Initializing buildozer..."
    buildozer init
fi

# ===== UPDATE buildozer.spec =====
echo "Updating buildozer.spec..."
sed -i "s/^title = .*/title = $APP_NAME/" buildozer.spec
sed -i "s/^package.name = .*/package.name = $PACKAGE_NAME/" buildozer.spec
sed -i "s/^package.domain = .*/package.domain = $PACKAGE_DOMAIN/" buildozer.spec
sed -i "s/^source.include_exts = .*/source.include_exts = py,png,jpg,kv,atlas/" buildozer.spec
sed -i "s/^requirements = .*/requirements = $REQUIREMENTS/" buildozer.spec
sed -i "s/^# *android.permissions = INTERNET/android.permissions = INTERNET/" buildozer.spec

# Set custom NDK path
if grep -q "^# *android.ndk_path" buildozer.spec; then
    sed -i "s|^# *android.ndk_path =.*|android.ndk_path = $ANDROID_NDK_PATH|" buildozer.spec
elif grep -q "^android.ndk_path" buildozer.spec; then
    sed -i "s|^android.ndk_path =.*|android.ndk_path = $ANDROID_NDK_PATH|" buildozer.spec
else
    echo "android.ndk_path = $ANDROID_NDK_PATH" >> buildozer.spec
fi

# ===== BUILD APK =====
echo "Building APK with local NDK path..."
buildozer -v android debug

echo "✅ APK build complete! Find it in: $PROJECT_DIR/bin/"
