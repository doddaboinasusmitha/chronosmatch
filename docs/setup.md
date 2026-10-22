ChronosMatch Setup Guide

Prerequisites

- Python installed and available from the terminal
- Git
- Visual Studio Code (recommended)

1. Open the repository

Open a terminal at the root of the "chronosmatch" repository.

2. Create a virtual environment

On Windows PowerShell:

python -m venv .venv

3. Activate the environment

.\.venv\Scripts\Activate.ps1

If PowerShell blocks activation, use Command Prompt:

.venv\Scripts\activate.bat

4. Install dependencies

python -m pip install -r requirements.txt

5. Run the tests

python -m pytest -q

6. Dashboard

Refer to "dashboard/README.md" for dashboard instructions. On Windows, "windows-curses" is included in the project dependencies.

Troubleshooting

- If "python" is not recognised, check your Python installation and PATH.
- If a package installation fails, check your internet connection and Python version.
- Run commands from the repository root unless otherwise specified.

A complete live demonstration requires the simulator, matching engine, shared statistics, and dashboard to be integrated and running.