# Google Colab GPU Setup - Complete Guide

**Generate images 10-20x faster using free Google GPU!**

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Detailed Setup Guide](#detailed-setup)
3. [Finding Your ngrok URL](#finding-ngrok-url)
4. [Usage & Testing](#usage)
5. [Troubleshooting](#troubleshooting)
6. [Quick Reference](#quick-reference)

---

## Quick Start

### Prerequisites (2 minutes)

1. **ngrok Account** (free)
   - Go to https://ngrok.com/
   - Sign up (use Google login for speed)
   - Copy auth token from https://dashboard.ngrok.com/get-started/your-authtoken

2. **GitHub Repo Access**
   - Make sure your code is pushed to GitHub, OR
   - Prepare to upload files manually

### Setup Steps (5 minutes)

#### In Google Colab:

1. **Open Colab:** https://colab.research.google.com/
2. **Upload notebook:** File → Upload → Select `colab_setup.ipynb`
3. **Enable GPU:** Runtime → Change runtime type → GPU (T4) → Save
4. **Run cells 1-7** (click play button on each)
5. **Copy ngrok URL** from Cell 7 output

#### On Your Local Machine:

```bash
# Add Colab URL to .env
echo "COLAB_API_URL=https://YOUR-NGROK-URL.ngrok-free.app" >> .env

# Test connection
source .venv/bin/activate
python colab_client.py

# Start app
python app.py

# Open browser
open http://localhost:8080
```

**Done! You're now using free GPU acceleration!** ⚡

---

## Detailed Setup

### Part 1: Get ngrok Token (3 minutes)

#### Step 1.1: Create Account
1. Go to **https://ngrok.com/**
2. Click **"Sign up"** (top right)
3. Use "Sign up with Google" (fastest)
4. Verify email if needed

#### Step 1.2: Get Auth Token
1. Go to https://dashboard.ngrok.com/get-started/your-authtoken
2. You'll see a token like: `2abc123def456ghi789jkl0mno1pqr2stu3vwx4`
3. Click **"Copy"**
4. Save it somewhere (you'll need it soon!)

---

### Part 2: Setup Google Colab (5 minutes)

#### Step 2.1: Upload Notebook
1. Open https://colab.research.google.com/
2. File → Upload notebook
3. Select `colab_setup.ipynb` from your project folder
4. Wait for upload to complete

#### Step 2.2: Enable GPU ⚡ IMPORTANT!
1. Runtime → Change runtime type
2. Hardware accelerator: **GPU**
3. GPU type: **T4** (free tier)
4. Click **Save**

You should see "GPU" in top right corner.

#### Step 2.3: Run Setup Cells

**Cell 1: Check GPU**
```python
!nvidia-smi
```
- Click ▶️ play button
- Should see "Tesla T4" in output
- If error → Go back and enable GPU

**Cell 2: Install Dependencies**
```python
!pip install -q flask python-dotenv pillow requests openai flask-cors pyngrok
!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install -q diffusers transformers accelerate safetensors peft
```
- Click ▶️
- Wait 2-3 minutes
- Look for "✓ Dependencies installed"

**Cell 3: Clone Repository**
```python
!git clone https://github.com/YOUR-USERNAME/qylysh-higgsfiled.git
%cd qylysh-higgsfiled
```
- Update GitHub URL to yours
- Click ▶️
- Should see "✓ Repository loaded"

**Alternative - Manual Upload:**
If GitHub fails, replace Cell 3 with:
```python
from google.colab import files
import zipfile, os

print("Upload your project zip:")
uploaded = files.upload()

zip_name = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_name, 'r') as z:
    z.extractall('.')
os.chdir('qylysh-higgsfiled')
print("✓ Repository loaded")
```

**Cell 4: Configure Environment**
```python
from getpass import getpass
api_key = getpass("OpenAI API key (or Enter to skip): ")
if api_key:
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY={api_key}\n')
```
- Enter your API key or press Enter to skip
- Shows CUDA availability

**Cell 5: Setup ngrok**
```python
from pyngrok import ngrok, conf
ngrok_token = getpass("Enter your ngrok auth token: ")
conf.get_default().auth_token = ngrok_token
```
- Paste your ngrok token from Part 1
- Press Enter
- Should see "✓ ngrok configured"

**Cell 6: Create API Server**
```python
# Creates colab_api.py file
```
- Click ▶️
- Wait 10 seconds
- Should see "✓ API server created"

**Cell 7: Start Server** 🚀 MOST IMPORTANT!
```python
# Starts Flask + ngrok tunnel
```
- Click ▶️
- **Wait 60-90 seconds** (loading model)
- Look for output:

```
Loading SDXL model on GPU...
✓ Model ready
======================================================================
🌐 COLAB API ENDPOINT:
   https://abc123-456-789.ngrok-free.app    👈👈👈 COPY THIS!
======================================================================

Add this to your local .env file:
   COLAB_API_URL=https://abc123-456-789.ngrok-free.app

⚠️  Keep this cell running to maintain the API
```

**COPY THE URL!** Keep this cell running!

---

## Finding ngrok URL

### Where to Look

After running Cell 7, look for output **directly below the cell**:

```
╔════════════════════════════════════════════╗
║  🌐 COLAB API ENDPOINT:                    ║
║     https://1a2b3c4d.ngrok-free.app       ║  👈 THIS!
╔════════════════════════════════════════════╗
```

### How to Copy

1. **Triple-click** on the URL to select it
2. Press **Cmd+C** (Mac) or **Ctrl+C** (Windows)
3. URL will look like:
   - `https://abc123.ngrok-free.app`
   - `https://1234-567-890.ngrok.io`

### Important Notes

- **URL changes each session** - normal for free tier
- **Keep Cell 7 running** - stopping it breaks the connection
- **Look in OUTPUT area** - not in the code cell itself

---

## Usage

### Part 3: Connect Local App

#### Step 3.1: Add URL to .env

```bash
# Navigate to project
cd qylysh-higgsfiled

# Add Colab URL (replace with YOUR actual URL)
echo 'COLAB_API_URL=https://YOUR-URL.ngrok-free.app' >> .env
```

**Real example:**
```bash
echo 'COLAB_API_URL=https://1a2b-34c5-6789.ngrok-free.app' >> .env
```

#### Step 3.2: Verify

```bash
cat .env
```

Should see:
```
OPENAI_API_KEY=sk-...
COLAB_API_URL=https://1a2b-34c5-6789.ngrok-free.app
```

#### Step 3.3: Test Connection

```bash
source .venv/bin/activate
python colab_client.py
```

Expected output:
```
✓ Connected to Colab API
  Device: cuda
  GPU: Tesla T4
Generating test image...
✓ Test successful! Image saved to: test_colab_output.png
```

#### Step 3.4: Start App

```bash
python app.py
```

Should see:
```
✓ Using Colab GPU for generation
======================================================================
🚀 Server starting on http://localhost:8080
======================================================================
```

#### Step 3.5: Generate!

1. Open http://localhost:8080
2. Enter prompt: "A greedy merchant learns to share"
3. Click "Generate Storyboard"
4. Watch frames appear in ~20 seconds each! ⚡

---

## Troubleshooting

### "Cannot connect to Colab API"

**Checklist:**
- [ ] Cell 7 is still running (shows ■ button in Colab)
- [ ] ngrok URL is correct in .env
- [ ] No typos in URL
- [ ] No trailing slash in URL
- [ ] Internet connection stable

**Test:**
```bash
curl https://YOUR-URL.ngrok-free.app/health
```

Should return: `{"status": "healthy", "device": "cuda"}`

**Fix:**
```bash
# Update .env with new URL
nano .env  # Edit COLAB_API_URL line
# OR
echo 'COLAB_API_URL=https://NEW-URL.ngrok-free.app' >> .env

# Test again
python colab_client.py
```

---

### "Generation taking forever"

**Possible causes:**
1. **First generation:** Takes 90s to load model (normal)
2. **GPU not enabled:** Runtime → Change runtime type → GPU
3. **Session expired:** Re-run Cell 7, get new URL

**Check GPU:**
In Colab:
```python
!nvidia-smi
import torch
print(torch.cuda.is_available())  # Should be True
```

---

### Red Errors in Colab

**"ngrok token invalid"**
- Go to Cell 5, paste correct token from ngrok.com

**"Repository not found"**
- Check GitHub URL in Cell 3

**"CUDA out of memory"**
- Runtime → Restart runtime → Re-run all cells

**"ModuleNotFoundError"**
- Re-run Cell 2 (installation)

---

### "Port 8080 already in use"

```bash
lsof -ti:8080 | xargs kill -9
python app.py
```

---

### "Session expired"

Colab disconnects after:
- 12 hours max runtime
- 90 minutes idle

**Solution:**
1. Re-run Cell 7 in Colab
2. Copy NEW ngrok URL
3. Update local .env
4. Restart local app

---

## Quick Reference

### Performance Comparison

| Method | Per Image | 6 Frames | Cost |
|--------|-----------|----------|------|
| M1 CPU | 3 min | 18 min | $0 |
| M1 MPS | 1 min | 6 min | $0 |
| **Colab T4** | **20s** | **2 min** | **$0** ⭐ |
| DALL-E | 25s | 3 min | $0.24 |

**Winner: Colab - 10-20x faster AND free!**

---

### Essential Commands

**Test Colab:**
```bash
python colab_client.py
```

**Start app:**
```bash
source .venv/bin/activate
python app.py
```

**Check .env:**
```bash
cat .env | grep COLAB
```

**Update URL:**
```bash
echo 'COLAB_API_URL=https://NEW-URL.ngrok-free.app' >> .env
```

**Test direct:**
```bash
curl https://YOUR-URL.ngrok-free.app/health
```

---

### Colab Session Limits (Free Tier)

- **Max runtime:** 12 hours
- **Idle disconnect:** 90 minutes
- **Concurrent notebooks:** 1
- **URL lifetime:** Until session ends

---

### Keep Session Alive

Add this cell after Cell 7:

```python
import time
from IPython.display import clear_output

while True:
    time.sleep(60)
    clear_output(wait=True)
    print(f"✓ Active at {time.strftime('%H:%M:%S')}")
```

---

### Quick Restart Flow

When Colab disconnects:

```bash
# 1. In Colab: Click ▶️ on Cell 7
# 2. Copy new ngrok URL
# 3. On local machine:

export COLAB_API_URL="https://NEW-URL.ngrok-free.app"
# OR update .env file

# 4. Restart app
python app.py
```

---

### Monitor GPU

In Colab:
```python
!nvidia-smi

import torch
print(f"Memory: {torch.cuda.memory_allocated()/1e9:.2f} GB")
```

---

### ngrok Dashboard

https://dashboard.ngrok.com/endpoints/status

See:
- Active tunnels
- Request count
- Traffic data
- Find URL if you lost it

---

## Pro Tips

### Tip 1: Save Notebook to Drive
File → Save a copy in Drive → Next time opens instantly

### Tip 2: Bookmark URLs
- Colab: https://colab.research.google.com/
- ngrok: https://dashboard.ngrok.com/
- Local: http://localhost:8080

### Tip 3: Static URLs
Upgrade ngrok to paid ($8/mo) for permanent URLs

### Tip 4: Colab Pro
For heavy use: $10/month gets:
- 24h sessions
- V100/A100 GPUs (2x faster)
- Priority access

### Tip 5: Test Before Full Run

In Colab before starting server:
```python
from local_image_generator import LocalImageGenerator
gen = LocalImageGenerator(lazy_load=False)
test = gen.generate_single("Aldar Kose walking")
test.save("test.png")
```

---

## Architecture Flow

```
User Browser
    ↓
Local Flask (localhost:8080)
    ↓
Check COLAB_API_URL?
    ├─ Not set → DALL-E API
    └─ Set ↓
        ngrok tunnel
            ↓
        Colab Flask API
            ↓
        SDXL + GPU (Tesla T4)
            ↓
        Return PNG (base64)
            ↓
        Save to static/generated/
            ↓
        Display in browser
```

---

## Success Checklist

Before generating, verify:

- [ ] Cell 7 running in Colab (■ button visible)
- [ ] "Model ready" in Cell 7 output
- [ ] ngrok URL copied
- [ ] URL in local .env file
- [ ] `python colab_client.py` passes
- [ ] Local app shows "Using Colab GPU"
- [ ] Browser opens to http://localhost:8080
- [ ] UI loads with text input

**All checked?** → Ready to generate! 🎨

---

## Expected Performance

| Metric | Value |
|--------|-------|
| First image | 60-90s (model loading) |
| Subsequent images | 15-25s each |
| Full 6-frame storyboard | 2-3 minutes |
| Speed vs local CPU | **10-20x faster** ⚡ |
| Speed vs M1 MPS | **3-5x faster** |
| Cost | **$0** (free tier) |

---

## Support

**Not working?**
1. Run `python colab_client.py` for diagnostics
2. Check both Colab AND local terminal for errors
3. Verify URL has no typos
4. Make sure Cell 7 is running
5. Check internet connection

**Resources:**
- ngrok docs: https://ngrok.com/docs
- Colab FAQ: https://research.google.com/colaboratory/faq.html
- Diffusers: https://huggingface.co/docs/diffusers

**Still stuck?**
Open GitHub issue with:
- Error message
- Colab output
- Local terminal output
- Steps to reproduce

---

## Summary

**Google Colab provides 10-20x faster generation with zero cost:**

- ⚡ 20 seconds per image (vs 3 minutes local)
- 💰 100% free (up to 12h/day)
- 🚀 5 minute setup
- 🔄 Works alongside local generation
- 📊 Same quality as local SDXL

**Perfect for:** Rapid prototyping, batch generation, testing

**Not ideal for:** Production (sessions expire), 24/7 use

---

**🎉 Congratulations! You're now using free GPU acceleration!**

**Next:** Generate your first storyboard and enjoy the speed! 🎨
