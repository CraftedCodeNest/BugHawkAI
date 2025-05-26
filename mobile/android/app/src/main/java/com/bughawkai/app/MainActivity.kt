// mobile/android/app/src/main/java/com/bughawkai/app/MainActivity.kt
package com.bughawkai.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.bughawkai.app.data.ApiService
import com.bughawkai.app.data.models.BugReportResponse
import com.bughawkai.app.data.models.LogSubmissionRequest
import com.bughawkai.app.ui.theme.BugHawkAITheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BugHawkAITheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    BugHawkAIScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BugHawkAIScreen() {
    var logInput by remember { mutableStateOf("") }
    var codeInput by remember { mutableStateOf("") }
    var analysisResult by remember { mutableStateOf("Submit logs/code for analysis.") }
    var isLoading by remember { mutableStateOf(false) }
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()
    val apiService = remember { ApiService() } // Assuming ApiService is defined

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(title = { Text("BugHawkAI") })
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text("Application Logs", style = MaterialTheme.typography.titleMedium)
            OutlinedTextField(
                value = logInput,
                onValueChange = { logInput = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(150.dp)
                    .padding(vertical = 8.dp),
                label = { Text("Enter logs here") },
                singleLine = false
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text("Relevant Code Snippet (Optional)", style = MaterialTheme.typography.titleMedium)
            OutlinedTextField(
                value = codeInput,
                onValueChange = { codeInput = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(100.dp)
                    .padding(vertical = 8.dp),
                label = { Text("Enter code snippet here") },
                singleLine = false
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    if (logInput.isBlank() && codeInput.isBlank()) {
                        coroutineScope.launch {
                            snackbarHostState.showSnackbar("Please enter either logs or a code snippet.")
                        }
                        return@Button
                    }
                    coroutineScope.launch { submitForAnalysis(logInput, codeInput, apiService, snackbarHostState) }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            ) {
                if (isLoading) {
                    CircularProgressIndicator(color = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(24.dp))
                    Spacer(Modifier.width(8.dp))
                }
                Text(if (isLoading) "Analyzing..." else "Analyze")
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text("Analysis Results", style = MaterialTheme.typography.titleMedium)
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .padding(vertical = 8.dp),
                shape = MaterialTheme.shapes.medium,
                color = MaterialTheme.colorScheme.surfaceVariant,
                tonalElevation = 1.dp
            ) {
                Text(
                    text = analysisResult,
                    modifier = Modifier
                        .padding(16.dp)
                        .verticalScroll(rememberScrollState())
                )
            }
        }
    }
}

suspend fun submitForAnalysis(
    logInput: String,
    codeInput: String,
    apiService: ApiService,
    snackbarHostState: SnackbarHostState
) {
    var isLoading by mutableStateOf(false)
    var analysisResult by mutableStateOf("Submit logs/code for analysis.")

    isLoading = true
    analysisResult = "Analysis in progress..."

    val request = LogSubmissionRequest(
        logs = logInput.ifBlank { null },
        code_snippet = codeInput.ifBlank { null },
        platform = "Android",
        language = "Kotlin"
    )

    try {
        val response = apiService.analyzeLogs(request)
        if (response.status == "QUEUED" || response.status == "IN_PROGRESS") {
            pollForResult(response.analysis_id, apiService) { result ->
                analysisResult = result
            }
        } else if (response.status == "COMPLETED") {
            analysisResult = formatResults(response)
        } else {
            analysisResult = "Error: ${response.message ?: "Unknown error."}"
        }
    } catch (e: Exception) {
        analysisResult = "Error submitting: ${e.localizedMessage}"
        snackbarHostState.showSnackbar("API Error: ${e.localizedMessage}")
    } finally {
        isLoading = false
    }
}

suspend fun pollForResult(
    analysisId: String,
    apiService: ApiService,
    updateResult: (String) -> Unit
) {
    val maxAttempts = 20
    var attempts = 0
    while (attempts < maxAttempts) {
        try {
            val response = apiService.getAnalysisStatus(analysisId)
            if (response.status == "COMPLETED") {
                updateResult(formatResults(response))
                return
            } else if (response.status == "FAILED") {
                updateResult("Analysis failed: ${response.message ?: "Please try again."}")
                return
            }
            attempts += 1
            delay(1000) // Wait 1 second
        } catch (e: Exception) {
            updateResult("Polling error: ${e.localizedMessage}")
            return
        }
    }
    updateResult("Analysis timed out. Please check back later.")
}

fun formatResults(response: BugReportResponse): String {
    var resultText = "Analysis ID: ${response.analysis_id}\nStatus: ${response.status}\n\n"

    val bugs = response.predicted_bugs
    if (!bugs.isNullOrEmpty()) {
        resultText += "--- Predicted Bugs ---\n"
        bugs.forEach { bug ->
            resultText += "Type: ${bug.type}\n"
            resultText += "Description: ${bug.description}\n"
            resultText += "Severity: ${bug.severity} (Confidence: %.1f%%)\n".format(bug.confidence * 100)
            bug.location?.let { resultText += "Location: $it\n" }
            bug.explanation?.let { resultText += "Explanation: $it\n" }
            resultText += "----------------------\n"
        }
    } else {
        resultText += "No specific bugs predicted based on current data.\n"
    }

    val patches = response.suggested_patches
    if (!patches.isNullOrEmpty()) {
        resultText += "\n--- Suggested Patches ---\n"
        patches.forEach { patch ->
            resultText += "Description: ${patch.description}\n"
            resultText += "Code:\n```kotlin\n${patch.suggested_code}\n```\n"
            resultText += "Relevance: %.1f%%\n".format(patch.relevance * 100)
            patch.explanation?.let { resultText += "Explanation: $it\n" }
            resultText += "----------------------\n"
        }
    }
    return resultText
}


@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    BugHawkAITheme {
        BugHawkAIScreen()
    }
}
</create_file>
