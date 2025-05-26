// mobile/android/app/src/main/java/com/bughawkai/app/ui/components/LogInputComponent.kt
package com.bughawkai.app.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bughawkai.app.data.ApiService
import com.bughawkai.app.data.models.BugReportResponse
import com.bughawkai.app.data.models.LogSubmissionRequest
import kotlinx.coroutines.launch

@Composable
fun LogInputComponent(viewModel: LogInputViewModel = androidx.lifecycle.viewmodel.compose.viewModel()) {
    val logs by viewModel.logs.collectAsState()
    val codeSnippet by viewModel.codeSnippet.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val statusMessage by viewModel.statusMessage.collectAsState()
    val predictedBugs by viewModel.predictedBugs.collectAsState()
    val suggestedPatches by viewModel.suggestedPatches.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    Column(modifier = Modifier.padding(16.dp)) {
        OutlinedTextField(
            value = logs,
            onValueChange = { viewModel.onLogsChange(it) },
            label = { Text("Enter logs") },
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = codeSnippet,
            onValueChange = { viewModel.onCodeSnippetChange(it) },
            label = { Text("Enter code snippet (optional)") },
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { viewModel.submitLogs() },
            enabled = !isLoading && logs.isNotBlank(),
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isLoading) {
                CircularProgressIndicator(modifier = Modifier.size(24.dp))
            } else {
                Text("Analyze Logs")
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        if (errorMessage.isNotEmpty()) {
            Text(text = "Error: $errorMessage", color = MaterialTheme.colorScheme.error)
        }
        if (statusMessage.isNotEmpty()) {
            Text(text = "Status: $statusMessage")
        }
        if (predictedBugs.isNotEmpty()) {
            Text(text = "Predicted Bugs:", style = MaterialTheme.typography.titleMedium)
            predictedBugs.forEach { bug ->
                Text("- ${bug.type}: ${bug.description} (Severity: ${bug.severity}, Confidence: ${"%.2f".format(bug.confidence)})")
            }
        }
        if (suggestedPatches.isNotEmpty()) {
            Text(text = "Suggested Patches:", style = MaterialTheme.typography.titleMedium)
            suggestedPatches.forEach { patch ->
                Text("- ${patch.description}\n${patch.suggested_code}")
            }
        }
    }
}

class LogInputViewModel : ViewModel() {
    private val apiService = ApiService()

    private val _logs = mutableStateOf("")
    val logs: State<String> = _logs

    private val _codeSnippet = mutableStateOf("")
    val codeSnippet: State<String> = _codeSnippet

    private val _isLoading = mutableStateOf(false)
    val isLoading: State<Boolean> = _isLoading

    private val _statusMessage = mutableStateOf("")
    val statusMessage: State<String> = _statusMessage

    private val _predictedBugs = mutableStateOf<List<com.bughawkai.app.data.models.BugPrediction>>(emptyList())
    val predictedBugs: State<List<com.bughawkai.app.data.models.BugPrediction>> = _predictedBugs

    private val _suggestedPatches = mutableStateOf<List<com.bughawkai.app.data.models.PatchSuggestion>>(emptyList())
    val suggestedPatches: State<List<com.bughawkai.app.data.models.PatchSuggestion>> = _suggestedPatches

    private val _errorMessage = mutableStateOf("")
    val errorMessage: State<String> = _errorMessage

    fun onLogsChange(newLogs: String) {
        _logs.value = newLogs
    }

    fun onCodeSnippetChange(newCode: String) {
        _codeSnippet.value = newCode
    }

    fun submitLogs() {
        if (_logs.value.isBlank()) {
            _errorMessage.value = "Logs cannot be empty."
            return
        }
        _isLoading.value = true
        _errorMessage.value = ""
        _statusMessage.value = "Submitting logs for analysis..."
        _predictedBugs.value = emptyList()
        _suggestedPatches.value = emptyList()

        viewModelScope.launch {
            try {
                val request = LogSubmissionRequest(
                    logs = _logs.value,
                    codeSnippet = if (_codeSnippet.value.isBlank()) null else _codeSnippet.value,
                    platform = "Android",
                    language = "Kotlin",
                    context = emptyMap()
                )
                val response: BugReportResponse = apiService.analyzeLogs(request)
                _statusMessage.value = response.status
                _predictedBugs.value = response.predictedBugs ?: emptyList()
                _suggestedPatches.value = response.suggestedPatches ?: emptyList()
            } catch (e: Exception) {
                _errorMessage.value = e.message ?: "Unknown error occurred"
            } finally {
                _isLoading.value = false
            }
        }
    }
}
