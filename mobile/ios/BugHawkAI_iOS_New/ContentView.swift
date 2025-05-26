import SwiftUI

struct ContentView: View {
    @State private var logs: String = ""
    @State private var codeSnippet: String = ""
    @State private var platform: String = "iOS"
    @State private var language: String = "Swift"
    @State private var context: [String: String] = [:]
    @State private var analysisId: String?
    @State private var statusMessage: String = ""
    @State private var isLoading: Bool = false
    @State private var predictedBugs: [BugPrediction] = []
    @State private var suggestedPatches: [PatchSuggestion] = []
    @State private var errorMessage: String?

    let apiService = APIService()

    var body: some View {
        NavigationView {
            VStack(alignment: .leading) {
                TextEditor(text: $logs)
                    .border(Color.gray, width: 1)
                    .frame(height: 150)
                    .padding()
                    .overlay(Text("Enter logs here").opacity(logs.isEmpty ? 0.5 : 0).padding(.leading, 8).padding(.top, 8), alignment: .topLeading)

                TextEditor(text: $codeSnippet)
                    .border(Color.gray, width: 1)
                    .frame(height: 150)
                    .padding()
                    .overlay(Text("Enter code snippet here (optional)").opacity(codeSnippet.isEmpty ? 0.5 : 0).padding(.leading, 8).padding(.top, 8), alignment: .topLeading)

                Button(action: submitLogs) {
                    if isLoading {
                        ProgressView()
                    } else {
                        Text("Analyze Logs")
                    }
                }
                .disabled(isLoading || logs.isEmpty)
                .padding()

                if let errorMessage = errorMessage {
                    Text("Error: \(errorMessage)")
                        .foregroundColor(.red)
                        .padding()
                }

                if !statusMessage.isEmpty {
                    Text("Status: \(statusMessage)")
                        .padding()
                }

                if !predictedBugs.isEmpty {
                    Text("Predicted Bugs:")
                        .font(.headline)
                        .padding(.top)
                    List(predictedBugs) { bug in
                        VStack(alignment: .leading) {
                            Text(bug.type).bold()
                            Text(bug.description)
                            Text("Severity: \(bug.severity), Confidence: \(String(format: "%.2f", bug.confidence))")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    }
                }

                if !suggestedPatches.isEmpty {
                    Text("Suggested Patches:")
                        .font(.headline)
                        .padding(.top)
                    List(suggestedPatches) { patch in
                        VStack(alignment: .leading) {
                            Text(patch.description).bold()
                            Text(patch.suggested_code)
                                .font(.system(.body, design: .monospaced))
                                .padding(.top, 2)
                        }
                    }
                }

                Spacer()
            }
            .navigationTitle("BugHawkAI Log Analysis")
            .padding()
        }
    }

    func submitLogs() {
        isLoading = true
        errorMessage = nil
        statusMessage = "Submitting logs for analysis..."
        predictedBugs = []
        suggestedPatches = []
        Task {
            do {
                let request = LogSubmissionRequest(logs: logs, code_snippet: codeSnippet.isEmpty ? nil : codeSnippet, platform: platform, language: language, context: context)
                let response = try await apiService.analyzeLogs(request: request)
                analysisId = response.analysis_id
                statusMessage = response.status
                predictedBugs = response.predicted_bugs ?? []
                suggestedPatches = response.suggested_patches ?? []
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                statusMessage = ""
                isLoading = false
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
