# Python Installation Guide - Python 3.12

## Why Python 3.12?

Python 3.12 is the **most compatible version** for this project. Most packages support it well, and it avoids the compatibility issues with Python 3.13.

## Installation Steps

### Step 1: Download Python 3.12

1. Visit: https://www.python.org/downloads/release/python-31211/
2. Download **Windows installer (64-bit)** for Python 3.12.11
3. Run the installer

### Step 2: During Installation

**IMPORTANT**: Check these options:
- ✅ **"Add Python 3.12 to PATH"** (CRITICAL!)
- ✅ **"Install for all users"** (optional but recommended)
- Choose **"Customize installation"**
  - ✅ Check all optional features
  - ✅ Include pip
  - ✅ Include tcl/tk and IDLE

### Step 3: Verify Installation

Open PowerShell and run:
```powershell
py -3.12 --version
# Should show: Python 3.12.11

py -3.12 -m pip --version
# Should show pip version
```

### Step 4: Create Virtual Environment with Python 3.12

```powershell
# Navigate to project
cd "D:\Python Projects\Agentic Stock trading"

# Create venv with Python 3.12
py -3.12 -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Verify Python version in venv
python --version
# Should show: Python 3.12.11
```

### Step 5: Install Dependencies

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Initialize Database

```powershell
python scripts/init_db.py
```

## If You Have Multiple Python Versions

You can keep both Python 3.12 and 3.13 installed. Use:
- `py -3.12` for Python 3.12
- `py -3.13` for Python 3.13
- `python` or `py` for default version

## Troubleshooting

### Python 3.12 Not Found
```powershell
# Check if installed
py --list
# Should show Python 3.12.x

# If not showing, reinstall and check "Add to PATH"
```

### Virtual Environment Issues
```powershell
# Delete old venv
Remove-Item -Recurse -Force venv

# Create new one with Python 3.12
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

### pip Issues
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Or use ensurepip
python -m ensurepip --upgrade
```

## Quick Setup Script

After installing Python 3.12, run:
```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python scripts/init_db.py
python scripts/test_ollama_connection.py
```

## Verification

Test that everything works:
```powershell
python -c "import crewai; print('✅ CrewAI')"
python -c "import streamlit; print('✅ Streamlit')"
python -c "import sqlalchemy; print('✅ SQLAlchemy')"
python -c "from config.settings import settings; print('✅ Config')"
```
