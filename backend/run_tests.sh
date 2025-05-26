#!/bin/bash

# --- Configuration ---
PROJECT_ROOT="/Users/morningstar/Documents/BugHawkAI" # Adjust if your root path changes
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${BACKEND_DIR}/venv"
PYTHON_BIN="${VENV_DIR}/bin/python" # Explicit path to venv's python
REQUIREMENTS_FILE="${BACKEND_DIR}/requirements.txt"

echo "--- Starting BugHawkAI Backend Test Setup ---"

# 1. Navigate to the backend directory
echo "Changing directory to: ${BACKEND_DIR}"
cd "${BACKEND_DIR}" || { echo "Failed to change to backend directory. Exiting."; exit 1; }

# 2. Create virtual environment if it doesn't exist
if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating virtual environment at ${VENV_DIR}..."
  /opt/homebrew/bin/python3.13 -m venv "${VENV_DIR}" || { echo "Failed to create virtual environment. Ensure python3.13 is accessible."; exit 1; }
fi

# 3. Activate virtual environment
echo "Activating virtual environment..."
source "${VENV_DIR}/bin/activate" || { echo "Failed to activate virtual environment. Exiting."; exit 1; }

# 4. Install dependencies
echo "Installing/Updating Python dependencies from ${REQUIREMENTS_FILE}..."
pip install -r "${REQUIREMENTS_FILE}" || { echo "Failed to install dependencies. Exiting."; exit 1; }

echo "Dependencies installed. Python path for tests:"
"${PYTHON_BIN}" -c "import sys; print(sys.path)" # Show Python path

# 5. Run tests explicitly from the backend root to resolve 'app' import
echo "Running backend tests using pytest..."
PYTHONPATH="${BACKEND_DIR}/app" pytest tests/ --maxfail=1 --disable-warnings -q

# 6. Deactivate virtual environment
deactivate

echo "--- Test Run Complete ---"
