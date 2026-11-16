"""Prepare an isolated native demo using the current kit's actual recording view."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SOURCE = Path('/Users/ihor.buts/Documents/Development/VideoEditorKit')
DEST = Path('/private/tmp/loca-ghost-native/VideoEditorKit')
DEST.mkdir(parents=True, exist_ok=True)
for directory in ['Sources', 'Tests', 'Demo']:
    target = DEST / directory
    if not target.exists():
        shutil.copytree(SOURCE / directory, target,
                        ignore=shutil.ignore_patterns('.build', 'DerivedData', 'xcuserdata', '*.xcuserstate'))
shutil.copy2(SOURCE / 'Package.swift', DEST / 'Package.swift')
relative = Path('Sources/VideoCaptureKit/StepCameraView.swift')
original = (SOURCE / relative).read_text()
updated = original


def replace(old, new):
    global updated
    assert updated.count(old) == 1, old[:90]
    updated = updated.replace(old, new)


replace('    let onDone: ([RecordedSegment]?) -> Void\n', '''    let onDone: ([RecordedSegment]?) -> Void
    #if DEBUG
    var previewBackgroundURL: URL? = nil
    #endif
''')
replace('''            CameraSurface(model: model)
                .ignoresSafeArea()''', '''            #if DEBUG
            if let previewBackgroundURL {
                StudyVideoBackground(url: previewBackgroundURL)
                    .aspectRatio(CameraSurface.videoAspect, contentMode: .fit)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .ignoresSafeArea()
            } else {
                CameraSurface(model: model).ignoresSafeArea()
            }
            #else
            CameraSurface(model: model).ignoresSafeArea()
            #endif''')
replace('''        .task {
            // Steps written for both cameras''', '''        .task {
            #if DEBUG
            if previewBackgroundURL != nil { return }
            #endif
            // Steps written for both cameras''')
replace('''        .task { guides = await loadGuides() }''', '''        .task {
            guides = await loadGuides()
            #if DEBUG
            if previewBackgroundURL != nil { guidePage = 1 }
            #endif
        }''')
replace('''if index > 0, index == page, let guide {''', '''if index > 0, index == page {''')
replace('''                            } else {
                                LiveGuidePage(guide: guide, showsModel: style == .model)''', '''                            } else if let guide {
                                LiveGuidePage(guide: guide, showsModel: style == .model)''')
replace('''if page > 0, guide == nil {''', '''if page > 0, guide == nil || style == .animation {''')
(DEST / relative).write_text(updated)
(HERE / 'StepCameraView-preview.patch').write_text(''.join(difflib.unified_diff(
    original.splitlines(True), updated.splitlines(True), fromfile=str(relative), tofile=str(relative))))
shutil.copy2(HERE / 'GhostOverlayStudyView.swift', DEST / 'Sources/VideoCaptureKit/GhostOverlayStudyView.swift')
app = DEST / 'Demo/VideoEditorDemo/VideoEditorDemoApp.swift'
app.write_text('''import SwiftUI
import VideoCaptureKit

@main
struct VideoEditorDemoApp: App {
    var body: some Scene {
        WindowGroup {
            if let overlay = Bundle.main.url(forResource: "ghost-study", withExtension: "png"),
               let background = Bundle.main.url(forResource: "ghost-background", withExtension: "mp4") {
                GhostOverlayStudyView(overlayURL: overlay, backgroundURL: background)
            } else {
                Text("Ghost study resources missing")
            }
        }
    }
}
''')
resources = app.parent
shutil.copy2(STUDY / 'bar_low_truckr_mm/guide.png', resources / 'ghost-study.png')
shutil.copy2(STUDY / 'bar_low_truckr_mm/lighting.mp4', resources / 'ghost-background.mp4')
report = dict(source=str(SOURCE), isolated_copy=str(DEST),
              original_recording_view_sha256=hashlib.sha256(original.encode()).hexdigest(),
              overlay_sha256=hashlib.sha256((resources / 'ghost-study.png').read_bytes()).hexdigest(),
              background='Rendered Blender reference; no live camera in Simulator',
              production_files_modified=False,
              preview_changes=['DEBUG-only background source and initial guide selection',
                               'Animation can play without a live-tracking scenario',
                               'App viewfinder remains visible in animation mode'])
(HERE / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
