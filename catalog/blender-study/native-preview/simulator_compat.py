"""Disable unavailable Cinematic features only in the isolated visual study.

The Simulator SDK here has no Cinematic module. Ghost playback itself needs none.
Production kit sources are never modified by this preparation script.
"""
from pathlib import Path
import difflib

ROOT = Path('/private/tmp/loca-ghost-native/VideoEditorKit')
HERE = Path(__file__).resolve().parent
patches = []


def edit(relative, transform):
    path = ROOT / relative
    original = path.read_text()
    updated = transform(original)
    path.write_text(updated)
    patches.extend(difflib.unified_diff(original.splitlines(True), updated.splitlines(True),
                                      fromfile=relative, tofile=relative))


def renderer(original):
    start = original.index('    static func sourcePoint(')
    end = original.index('\n    /// The frame in a format', start)
    source_point = original[start:end]
    fallback = '''
import AVFoundation
import CoreVideo
import ImageIO
import VideoEditorModel
enum StudyCinematicQuality { case preview, export }
final class CinematicClipRenderer: @unchecked Sendable {
    let orientation = CGImagePropertyOrientation.up
    static func make(url: URL, quality: StudyCinematicQuality) async -> CinematicClipRenderer? { nil }
    static func isCinematic(_ url: URL) async -> Bool { false }
    static func debugLog(_ line: String) {}
    func render(image: CVPixelBuffer, disparity: CVPixelBuffer, metadata: AVTimedMetadataGroup,
                sourceTime: CMTime, depth: DepthEffect) -> CVPixelBuffer? { nil }
''' + source_point + '''
}
public enum DepthCapability {
    public static func isCinematic(_ url: URL) async -> Bool { false }
    public static func sourcePoint(_ point: NormalizedPoint, orientation: CGImagePropertyOrientation) -> CGPoint {
        CinematicClipRenderer.sourcePoint(point, orientation: orientation)
    }
}
'''
    return '#if canImport(Cinematic)\n' + original + '\n#else\n' + fallback + '\n#endif\n'


edit('Sources/VideoEditorEngine/CinematicClipRenderer.swift', renderer)


def composition(original):
    start = original.index('        let added = composition.addTracks(for: renderer.info')
    end = original.index('\n    }', start)
    return original[:start] + '        #if canImport(Cinematic)\n' + original[start:end] + '\n        #else\n        return nil\n        #endif' + original[end:]


edit('Sources/VideoEditorEngine/CompositionBuilder.swift', composition)
edit('Sources/AutoEdit/Analysis/ClipAnalyzer.swift', lambda t: t.replace('import Cinematic', '#if canImport(Cinematic)\nimport Cinematic\n#endif').replace(
    'isCinematic: await CNAssetInfo.isCinematic(asset: asset)', 'isCinematic: false /* Simulator visual study only */'))
edit('Sources/VideoCaptureKit/CinematicProbe.swift', lambda t: '#if canImport(Cinematic)\n' + t + '''
#else
import Foundation
enum CinematicProbe { static func run(_ url: URL) {} }
#endif
''')
(HERE / 'Simulator-compatibility.patch').write_text(''.join(patches))
print('Cinematic features disabled only in the isolated Simulator preview.')
