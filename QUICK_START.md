# Quick Start Guide

## After Python Installation

### 1. Create .env File

Copy the content below and save as `.env` in the project root:

```env
# Ollama Local Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Model Selection (local Ollama models - must be pulled locally)
OLLAMA_STRATEGY_MODEL=deepseek-r1:7b
OLLAMA_STRATEGY_FALLBACK=qwen2.5:7b
OLLAMA_DATABASE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_DATABASE_FALLBACK=codegemma:7b
OLLAMA_CHATBOT_MODEL=gemma2:2b-instruct-q4_K_M
OLLAMA_CHATBOT_FALLBACK=phi3:mini
OLLAMA_GUARDIAN_MODEL=deepseek-r1:7b
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
SHOONYA_USER_ID=your_shoonya_user_id
SHOONYA_PASSWORD=your_shoonya_password
SHOONYA_TWO_FA=your_2fa_key
SHOONYA_VENDOR_CODE=your_vendor_code
SHOONYA_API_SECRET=your_api_secret
SHOONYA_IMEI=your_imei
DATABASE_URL=sqlite:///./data/trading.db
MAX_POSITION_SIZE=10000.0
RISK_PERCENTAGE=2.0
ENABLE_LIVE_TRADING=false
PORTFOLIO_HEAT_THRESHOLD=80.0
WATCHLIST=RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK
DATA_UPDATE_INTERVAL=300
SENTIMENT_UPDATE_INTERVAL=600
HEARTBEAT_INTERVAL=1800
STOP_LOSS_CHECK_INTERVAL=300
PORTFOLIO_HEAT_CHECK_INTERVAL=300
LOG_LEVEL=INFO
LOG_FILE=./logs/trading_app.log
```

### 2. Install Python 3.12 (Recommended)

**IMPORTANT**: This project works best with **Python 3.12**. 

1. Download Python 3.12.11: https://www.python.org/downloads/release/python-31211/
2. During installation, **check "Add Python 3.12 to PATH"**
3. See `PYTHON_INSTALLATION_GUIDE.md` for detailed instructions

### 3. Setup Commands (Run in PowerShell)

**Option A: Automated Setup (Recommended)**
```powershell
# Navigate to project
cd "D:\Python Projects\Agentic Stock trading"

# Create venv with Python 3.12
py -3.12 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run automated setup script
python scripts/setup_env.py
```

**Option B: Manual Setup**
```powershell
# Navigate to project
cd "D:\Python Projects\Agentic Stock trading"

# Create virtual environment with Python 3.12
py -3.12 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install dependencies (Python 3.12 compatible)
pip install -r requirements.txt

# Note: Shoonya API is installed from GitLab. If you encounter issues, install separately:
# pip install git+https://gitlab.com/algo2t/shoonya.git

# Install Ollama (if not already installed)
# Download from: https://ollama.com/download
# Or use: winget install Ollama.Ollama (Windows)

# Start Ollama server (in a separate terminal)
ollama serve

# Pull required models (in another terminal)
ollama pull deepseek-r1:7b
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b-instruct
ollama pull codegemma:7b
ollama pull gemma2:2b-instruct-q4_K_M
ollama pull phi3:mini
ollama pull gemma2:2b  # Optional: standard version

# Initialize database
python scripts/init_db.py

# Add sentiment analysis tables (if not already done)
python scripts/migrate_add_sentiment_tables.py

# Test Ollama connection
python scripts/test_ollama_connection.py
```

**Note**: If you don't have Python 3.12, the setup script will warn you and suggest using it.

### 3. Expected Output

**Database initialization:**
```
✅ Database initialized successfully!
```

**Ollama test:**
```
✅ Local Ollama server connection successful!
Found X available models:
  1. deepseek-r1:7b
  2. qwen2.5-coder:7b-instruct
  3. gemma2:2b
  ...
```

## If You Get Errors

1. **Python not found**: Install Python from python.org (check "Add to PATH")
2. **Activation error**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. **Import errors**: Make sure virtual environment is activated and dependencies are installed
