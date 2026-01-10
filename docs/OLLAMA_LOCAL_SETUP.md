# Ollama Local Setup Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Overview

This project uses **local Ollama models** instead of Ollama Cloud. All models run on your local machine, providing:
- ✅ **No API costs**: Completely free
- ✅ **Privacy**: All data stays local
- ✅ **No rate limits**: Unlimited usage
- ✅ **Offline capable**: Works without internet (after initial setup)

---

## Installation

### Step 1: Install Ollama

**Windows**:
```powershell
# Using winget (recommended)
winget install Ollama.Ollama

# Or download from: https://ollama.com/download
```

**Linux/macOS**:
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama
# Or download from: https://ollama.com/download
```

### Step 2: Verify Installation

```bash
ollama --version
```

Expected output: `ollama version is x.x.x`

---

## Starting Ollama Server

### Start Server

```bash
ollama serve
```

**Important**: Keep this terminal open. The server must be running for the application to work.

### Verify Server is Running

Open a new terminal and test:
```bash
curl http://localhost:11434/api/tags
```

Or use the test script:
```bash
python scripts/test_ollama_connection.py
```

---

## Pulling Required Models

### Required Models

The following models must be pulled locally:

1. **Strategy Specialist**:
   ```bash
   ollama pull deepseek-r1:7b
   ollama pull qwen2.5:7b  # Fallback
   ```

2. **Database Librarian**:
   ```bash
   ollama pull qwen2.5-coder:7b-instruct
   ollama pull codegemma:7b  # Fallback
   ```

3. **Telegram Assistant**:
   ```bash
   ollama pull gemma2:2b-instruct-q4_K_M
   ollama pull phi3:mini  # Fallback
   ```

4. **Portfolio Guardian**:
   ```bash
   ollama pull deepseek-r1:7b  # Same as strategy
   ```

### Pull All Models (One Command)

```bash
ollama pull deepseek-r1:7b
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b-instruct
ollama pull codegemma:7b
ollama pull gemma2:2b-instruct-q4_K_M
ollama pull phi3:mini
ollama pull gemma2:2b  # Optional: standard version
```

**Estimated Time**: 30-60 minutes depending on internet speed  
**Total Size**: ~25GB disk space required

### Verify Models

```bash
ollama list
```

Should show all pulled models.

---

## Configuration

### .env File

Add to your `.env` file:

```env
# Ollama Local Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Model Selection
OLLAMA_STRATEGY_MODEL=deepseek-r1:7b
OLLAMA_STRATEGY_FALLBACK=qwen2.5:7b
OLLAMA_DATABASE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_DATABASE_FALLBACK=codegemma:7b
OLLAMA_CHATBOT_MODEL=gemma2:2b
OLLAMA_CHATBOT_FALLBACK=phi3:mini
OLLAMA_GUARDIAN_MODEL=deepseek-r1:7b
```

### Default Configuration

If not specified, the system defaults to:
- **Base URL**: `http://localhost:11434`
- **Models**: As specified in `config/settings.py`

---

## System Requirements

### Minimum Requirements

- **RAM**: 8GB (for 7B models)
- **Storage**: 30GB free space
- **CPU**: Modern multi-core processor

### Recommended Requirements

- **RAM**: 16GB+ (for better performance)
- **Storage**: 50GB+ free space
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for faster inference)

### Model Sizes

| Model | Size | RAM Usage |
|-------|------|-----------|
| deepseek-r1:7b | ~4.1GB | ~8GB |
| qwen2.5:7b | ~4.4GB | ~8GB |
| qwen2.5-coder:7b-instruct | ~4.4GB | ~8GB |
| codegemma:7b | ~4.8GB | ~8GB |
| gemma2:2b-instruct-q4_K_M | ~1.4GB | ~4GB (quantized) |
| phi3:mini | ~2.3GB | ~4GB |
| gemma2:2b | ~1.4GB | ~4GB (optional) |

**Note**: Models are loaded sequentially to manage RAM usage.

---

## Troubleshooting

### Issue: "Connection refused"

**Solution**: Make sure Ollama server is running:
```bash
ollama serve
```

### Issue: "Model not found"

**Solution**: Pull the model:
```bash
ollama pull <model_name>
```

### Issue: "Out of memory"

**Solution**: 
1. Close other applications
2. Use smaller models (2B instead of 7B)
3. Increase system RAM
4. Models load sequentially, so only one is in memory at a time

### Issue: Slow inference

**Solutions**:
1. Use GPU acceleration (if available)
2. Close other applications
3. Use smaller models for faster responses
4. Check system resources (CPU/RAM usage)

---

## GPU Acceleration (Optional)

### NVIDIA GPU

Ollama automatically uses CUDA if available. No additional configuration needed.

### Verify GPU Usage

```bash
ollama run deepseek-r1:7b "test"
# Check GPU usage with: nvidia-smi
```

### AMD GPU

Ollama supports ROCm for AMD GPUs. See [Ollama documentation](https://ollama.com) for setup.

---

## Model Management

### List All Models

```bash
ollama list
```

### Remove Unused Models

```bash
ollama rm <model_name>
```

### Show Model Info

```bash
ollama show <model_name>
```

### Update Models

```bash
ollama pull <model_name>  # Re-pulls latest version
```

---

## Performance Tips

1. **Sequential Loading**: Models load one at a time (by design)
2. **Model Caching**: First inference is slower, subsequent calls are faster
3. **GPU Usage**: Automatically used if available
4. **RAM Management**: Close unused applications
5. **Disk Space**: Keep 50GB+ free for models and cache

---

## Testing

### Test Connection

```bash
python scripts/test_ollama_connection.py
```

### Test Individual Model

```bash
ollama run deepseek-r1:7b "Hello, test"
```

### Test from Python

```python
from services.ollama_service import OllamaService

service = OllamaService()
if service.is_available:
    print("✅ Ollama is working!")
    llm = service.get_strategy_llm()
    if llm:
        response = llm.invoke("Test")
        print(response)
```

---

## Best Practices

1. **Keep Server Running**: Start `ollama serve` before running the application
2. **Pull Models First**: Pull all required models before starting the app
3. **Monitor Resources**: Check RAM/CPU usage during operation
4. **Regular Updates**: Update models periodically: `ollama pull <model>`
5. **Backup Models**: Models are stored locally, backup if needed

---

## Model Storage Location

Models are stored in:
- **Windows**: `%USERPROFILE%\.ollama\models`
- **Linux/macOS**: `~/.ollama/models`

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Start server (`ollama serve`)
3. ✅ Pull required models
4. ✅ Configure `.env` file
5. ✅ Test connection
6. ✅ Start the application

---

**For more information**: See [Ollama Documentation](https://ollama.com)
