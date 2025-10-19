# Colab Quick Reference

## Initial Setup (Once)

1. **Enable GPU in Colab:**
   - Runtime → Change runtime type → GPU → Save

2. **Get ngrok token:**
   - Sign up: https://ngrok.com/
   - Get token: https://dashboard.ngrok.com/get-started/your-authtoken

## Every Session

### In Google Colab:

```python
# 1. Install dependencies
!pip install -q flask python-dotenv pillow requests openai flask-cors pyngrok
!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install -q diffusers transformers accelerate safetensors peft

# 2. Clone repo
!git clone https://github.com/sapogeth/qylysh-higgsfiled.git
%cd qylysh-higgsfiled

# 3. Configure ngrok
from pyngrok import ngrok, conf
conf.get_default().auth_token = "YOUR_NGROK_TOKEN"

# 4. Start server
from pyngrok import ngrok
import threading
import os

public_url = ngrok.connect(5000)
print(f"🌐 PUBLIC URL: {public_url}")

def run_api():
    # Create simple API file first (see COLAB_SETUP.md)
    os.system('python colab_api.py')

threading.Thread(target=run_api, daemon=True).start()

# Keep running
import time
while True:
    time.sleep(1)
```

### On Your Local Machine:

```bash
# 1. Add Colab URL to .env
echo "COLAB_API_URL=https://YOUR-NGROK-URL.ngrok.io" >> .env

# 2. Test connection
source .venv/bin/activate
python colab_client.py

# 3. Start local app
python app.py

# 4. Open browser
open http://localhost:8080
```

## Test Generation

```bash
# In local terminal
curl -X POST http://localhost:8080/api/generate/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test story about sharing bread"}'
```

## Monitor Colab

```python
# In Colab, check GPU usage
!nvidia-smi

# Check memory
import torch
print(f"GPU Memory: {torch.cuda.memory_allocated()/1e9:.2f} GB")
```

## Stop & Restart

```bash
# Stop local app
Ctrl+C

# Stop Colab
# Click stop button or: Ctrl+M then I

# Restart Colab
# Re-run the server cell (you'll get a new ngrok URL)
# Update COLAB_API_URL in local .env
```

## Troubleshooting One-Liners

```bash
# Test if Colab is reachable
curl https://YOUR-NGROK-URL.ngrok.io/health

# Check local .env
cat .env | grep COLAB

# Clear local cache
rm -rf static/generated/*.png

# Kill stuck process
lsof -ti:8080 | xargs kill -9
```

## Performance Tips

**Colab:**
- First generation: ~90 seconds (model loading)
- Subsequent: ~20 seconds each
- Keep session active (run every 30 min)

**Local:**
- API mode: instant UI + 20s generation
- Full mode: 2-3 min on M1 CPU

## Common URLs

- **Colab notebook:** https://colab.research.google.com/
- **ngrok dashboard:** https://dashboard.ngrok.com/
- **Local app:** http://localhost:8080
- **Colab API:** https://YOUR-URL.ngrok.io

## Quick Restart Flow

```bash
# 1. In Colab: re-run server cell
# 2. Copy new ngrok URL
# 3. On local:
export COLAB_API_URL="https://NEW-URL.ngrok.io"
python app.py
```

## Health Check

```python
# Test everything is working
import requests

# Test local app
print(requests.get("http://localhost:8080/api/health").json())

# Test Colab API
import os
colab_url = os.getenv("COLAB_API_URL")
print(requests.get(f"{colab_url}/health").json())
```
