// Print the face rectangle and eye midpoint of each image given on the command
// line, as one JSON object per line, in pixels with the origin at the top left.
// Used by make_thumbnails.py to crop consistent square portraits.

import Foundation
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    let esc = path.replacingOccurrences(of: "\"", with: "\\\"")
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("{\"path\":\"\(esc)\",\"error\":\"cannot load\"}")
        continue
    }
    let w = CGFloat(cg.width), h = CGFloat(cg.height)
    let request = VNDetectFaceLandmarksRequest()
    do {
        try VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
    } catch {
        print("{\"path\":\"\(esc)\",\"error\":\"vision failed\"}")
        continue
    }

    var faces: [String] = []
    for face in (request.results ?? []) {
        let box = face.boundingBox                    // normalised, origin bottom left
        let fx = box.origin.x * w
        let fw = box.width * w
        let fh = box.height * h
        let fy = (1 - box.origin.y - box.height) * h   // top edge, origin top left

        // The eye line is a steadier anchor than the box centre.
        var eyeX = fx + fw / 2, eyeY = fy + fh * 0.42
        if let left = face.landmarks?.leftEye, let right = face.landmarks?.rightEye {
            let size = CGSize(width: w, height: h)
            let pts = left.pointsInImage(imageSize: size) + right.pointsInImage(imageSize: size)
            eyeX = pts.map { $0.x }.reduce(0, +) / CGFloat(pts.count)
            eyeY = h - pts.map { $0.y }.reduce(0, +) / CGFloat(pts.count)
        }
        faces.append("{\"x\":\(fx),\"y\":\(fy),\"w\":\(fw),\"h\":\(fh),"
                     + "\"eyeX\":\(eyeX),\"eyeY\":\(eyeY)}")
    }
    print("{\"path\":\"\(esc)\",\"width\":\(Int(w)),\"height\":\(Int(h)),"
          + "\"faces\":[\(faces.joined(separator: ","))]}")
}
