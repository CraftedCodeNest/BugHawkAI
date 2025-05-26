// mobile/ios/BugHawkAI_iOS/ContentView.swift
import SwiftUI

struct ContentView: View {
    @State private var logInput: String = ""
    @State private var codeInput: String = ""
    @State private var analysisResult: String = "Submit logs/code for analysis."
    @State private var isLoading: Bool = false
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""

    private let apiService = APIService() // Assuming APIService is defined

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Application Logs")) {
                    TextEditor(text: $logInput)
                        .frame(height: 150)
                        .border(Color.gray.opacity(0.2), width: 1)
                        .padding(.vertical, 5)
                }

                Section(header: Text("Relevant Code Snippet (Optional)")) {
                    TextEditor(text: $codeInput)
                        .frame(height: 100)
                        .border(Color.gray.opacity(0.2), width: 1)
                        .padding(.vertical, 5)
                }

                Section {
                    Button(action: submitForAnalysis) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            }
                            Text(isLoading ? "Analyzing..." : "Analyze")
                                .font(.headline)
                                .foregroundColor(.white)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(Color.blue)
                        .cornerRadius(10)
                    }
                    .disabled(isLoading)
                }

                Section(header: Text("Analysis Results")) {
                    ScrollView {
                        Text(analysisResult)
                            .font(.body)
                            .foregroundColor(.primary)
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.gray.opacity(0.05))
                            .cornerRadius(8)
                    }
                    .frame(height: 200)
                }
            }
            .navigationTitle("BugHawkAI")
            .alert(isPresented: $showAlert) {
                Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
            }
        }
    }

    func submitForAnalysis() {
        guard !logInput.isEmpty || !codeInput.isEmpty else {
            alertMessage = "Please enter either logs or a code snippet."
            showAlert = true
            return
        }

        isLoading = true
        analysisResult = "Analysis in progress..."

        let request = LogSubmissionRequest(
            logs: logInput.isEmpty ? nil : logInput,
            code_snippet: codeInput.isEmpty ? nil : codeInput,
            platform: "iOS",
            language: "Swift"
        )

        Task {
            do {
                let response = try await apiService.analyzeLogs(request: request)
                if response.status == "QUEUED" || response.status == "IN_PROGRESS" {
                    // Start polling for results
                    await pollForResult(analysisId: response.analysis_id)
                } else if response.status == "COMPLETED" {
                    updateResultsUI(response: response)
                } else {
                    analysisResult = "Error: \(response.message ?? "Unknown error.")"
                }
            } catch {
                analysisResult = "Error submitting: \(error.localizedDescription)"
                alertMessage = "API Error: \(error.localizedDescription)"
                showAlert = true
            } finally {
                isLoading = false
            }
        }
    }

    private func pollForResult(analysisId: String) async {
        let maxAttempts = 20 // Poll for up to 20 seconds
        var attempts = 0
        while attempts < maxAttempts {
            do {
                let response = try await apiService.getAnalysisStatus(analysisId: analysisId)
                if response.status == "COMPLETED" {
                    updateResultsUI(response: response)
                    return
                } else if response.status == "FAILED" {
                    analysisResult = "Analysis failed: \(response.message ?? "Please try again.")"
                    return
                }
                attempts += 1
                try await Task.sleep(nanoseconds: 1_000_000_000) // Wait 1 second
            } catch {
                analysisResult = "Polling error: \(error.localizedDescription)"
                return
            }
        }
        analysisResult = "Analysis timed out. Please check back later."
    }

    private func updateResultsUI(response: BugReportResponse) {
        var resultText = "Analysis ID: \(response.analysis_id)\nStatus: \(response.status)\n\n"

        if let bugs = response.predicted_bugs, !bugs.isEmpty {
            resultText += "--- Predicted Bugs ---\n"
            for bug in bugs {
                resultText += "Type: \(bug.type)\n"
                resultText += "Description: \(bug.description)\n"
                resultText += "Severity: \(bug.severity) (Confidence: \(bug.confidence * 100, specifier: "%.1f")%)\n"
                if let loc = bug.location { resultText += "Location: \(loc)\n" }
                if let exp = bug.explanation { resultText += "Explanation: \(exp)\n" }
                resultText += "----------------------\n"
            }
        } else {
            resultText += "No specific bugs predicted based on current data.\n"
        }

        if let patches = response.suggested_patches, !patches.isEmpty {
            resultText += "\n--- Suggested Patches ---\n"
            for patch in patches {
                resultText += "Description: \(patch.description)\n"
                resultText += "Code:\n```swift\n\(patch.suggested_code)\n```\n"
                resultText += "Relevance: \(patch.relevance * 100, specifier: "%.1f")%\n"
                if let exp = patch.explanation { resultText += "Explanation: \(exp)\n" }
                resultText += "----------------------\n"
            }
        }

        analysisResult = resultText
    }
}

// Data models for Swift (matching Pydantic schemas)
struct LogSubmissionRequest: Codable {
    let logs: String?
    let code_snippet: String?
    let platform: String
    let language: String
    let context: [String: String]? // Simplified for example

    enum CodingKeys: String, CodingKey {
        case logs
        case code_snippet
        case platform
        case language
        case context
    }
}

struct BugPrediction: Codable, Identifiable {
    let id = UUID() // For SwiftUI List iteration
    let type: String
    let description: String
    let severity: String
    let location: String?
    let confidence: Double
    let explanation: String?
}

struct PatchSuggestion: Codable, Identifiable {
    let id = UUID() // For SwiftUI List iteration
    let description: String
    let suggested_code: String
    let relevance: Double
    let explanation: String?
}

struct BugReportResponse: Codable {
    let analysis_id: String
    let status: String
    let message: String?
    let predicted_bugs: [BugPrediction]?
    let suggested_patches: [PatchSuggestion]?
    let timestamp: String?
}


// APIService for Swift (simplified)
class APIService {
    let baseURL = "http://127.0.0.1:8000/api/v1" // Make sure this matches your backend

    func analyzeLogs(request: LogSubmissionRequest) async throws -> BugReportResponse {
        guard let url = URL(string: "\(baseURL)/analyze-logs") else {
            throw APIError.invalidURL
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            let errorData = String(data: data, encoding: .utf8) ?? "No error message"
            print("API Error Response: \(errorData)")
            throw APIError.invalidResponse(statusCode: (response as? HTTPURLResponse)?.statusCode ?? -1, message: errorData)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase // To match Swift's camelCase
        let decodedResponse = try decoder.decode(BugReportResponse.self, from: data)
        return decodedResponse
    }

    func getAnalysisStatus(analysisId: String) async throws -> BugReportResponse {
        guard let url = URL(string: "\(baseURL)/status/\(analysisId)") else {
            throw APIError.invalidURL
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            let errorData = String(data: data, encoding: .utf8) ?? "No error message"
            print("API Status Error Response: \(errorData)")
            throw APIError.invalidResponse(statusCode: (response as? HTTPURLResponse)?.statusCode ?? -1, message: errorData)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        let decodedResponse = try decoder.decode(BugReportResponse.self, from: data)
        return decodedResponse
    }

    enum APIError: Error, LocalizedError {
        case invalidURL
        case invalidResponse(statusCode: Int, message: String)
        case decodingError(Error)

        var errorDescription: String? {
            switch self {
            case .invalidURL:
                return "The URL was invalid."
            case .invalidResponse(let statusCode, let message):
                return "API call failed with status code \(statusCode): \(message)"
            case .decodingError(let error):
                return "Failed to decode API response: \(error.localizedDescription)"
            }
        }
    }
}
