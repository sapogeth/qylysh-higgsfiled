# Google Colab Integration Guide

Connect your local Flask app to Google Colab's free GPU for **10-20x faster** SDXL image generation.

## Why Colab?

- **Free GPU access** (NVIDIA T4 or better)
- **No local ML setup needed** - Keep your lightweight local UI
- **Faster generation** - 15-30 seconds per image vs. 2-3 minutes locally
- **No model downloads** - Colab handles the 7GB+ SDXL model

---

## Quick Setup (5 minutes)

### 1. Get ngrok Token

1. Go to [ngrok.com](https://ngrok.com/) and sign up (free)
2. Copy your auth token from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)

### 2. Upload to Google Colab

**Option A: From GitHub (Recommended)**
```python
# In Colab notebook cell:
!git clone https://github.com/sapogeth/qylysh-higgsfiled.git
%cd qylysh-higgsfiled
```

**Option B: Upload manually**
- Zip your project folder
- Upload to Colab: Files → Upload
- Extract: `!unzip qylysh-higgsfiled.zip`

### 3. Open the Colab Notebook

Open `colab_setup.ipynb` in Google Colab:

1. Upload `colab_setup.ipynb` to Colab
2. **Enable GPU**: Runtime → Change runtime type → GPU (T4)
3. Run cells in order

### 4. Connect Your Local App

After running the Colab notebook, you'll get a public URL like:
```
https://abc123.ngrok.io
```

Add this to your local `.env` file:
```bash
COLAB_API_URL=https://abc123.ngrok.io
```

### 5. Restart Local App

```bash
source .venv/bin/activate
python app.py
```

✓ Your local UI now uses Colab GPU automatically!

---

## Two Modes

### Mode 1: Full Server (Simplest)

Run the entire Flask app in Colab with public URL.

**Pros:**
- One URL for everything
- Share with anyone
- No local setup needed

**Cons:**
- UI customization requires Colab edits
- Session expires after ~12 hours

**Setup:**
Run cells in section **4A** of the notebook.

### Mode 2: API-Only (Recommended)

Keep your local Flask UI, offload only generation to Colab.

**Pros:**
- Edit UI/code locally in real-time
- Faster iteration
- Best performance

**Cons:**
- Need local Flask running
- Two processes to manage

**Setup:**
1. Run cells in section **4B** of the notebook
2. Add `COLAB_API_URL` to local `.env`
3. Restart local `app.py`

---

## Usage

Once connected:

1. Open your local app: http://localhost:8080
2. Check "Lock identity to reference" for IP-Adapter (if Colab has it loaded)
3. Generate normally - images now use Colab GPU!

**Logs show:**
```
✓ Colab GPU backend available
✓ Using Colab GPU for generation
Device: cuda
GPU: Tesla T4
```

---

## Troubleshooting

### "Cannot connect to Colab API"

**Check:**
1. Colab notebook cell is still running (green play icon)
2. ngrok tunnel is active (should see URL in output)
3. `COLAB_API_URL` in `.env` matches the ngrok URL exactly
4. No firewall blocking outgoing connections

**Test connection:**
```bash
source .venv/bin/activate
python colab_client.py
```

### "Colab generation timed out"

- First generation takes 1-2 minutes to load model
- Subsequent generations are much faster (15-30s)
- Colab may have disconnected - check notebook

### "Session expired"

Colab free tier disconnects after:
- 12 hours of runtime
- 90 minutes of inactivity

**Solution:** Re-run the server cell to get a new ngrok URL.

### Generation still slow

**Check GPU is enabled:**
- Colab: Runtime → Change runtime type → GPU
- Should see "GPU: Tesla T4" in logs

**Without GPU:**
- 2-3 minutes per image (same as local CPU)

**With GPU:**
- 15-30 seconds per image

---

## Performance Comparison

| Mode | Setup Time | Generation Speed | Cost |
|------|-----------|-----------------|------|
| **Local M1 CPU** | 0 min | 2-3 min/image | Free |
| **Local M1 MPS** | 5 min (torch install) | 60-90 sec/image | Free |
| **Colab GPU** | 5 min (one-time) | 15-30 sec/image | Free |
| **Local NVIDIA GPU** | Varies | 10-20 sec/image | Hardware cost |

---

## Advanced: Keep Colab Alive

Colab disconnects after 90 minutes of inactivity. To prevent this:

```python
# Add to Colab notebook
import time
from IPython.display import clear_output

while True:
    time.sleep(60)
    clear_output(wait=True)
    print(f"Active at {time.strftime('%H:%M:%S')}")
```

Or use browser extensions like "Colab Keep Alive" (search Chrome Web Store).

---

## Security Notes

- **ngrok URLs are public** - Anyone with the URL can generate images
- For production, add authentication in `colab_api.py`
- Free ngrok URLs change each session (upgrade to static URLs)
- Never commit ngrok tokens or API keys to git

---

## Cost Analysis

**Colab Free Tier:**
- GPU: ~12 hours/day
- High-RAM: Limited
- TPU: Available

**Colab Pro ($10/month):**
- Longer runtimes
- Faster GPUs (V100/A100)
- Background execution

**For this project, free tier is sufficient.**

---

## Next Steps

After Colab is working:

1. **Add authentication** to API endpoint
2. **Cache models** in Colab session for faster startup
3. **Batch generation** for multiple frames at once
4. **Monitor usage** to stay within Colab limits

---

## Need Help?

**Common issues:**
- Port 8080 blocked → Change port in `app.py`
- ngrok token expired → Get new token from dashboard
- GPU not available → Check runtime type in Colab
- Connection refused → Restart both Colab and local app

**Test each component:**
```bash
# Test local app (without Colab)
unset COLAB_API_URL
python app.py

# Test Colab connection
python colab_client.py

# Test end-to-end
python app.py
# Open browser → Generate
```
