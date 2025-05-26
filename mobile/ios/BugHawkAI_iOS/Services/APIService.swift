// APIService for Swift (moved from ContentView.swift)
import Foundation

class APIService {
    var baseURL: String

    init(baseURL: String = "http://127.0.0.1:8000/api/v1") {
        self.baseURL = baseURL
    }

    func analyzeLogs(request: LogSubmissionRequest) async throws -> BugReportResponse {
        guard let url = URL(string: "\(baseURL)/analyze-logs") else {
            throw APIError.invalidURL
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData

        let maxRetries = 3
        var lastError: Error?

        for attempt in 1...maxRetries {
            do {
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
            } catch {
                lastError = error
                print("Attempt \(attempt) failed with error: \(error.localizedDescription)")
                if attempt == maxRetries {
                    throw error
                }
                // Optionally add delay before retrying
                try await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
            }
        }
        throw lastError ?? APIError.invalidResponse(statusCode: -1, message: "Unknown error")
    }

    func getAnalysisStatus(analysisId: String) async throws -> BugReportResponse {
        guard let url = URL(string: "\(baseURL)/status/\(analysisId)") else {
            throw APIError.invalidURL
        }

        let maxRetries = 3
        var lastError: Error?

        for attempt in 1...maxRetries {
            do {
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
            } catch {
                lastError = error
                print("Attempt \(attempt) failed with error: \(error.localizedDescription)")
                if attempt == maxRetries {
                    throw error
                }
                try await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
            }
        }
        throw lastError ?? APIError.invalidResponse(statusCode: -1, message: "Unknown error")
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
