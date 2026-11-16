import AppKit

// Menu bar control for the scriptwriter dev server: status, start, stop, restart.
// The server runs detached, so it keeps serving when this app quits.

let port = 8765
let serverDirectory = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().path
let python = "/opt/homebrew/bin/python3"
let logPath = NSHomeDirectory() + "/Library/Logs/scriptwriter-server.log"

enum ServerState: Equatable {
    case running(pid: Int32)
    case notResponding(pid: Int32)
    case stopped
    case busy(String)
}

final class Controller: NSObject, NSApplicationDelegate {
    private let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    private let menu = NSMenu()
    private let statusLine = NSMenuItem(title: "", action: nil, keyEquivalent: "")
    private let detailLine = NSMenuItem(title: "", action: nil, keyEquivalent: "")
    private var startItem: NSMenuItem!
    private var stopItem: NSMenuItem!
    private var restartItem: NSMenuItem!
    private var state = ServerState.stopped
    private var lastHealth: Date?

    func applicationDidFinishLaunching(_ notification: Notification) {
        statusLine.isEnabled = false
        detailLine.isEnabled = false
        menu.addItem(statusLine)
        menu.addItem(detailLine)
        menu.addItem(.separator())
        startItem = add("Start", #selector(start), "s")
        stopItem = add("Stop", #selector(stop), "x")
        restartItem = add("Restart", #selector(restart), "r")
        menu.addItem(.separator())
        add("Open Log", #selector(openLog), "l")
        add("Open Health Check", #selector(openHealth), "")
        add("Open Server Folder", #selector(openFolder), "")
        menu.addItem(.separator())
        add("Quit Menu (server keeps running)", #selector(quit), "q")
        item.menu = menu
        render()
        Timer.scheduledTimer(withTimeInterval: 3, repeats: true) { [weak self] _ in self?.refresh() }
        refresh()
    }

    @discardableResult
    private func add(_ title: String, _ action: Selector, _ key: String) -> NSMenuItem {
        let menuItem = NSMenuItem(title: title, action: action, keyEquivalent: key)
        menuItem.target = self
        menu.addItem(menuItem)
        return menuItem
    }

    private func refresh() {
        if case .busy = state { return }
        let pid = listeningPID()
        guard let pid else { apply(.stopped); return }
        var request = URLRequest(url: URL(string: "http://127.0.0.1:\(port)/v1/health")!)
        request.timeoutInterval = 2
        URLSession.shared.dataTask(with: request) { [weak self] data, _, _ in
            let healthy = data.flatMap { String(data: $0, encoding: .utf8) }?.contains("\"ok\": true") ?? false
            DispatchQueue.main.async {
                guard let self else { return }
                if case .busy = self.state { return }
                if healthy { self.lastHealth = Date() }
                self.apply(healthy ? .running(pid: pid) : .notResponding(pid: pid))
            }
        }.resume()
    }

    private func apply(_ newState: ServerState) {
        state = newState
        render()
    }

    private func render() {
        let symbol: String
        let tint: NSColor
        switch state {
        case .running(let pid):
            symbol = "circle.fill"; tint = .systemGreen
            statusLine.title = "Scriptwriter server: running"
            detailLine.title = "Port \(port), PID \(pid)" + (lastHealth.map { ", checked " + Self.time.string(from: $0) } ?? "")
        case .notResponding(let pid):
            symbol = "exclamationmark.circle.fill"; tint = .systemOrange
            statusLine.title = "Scriptwriter server: not responding"
            detailLine.title = "Port \(port) held by PID \(pid)"
        case .stopped:
            symbol = "circle"; tint = .secondaryLabelColor
            statusLine.title = "Scriptwriter server: stopped"
            detailLine.title = "Port \(port) is free"
        case .busy(let what):
            symbol = "circle.dotted"; tint = .systemYellow
            statusLine.title = "Scriptwriter server: \(what)"
            detailLine.title = "Port \(port)"
        }
        let image = NSImage(systemSymbolName: symbol, accessibilityDescription: statusLine.title)?
            .withSymbolConfiguration(.init(paletteColors: [tint]))
        item.button?.image = image
        item.button?.imagePosition = .imageLeading
        item.button?.title = " SW"
        item.button?.toolTip = statusLine.title
        let isBusy: Bool = { if case .busy = state { return true }; return false }()
        let isStopped = state == .stopped
        startItem.isEnabled = isStopped && !isBusy
        stopItem.isEnabled = !isStopped && !isBusy
        restartItem.isEnabled = !isBusy
    }

    @objc private func start() { perform("starting") { self.launch() } }
    @objc private func stop() { perform("stopping") { self.terminate() } }
    @objc private func restart() { perform("restarting") { self.terminate(); self.launch() } }

    private func perform(_ label: String, _ work: @escaping () -> Void) {
        apply(.busy(label))
        DispatchQueue.global().async {
            work()
            DispatchQueue.main.async {
                self.state = .stopped
                self.refresh()
            }
        }
    }

    private func launch() {
        guard listeningPID() == nil else { return }
        // Started through the shell with nohup so the server outlives this app.
        let command = "cd \(quoted(serverDirectory)) && nohup \(python) server.py --port \(port) >> \(quoted(logPath)) 2>&1 &"
        run("/bin/zsh", ["-c", command])
        for _ in 0..<40 where !healthy() { Thread.sleep(forTimeInterval: 0.25) }
    }

    private func terminate() {
        guard let pid = listeningPID() else { return }
        kill(pid, SIGTERM)
        for _ in 0..<20 where listeningPID() != nil { Thread.sleep(forTimeInterval: 0.25) }
        if let pid = listeningPID() { kill(pid, SIGKILL) }
    }

    private func healthy() -> Bool {
        guard let data = try? Data(contentsOf: URL(string: "http://127.0.0.1:\(port)/v1/health")!) else { return false }
        return String(data: data, encoding: .utf8)?.contains("\"ok\": true") ?? false
    }

    private func listeningPID() -> Int32? {
        let output = run("/usr/sbin/lsof", ["-nP", "-t", "-iTCP:\(port)", "-sTCP:LISTEN"])
        return output.split(separator: "\n").first.flatMap { Int32($0) }
    }

    @discardableResult
    private func run(_ path: String, _ arguments: [String]) -> String {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: path)
        process.arguments = arguments
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = FileHandle.nullDevice
        guard (try? process.run()) != nil else { return "" }
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        process.waitUntilExit()
        return String(data: data, encoding: .utf8) ?? ""
    }

    private func quoted(_ path: String) -> String { "'" + path.replacingOccurrences(of: "'", with: "'\\''") + "'" }

    @objc private func openLog() {
        if !FileManager.default.fileExists(atPath: logPath) { FileManager.default.createFile(atPath: logPath, contents: nil) }
        NSWorkspace.shared.open(URL(fileURLWithPath: logPath))
    }

    @objc private func openHealth() { NSWorkspace.shared.open(URL(string: "http://127.0.0.1:\(port)/v1/health")!) }
    @objc private func openFolder() { NSWorkspace.shared.open(URL(fileURLWithPath: serverDirectory)) }
    @objc private func quit() { NSApp.terminate(nil) }

    private static let time: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter
    }()
}

let app = NSApplication.shared
let controller = Controller()
app.delegate = controller
app.setActivationPolicy(.accessory)
app.run()
