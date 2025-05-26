// mobile/android/app/src/main/java/com/bughawkai/app/data/ApiService.kt
package com.bughawkai.app.data

import com.bughawkai.app.data.models.BugReportResponse
import com.bughawkai.app.data.models.LogSubmissionRequest
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import kotlinx.coroutines.delay

class ApiService {
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
                encodeDefaults = true
                explicitNulls = false // Don't include nulls in JSON if not specified
            })
        }
    }

    private val baseUrl = "http://10.0.2.2:8000/api/v1" // For Android emulator to access host machine localhost

    private val maxRetries = 3
    private val retryDelayMillis = 500L

    suspend fun analyzeLogs(request: LogSubmissionRequest): BugReportResponse {
        var lastException: Exception? = null
        repeat(maxRetries) { attempt ->
            try {
                val response = client.post("$baseUrl/analyze-logs") {
                    contentType(ContentType.Application.Json)
                    setBody(request)
                }
                if (response.status.isSuccess()) {
                    return response.body()
                } else {
                    val errorBody = response.bodyAsText()
                    throw Exception("API error: ${response.status.value} - $errorBody")
                }
            } catch (e: Exception) {
                lastException = e
                if (attempt == maxRetries - 1) {
                    throw e
                }
                delay(retryDelayMillis)
            }
        }
        throw lastException ?: Exception("Unknown error in analyzeLogs")
    }

    suspend fun getAnalysisStatus(analysisId: String): BugReportResponse {
        var lastException: Exception? = null
        repeat(maxRetries) { attempt ->
            try {
                val response = client.get("$baseUrl/status/$analysisId")
                if (response.status.isSuccess()) {
                    return response.body()
                } else {
                    val errorBody = response.bodyAsText()
                    throw Exception("API error: ${response.status.value} - $errorBody")
                }
            } catch (e: Exception) {
                lastException = e
                if (attempt == maxRetries - 1) {
                    throw e
                }
                delay(retryDelayMillis)
            }
        }
        throw lastException ?: Exception("Unknown error in getAnalysisStatus")
    }
}
