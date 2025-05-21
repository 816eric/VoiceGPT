#!/bin/bash

set -e

PROJECT_DIR="$(pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "🧹 Cleaning old Buildozer"

# 1. Remove all previous build caches
rm -rf .buildozer
rm -rf ~/.buildozer
rm -rf ~/.local/share/python-for-android

# 2. Blacklist pyjnius globally (to stop forced build)
#echo "🛑 Blacklisting pyjnius..."
#mkdir -p ~/.p4a
#echo "pyjnius" > ~/.p4a/blacklist.txt

# 3. Set up virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "♻️ Removing old virtualenv..."
    rm -rf "$VENV_DIR"
fi

echo "🐍 Creating fresh Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

#export ANDROID_HOME=/home/uidc1098/android
#export PATH=$ANDROID_HOME/platform/android-sdk/tools/bin:$PATH

# 4. Upgrade pip and install dependencies
echo "📦 Installing Buildozer and Cython into venv..."
pip install --upgrade pip setuptools wheel
pip install cython buildozer
pip install Cython==0.29.36 pyjnius

# 5. Check that buildozer.spec exists and is correct
if [ ! -f "buildozer.spec" ]; then
    echo "📝 Generating buildozer.spec..."
    buildozer init
fi

# 6. Start Buildozer build
echo "🚀 Running Buildozer build in virtualenv..."
buildozer -v android debug

# STEP 2: Fix gradle-wrapper.properties
WRAPPER_FILE=$(find .buildozer/android/platform/build-* -name gradle-wrapper.properties | head -n 1)

if [ -f "$WRAPPER_FILE" ]; then
    echo "🛠️  Patching gradle-wrapper.properties at: $WRAPPER_FILE"
    sed -i 's|distributionUrl=.*|distributionUrl=file:///home/uidc1098/app/gradle-8.0.2-all.zip|' "$WRAPPER_FILE"
else
    echo "❌ Could not find gradle-wrapper.properties. Build may have failed."
    exit 1
fi

# STEP 3: Manually run gradle
DIST_DIR=$(dirname "$WRAPPER_FILE")/..
cd "$DIST_DIR"
echo "🏗️  Running Gradle to build APK..."
cd /home/uidc1098/app/MyKivyApp/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/mykivyapp
./gradlew clean assembleDebug

echo "✅ Done! Your APK is located in: $PROJECT_DIR/bin/"
