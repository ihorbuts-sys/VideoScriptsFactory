#!/bin/zsh
# Builds "Scriptwriter Server.app" into ~/Applications and launches it.
set -e
HERE=${0:A:h}
APP="$HOME/Applications/Scriptwriter Server.app"
mkdir -p "$APP/Contents/MacOS"
swiftc -O -o "$APP/Contents/MacOS/ScriptwriterMenu" "$HERE/ScriptwriterMenu.swift"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>ScriptwriterMenu</string>
    <key>CFBundleIdentifier</key><string>local.videoeditorkit.scriptwriter-menu</string>
    <key>CFBundleName</key><string>Scriptwriter Server</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleShortVersionString</key><string>1.0</string>
    <key>LSMinimumSystemVersion</key><string>13.0</string>
    <key>LSUIElement</key><true/>
    <key>NSAppTransportSecurity</key><dict><key>NSAllowsLocalNetworking</key><true/></dict>
</dict>
</plist>
PLIST
codesign --force --sign - "$APP"
pkill -x ScriptwriterMenu || true
open "$APP"
echo "Built and launched $APP"
