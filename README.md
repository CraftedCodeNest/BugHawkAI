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

## Repository Structure

BugHawkAI/
├── .github/                         # GitHub Actions CI/CD workflows
│   └── workflows/
│       └── main_ci_cd.yml           # CI/CD for backend deployment & mobile build checks
├── mobile/                          # Contains mobile application source codes
│   ├── ios/                         # iOS Application (Swift/SwiftUI)
│   │   ├── BugHawkAI_iOS.xcodeproj/  # Xcode Project Directory
│   │   ├── BugHawkAI_iOS/           # Main iOS App Source
│   │   │   ├── BugHawkAIApp.swift   # App entry point (SwiftUI)
│   │   │   ├── ContentView.swift    # Main UI View
│   │   │   ├── Views/               # Sub-views (e.g., LogSubmissionView, BugReportView)
│   │   │   │   └── LogSubmissionView.swift
│   │   │   ├── Models/              # Data Models for API responses/requests
│   │   │   │   └── BugReport.swift
│   │   │   │   └── APIResponse.swift
│   │   │   ├── Services/            # API Client and other service logic
│   │   │   │   └── APIService.swift
│   │   │   ├── Utils/               # Utility functions (e.g., LogFormatter)
│   │   │   └── Assets.xcassets/     # App assets (icons, images)
│   │   ├── Tests/                   # Unit and UI Tests for iOS
│   │   └── README.md                # iOS App specific README
│   └── android/                     # Android Application (Kotlin/Jetpack Compose)
│       ├── app/                     # Android App Module
│       │   ├── src/
│       │   │   ├── main/
│       │   │   │   ├── java/com/bughawkai/app/ # Main Java/Kotlin source folder
│       │   │   │   │   ├── MainActivity.kt    # Main Activity (Jetpack Compose)
│       │   │   │   │   ├── ui/                # UI Composables
│       │   │   │   │   │   ├── theme/
│       │   │   │   │   │   │   └── Theme.kt
│       │   │   │   │   │   └── components/
│       │   │   │   │   │       └── LogInputComponent.kt
│       │   │   │   │   ├── data/              # Data layer (API service, models)
│       │   │   │   │   │   ├── ApiService.kt  # Retrofit/Ktor API client
│       │   │   │   │   │   └── models/
│       │   │   │   │   │       └── BugReport.kt
│       │   │   │   │   │       └── APIResponse.kt
│       │   │   │   │   └── di/                # Dependency Injection (e.g., Hilt)
│       │   │   │   │       └── NetworkModule.kt
│       │   │   │   ├── AndroidManifest.xml    # App manifest
│       │   │   │   └── res/                   # Android resources (layouts, drawables, strings)
│       │   ├── build.gradle.kts               # Module-level Gradle build file
│       └── README.md                # Android App specific README
├── backend/                         # Backend Services (Python/FastAPI)
│   ├── app/                         # FastAPI Application Core
│   │   ├── main.py                  # Main FastAPI application
│   │   ├── api/                     # API Routers
│   │   │   └── v1/
│   │   │       └── bug_analysis.py  # Endpoints for log submission, analysis status
│   │   ├── services/                # Core business logic services
│   │   │   ├── llm_service.py       # Handles interaction with LLM APIs
│   │   │   ├── static_analysis_service.py # Orchestrates static analysis tools
│   │   │   └── analysis_orchestrator.py # Combines LLM & static analysis logic
│   │   ├── models/                  # Pydantic models for request/response schemas
│   │   │   └── schemas.py
│   │   ├── database/                # Database related files
│   │   │   ├── crud.py              # Create, Read, Update, Delete operations
│   │   │   └── database.py          # Database connection and session management
│   │   │   └── models.py            # SQLAlchemy ORM models
│   │   ├── utils/                   # Utility functions
│   │   │   └── log_parser.py        # Parses different log formats
│   │   │   └── code_extractor.py    # Extracts relevant code snippets
│   │   └── core/                    # Core configurations
│   │       └── config.py            # Application settings (API keys, DB URLs)
│   ├── tests/                       # Backend tests
│   │   ├── test_api.py              # API endpoint tests
│   │   └── test_services.py         # Unit tests for services
│   ├── Dockerfile                   # Docker build instructions for the backend
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Example environment variables
│   ├── poetry.lock                  # If using Poetry for dependency management
│   └── README.md                    # Backend specific README
├── docs/                            # Project Documentation
│   ├── ARCHITECTURE.md              # Detailed architecture overview
│   ├── API_SPEC.md                  # OpenAPI/Swagger spec documentation
│   ├── DEPLOYMENT.md                # Deployment instructions
│   ├── USAGE.md                     # How to use BugHawkAI
│   └── SETUP.md                     # Local development setup guide
├── .gitignore                       # Standard Git ignore file for Python, iOS, Android
├── LICENSE                          # Project License (e.g., MIT, Apache 2.0)
├── README.md                        # Main Project README (overview, setup, features)
└── CONTRIBUTING.md                  # Guidelines for contributors


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
