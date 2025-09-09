import SwiftUI
import RealityKit
import ARKit

@main
struct PuppetApp: SwiftUI.App {
  var body: some SwiftUI.Scene { WindowGroup { ContentView() } }
}

// MARK: Model

final class PoseModel: ObservableObject {
  @Published var timestamp: TimeInterval = 0
  @Published var qx: Double = 0
  @Published var qy: Double = 0
  @Published var qz: Double = 0
  @Published var qw: Double = 1

  private func f(_ v: Double) -> String { String(format: "%.12f", v) }
  var jsonString: String {
    """
    {
      "timestamp": \(String(format: "%.3f", timestamp)),
      "quaternion": {
        "x": \(f(qx)), "y": \(f(qy)), "z": \(f(qz)), "w": \(f(qw))
      }
    }
    """
  }
}


// MARK: UI

struct ContentView: View {
  @State private var recording = false
  @StateObject private var pose = PoseModel()

  private var bg: Color {
    recording ? Color(red: 0.92, green: 0.97, blue: 1.0) : Color(.systemGray6)
  }

  var body: some View {
    ZStack {
      bg.ignoresSafeArea()

      VStack(spacing: 24) {
        Text("6DOF Pose")
          .font(.title.bold())

        PoseCard(text: pose.jsonString)
          .padding(.horizontal)

        Spacer()

        VStack(spacing: 12) {
          Toggle("", isOn: $recording)
            .labelsHidden()
            .toggleStyle(SwitchToggleStyle(tint: .blue))
            .scaleEffect(1.8)
          Text(recording ? "Recording" : "Start Recording")
            .font(.headline)
            .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.bottom, 40)
      }
    }
    // ARKit runs invisibly to supply pose
    .background(
      ARPoseStreamer(streaming: recording, model: pose)
        .frame(width: 1, height: 1)
        .allowsHitTesting(false)
    )
  }
}

struct PoseCard: View {
  let text: String
  var body: some View {
    ScrollView {
      Text(text)
        .font(.system(.body, design: .monospaced))
        .foregroundStyle(.primary)
        .textSelection(.enabled)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
    }
    .frame(maxHeight: 260)
    .background(
      RoundedRectangle(cornerRadius: 14)
        .fill(Color(.secondarySystemBackground))
        .overlay(
          RoundedRectangle(cornerRadius: 14)
            .stroke(Color(.separator), lineWidth: 1)
        )
    )
  }
}

// MARK: Pose streamer (no AR content)

struct ARPoseStreamer: UIViewRepresentable {
  let streaming: Bool
  let model: PoseModel
  private let endpoint = URL(string: "http://10.0.0.141:5001/pose")!

  func makeUIView(context: Context) -> ARView {
    let v = ARView(frame: .zero)
    v.automaticallyConfigureSession = false
    if #available(iOS 15.0, *) { v.environment.background = .color(.clear) }
    v.session.delegate = context.coordinator
    context.coordinator.model = model
    context.coordinator.start(url: endpoint)

    let config = ARWorldTrackingConfiguration()
    config.worldAlignment = .gravity
    v.session.run(config)
    context.coordinator.streaming = streaming
    return v
  }

  func updateUIView(_ v: ARView, context: Context) {
    context.coordinator.streaming = streaming
  }

  func makeCoordinator() -> Coordinator { Coordinator() }

  final class Coordinator: NSObject, ARSessionDelegate {
    var streaming = false
    private var endpoint: URL?
    private var lastSent = CFTimeInterval(0)
    private let urlSession = URLSession(configuration: .ephemeral)
    weak var model: PoseModel?

    func start(url: URL) { endpoint = url }

    func session(_ session: ARSession, didUpdate frame: ARFrame) {
      // Update display every frame
      let q = simd_quatf(frame.camera.transform).normalized
      let now = Date().timeIntervalSince1970
      DispatchQueue.main.async { [weak self] in
        guard let m = self?.model else { return }
        m.timestamp = now
        m.qx = Double(q.imag.x); m.qy = Double(q.imag.y)
        m.qz = Double(q.imag.z); m.qw = Double(q.real)
      }

      // Stream when recording
      guard streaming, let endpoint else { return }
      let tnow = CACurrentMediaTime()
      if tnow - lastSent < 1.0/30.0 { return }
      lastSent = tnow

      let payload: [String: Any] = [
        "timestamp": now,
        "quaternion": [
          "x": Double(q.imag.x), "y": Double(q.imag.y),
          "z": Double(q.imag.z), "w": Double(q.real)
        ]
      ]

      var req = URLRequest(url: endpoint)
      req.httpMethod = "POST"
      req.setValue("application/json", forHTTPHeaderField: "Content-Type")
      req.httpBody = try? JSONSerialization.data(withJSONObject: payload)
      urlSession.dataTask(with: req).resume()
    }
  }
}
