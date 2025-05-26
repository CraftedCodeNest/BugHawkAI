// mobile/android/app/src/main/java/com/bughawkai/app/data/models/BugReport.kt
package com.bughawkai.app.data.models

import kotlinx.serialization.Serializable

@Serializable
data class LogSubmissionRequest(
    val logs: String?,
    val code_snippet: String?,
    val platform: String,
    val language: String,
    val context: Map<String, String>? = null
)

@Serializable
data class BugPrediction(
    val type: String,
    val description: String,
    val severity: String,
    val location: String? = null,
    val confidence: Double,
    val explanation: String? = null
)

@Serializable
data class PatchSuggestion(
    val description: String,
    val suggested_code: String,
    val relevance: Double,
    val explanation: String? = null
)

@Serializable
data class BugReportResponse(
    val analysis_id: String,
    val status: String,
    val message: String? = null,
    val predicted_bugs: List<BugPrediction>? = null,
    val suggested_patches: List<PatchSuggestion>? = null,
    val timestamp: String? = null
)
