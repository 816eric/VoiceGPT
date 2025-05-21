

set -e

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
