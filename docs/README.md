Running ChronosMatch

Follow these steps from the repository root directory.

1. Open the project

Open a terminal in VS Code and navigate to the "chronosmatch" repository root.

2. Create a virtual environment

On Windows:

python -m venv .venv

3. Activate the virtual environment

.\.venv\Scripts\Activate.ps1

If PowerShell blocks activation, open Command Prompt and run:

.venv\Scripts\activate.bat

4. Install dependencies

python -m pip install -r requirements.txt

5. Run the automated tests

python -m pytest -q

6. Run the dashboard

Follow the dashboard module's instructions and start command, if available. For the curses dashboard on Windows, install the required "windows-curses" dependency first.

Note: The complete simulator, matching engine, shared statistics, and dashboard must be connected and running for a full end-to-end demonstration. Check the relevant module instructions before starting individual components.
