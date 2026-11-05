# Fresh Clone Quickstart Verification

## Current Repository Setup

The repository includes requirements.txt with pytest, Cython, and Windows curses dependencies.

## Windows Setup

1. Create a virtual environment:
   python -m venv .venv

2. Activate it:
   .\.venv\Scripts\Activate.ps1

3. Install dependencies:
   python -m pip install -r requirements.txt

4. Build both Cython extensions:
   python setup.py build_ext --inplace
   python engine/setup.py build_ext --inplace

A Microsoft C++ Build Tools compiler is required for the Cython builds.

## Run Tests

Run:
   python -m pytest -v

The current integration branch collects 100 tests, all of which passed in the latest local test run.

## Historical Verification

An earlier fresh-clone verification was performed on the madhu branch using Python 3.14.7. It recorded 49 passing tests. This is a historical result, not verification of the current integration branch.

## Limitations

- Fresh-clone verification was previously performed on Windows only.
- Linux and macOS verification has not been documented.
