# 🐞 BugHawkAI 🦅

**The Next-Gen AI-Powered Bug Prediction & Patching Platform for iOS & Android**

## Vision

BugHawkAI is designed to revolutionize the debugging process by proactively identifying potential bugs and suggesting precise, context-aware code patches. Leveraging a unique blend of advanced Large Language Models (LLMs) for intelligent reasoning and sophisticated static code analysis for deep code understanding, BugHawkAI aims to be an indispensable tool for mobile developers, significantly enhancing efficiency and code quality.

## Features

* **Hybrid Analysis Engine:** Combines LLM-driven predictive analysis with deep static code analysis (e.g., SwiftLint, Detekt, Clang-Tidy) for comprehensive bug detection.
* **Context-Aware Patch Suggestion:** Utilizes LLMs to generate actual code fixes, considering the specific language, framework, and surrounding code context.
* **Real-time & Asynchronous Processing:** Mobile apps can submit logs and code snippets, with backend analysis handled efficiently in the background.
* **User Feedback & Model Improvement:** Built-in mechanisms for developers to provide feedback, continuously fine-tuning the LLM's accuracy and relevance.
* **Native Mobile Experience:** Intuitive iOS (SwiftUI) and Android (Jetpack Compose) applications for seamless interaction.

## Architecture Overview

BugHawkAI consists of three primary components:

1.  **Mobile Applications (iOS & Android):** Native clients responsible for collecting logs and code snippets, sending them to the backend, and displaying predicted bugs and suggested patches.
2.  **Backend (Python/FastAPI):** The core intelligence engine. It orchestrates static analysis tools, interacts with LLM APIs, performs bug prediction, generates patches, and manages analysis states.
3.  **Database (PostgreSQL/SQLite):** Stores analysis reports, user feedback, and historical data for model improvement and persistent state.

For a detailed architectural diagram and explanation, refer to [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).


## Getting Started

Follow these steps to set up BugHawkAI for local development:

### Prerequisites

* Python 3.10+
* Node.js (for backend dev tools if any, not strictly required for FastAPI)
* Docker (recommended for easy backend setup)
* Xcode (for iOS development)
* Android Studio (for Android development)
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/BugHawkAI.git
cd BugHawkAI
```

### 2. Backend Setup

Navigate to the backend/ directory:

```bash
cd backend
```

Using Poetry (Recommended):

```bash
pip install poetry
poetry install
cp .env.example .env
# Edit .env to add your database URL and LLM API keys (e.g., OPENAI_API_KEY)
# LLM API keys are crucial for core functionality.
```

Using pip:

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your database URL and LLM API keys
```

Run the Backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be accessible at http://localhost:8000. You can view the API documentation at http://localhost:8000/docs.

Note on Static Analysis Tools:
The static_analysis_service.py is a wrapper. You will need to install the actual static analysis tools (e.g., SwiftLint, Detekt, Clang-Tidy) on your development machine/CI/CD environment for them to be runnable by the backend's subprocess calls.

### 3. Mobile App Setup

#### iOS (SwiftUI)

Navigate to the mobile/ios/ directory:

```bash
cd ../mobile/ios
```

Open BugHawkAI_iOS.xcodeproj in Xcode.

Ensure your APIService.swift baseURL matches your backend's URL (e.g., http://127.0.0.1:8000/api/v1).

Build and run the application on a simulator or physical device.

#### Android (Jetpack Compose)

Navigate to the mobile/android/ directory:

```bash
cd ../mobile/android
```

Open the project in Android Studio.

Ensure your ApiService.kt baseUrl matches your backend's URL. For Android Emulator to access your host machine's localhost, use http://10.0.2.2:8000/api/v1.

Build and run the application on an emulator or physical device.

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

This project is licensed under the MIT License.
