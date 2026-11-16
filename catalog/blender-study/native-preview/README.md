# Native ghost-overlay visual preview

The owner requested seeing the Blender animation as a ghost overlay in the app. This study
builds the current kit's actual recording view and APNG player in an isolated copy at
`/private/tmp/loca-ghost-native/VideoEditorKit`. Production files are unchanged.

`prepare.py` copies the current kit sources/demo, adds a DEBUG-only rendered-background source
and initial overlay selection, and exposes a study wrapper. The recording layout and player
come from `StepCameraView.swift`. The source hash and asset hash are in `preparation.json`.
The built app's APNG was verified byte-for-byte identical to the Blender export.
The original recording view changed after this snapshot (opacity-control presentation).
The native preview remains tied to its recorded source hash; `verification.json` records that
difference. This study did not write the original kit source.

The app has an isolated bundle ID, `io.snapads.ghost.study`, and launches directly into the
preview. It uses a rendered background because the Simulator has no live camera. The visible
sample badge makes that distinction explicit. The raw transparent APNG has no baked viewfinder;
the app supplies the fixed yellow sight. No second opacity multiplier is applied.

Two small player/viewfinder changes are included only in the copied source: an animation may
play without a tracking scenario, and animation mode keeps the app sight visible. The complete
change is reviewable in `StepCameraView-preview.patch`.

The installed Simulator SDK lacks the Cinematic framework. `simulator_compat.py` disables those
unrelated capture/editing features only in the copied project so this visual test can build.
Its changes are in `Simulator-compatibility.patch`; they are not proposed production changes.

Build passed for the installed iPhone 16 Pro / iOS 18.3 Simulator. The app was installed and
launched. `app-screen.png` and `app-preview.mp4` capture that native screen. The Simulator UI
application itself is absent from the installed Xcode bundle, so the screen recording is the
directly viewable artifact. The headless Simulator app is running.

This validates native APNG playback and the recording-screen layout, not real camera capture,
resource detection, device performance, exposure, sensor scoring or caught-state tinting.
The instruction loop is 5.6 seconds: a four-second take plus its next-shot handover.

To prepare the same isolated study, run `prepare.py`, then `simulator_compat.py`. Build using:

```sh
xcodebuild -project /private/tmp/loca-ghost-native/VideoEditorKit/Demo/VideoEditorDemo.xcodeproj -scheme VideoEditorDemo -configuration Debug -destination 'id=6D9ADF20-615B-459C-888A-A85317B9C493' -derivedDataPath /private/tmp/loca-ghost-native/DerivedData CODE_SIGNING_ALLOWED=NO PRODUCT_BUNDLE_IDENTIFIER=io.snapads.ghost.study 'INFOPLIST_KEY_CFBundleDisplayName=Ghost Guide Study'
```

The preparation scripts are for a fresh isolated copy. Avoid applying the compatibility
script repeatedly to an already patched copy. No production source or API publication is
performed by either script.
