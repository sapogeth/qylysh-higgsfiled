# Colab Setup - Visual Workflow

## 🎯 Goal
Run SDXL image generation on free Google GPU (10-20x faster than local)

---

## 📋 Prerequisites (2 minutes)

### 1. ngrok Account
```
→ Go to https://ngrok.com/
→ Sign up (free)
→ Copy auth token from dashboard
   Example: 2abc...xyz9
```

### 2. GitHub Repo Access
```
→ Make sure code is pushed to GitHub
→ Or prepare to upload manually
```

---

## 🚀 Step-by-Step Setup (5 minutes)

### PART A: In Google Colab

#### Step 1: Open Colab
```
→ Go to https://colab.research.google.com/
→ File → Upload notebook
→ Select colab_setup.ipynb
```

#### Step 2: Enable GPU
```
→ Runtime → Change runtime type
→ Hardware accelerator: GPU
→ GPU type: T4 (default free tier)
→ Save
```

#### Step 3: Run Setup Cells
```
Cell 1: Check GPU
→ Click play button
→ Should see "Tesla T4" or similar

Cell 2: Install Dependencies
→ Click play button
→ Wait 2-3 minutes
→ Look for "✓ Dependencies installed"

Cell 3: Clone Repo
→ Update with your GitHub URL
→ Or upload files manually
→ Click play button
```

#### Step 4: Configure ngrok
```
Cell 4: Setup ngrok
→ Paste your ngrok auth token
→ Click play button
→ Look for "✓ ngrok configured"
```

#### Step 5: Start API Server
```
Cell: Run API server (Mode 2)
→ Click play button
→ Copy the ngrok URL shown:
   
   🌐 COLAB API ENDPOINT:
      https://abc123.ngrok.io/generate
   
→ KEEP THIS CELL RUNNING!
```

---

### PART B: On Your Local Machine

#### Step 6: Add Colab URL
```bash
# Open .env file
nano .env

# Add this line (use YOUR ngrok URL):
COLAB_API_URL=https://abc123.ngrok.io

# Save and exit (Ctrl+X, Y, Enter)
```

#### Step 7: Test Connection
```bash
# Activate virtual environment
source .venv/bin/activate

# Test Colab connection
python colab_client.py

# Should see:
# ✓ Connected to Colab API
#   Device: cuda
#   GPU: Tesla T4
```

#### Step 8: Start Local App
```bash
# Start Flask server
python app.py

# Should see:
# ✓ Using Colab GPU for generation
# 🚀 Server starting on http://localhost:8080
```

#### Step 9: Open Browser
```
→ Go to http://localhost:8080
→ Enter a prompt
→ Check "Lock identity to reference" (optional)
→ Click "Generate Storyboard"
→ Watch frames appear in ~20 seconds each!
```

---

## 🔍 Verification Checklist

After setup, verify each part:

- [ ] Colab cell shows "Running" (green play icon)
- [ ] ngrok URL is visible in Colab output
- [ ] Local .env contains COLAB_API_URL
- [ ] `python colab_client.py` succeeds
- [ ] Local app shows "Using Colab GPU"
- [ ] Browser can access http://localhost:8080
- [ ] First generation takes ~90s (model loading)
- [ ] Second generation takes ~20s (fast!)

---

## 🎨 Usage Flow

```
┌──────────────┐
│ Enter Prompt │
└──────┬───────┘
       │
       ↓
┌──────────────────────┐
│ Local Flask receives │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ Check COLAB_API_URL  │
└──────┬───────────────┘
       │
       ├─→ Not Set → Use DALL-E API
       │
       └─→ Set ↓
           
┌──────────────────────┐
│ Send to Colab via    │
│ ngrok tunnel         │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ Colab GPU generates  │
│ (~20 seconds)        │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ Return base64 PNG    │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ Local saves & shows  │
│ in browser           │
└──────────────────────┘
```

---

## ⚡ Performance Comparison

### One Image (1024x1024)

| Method | Time | Notes |
|--------|------|-------|
| Local M1 CPU | 3 min | Slow but free |
| Local M1 MPS | 1 min | Need torch install |
| **Colab GPU** | **20 sec** | ⭐ Recommended |
| DALL-E API | 25 sec | Costs money |

### Full Storyboard (6 frames)

| Method | Time | Cost |
|--------|------|------|
| Local M1 CPU | 18 min | $0 |
| Local M1 MPS | 6 min | $0 |
| **Colab GPU** | **2 min** | **$0** ⭐ |
| DALL-E API | 3 min | $0.24 |

**Winner: Colab GPU - Fastest AND Free!**

---

## 🔧 Common Issues & Fixes

### Issue: "Cannot connect to Colab API"
```bash
# Check if Colab cell is still running
→ Look for green play icon in Colab

# Verify URL is correct
cat .env | grep COLAB_API_URL

# Test directly
curl https://YOUR-URL.ngrok.io/health
```

### Issue: "Address already in use"
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Restart app
python app.py
```

### Issue: Generation still slow
```bash
# Check GPU is enabled in Colab
→ Runtime → Change runtime type → GPU

# Verify in Colab notebook:
import torch
print(torch.cuda.is_available())  # Should be True
```

### Issue: "Session expired"
```
→ Colab disconnects after 12 hours or 90 min idle
→ Solution: Re-run the server cell in Colab
→ Copy the NEW ngrok URL
→ Update .env with new URL
→ Restart local app
```

---

## 📊 Session Management

### Colab Free Tier Limits
- ⏱️ 12 hours max runtime per session
- 💤 90 minutes idle = disconnect
- 🔄 New session = new ngrok URL

### Keep Session Alive
Add this cell to Colab:
```python
import time
while True:
    print(f"Active: {time.strftime('%H:%M:%S')}")
    time.sleep(60)
```

Or use browser extension: "Colab Keep Alive"

---

## 🎓 Pro Tips

### Tip 1: Bookmark ngrok Dashboard
```
https://dashboard.ngrok.com/
→ See all active tunnels
→ Check usage stats
→ Upgrade to static URLs ($8/mo)
```

### Tip 2: Save Colab Notebook to Drive
```
File → Save a copy in Drive
→ Auto-saves your setup
→ Faster restart next time
```

### Tip 3: Test Generation First
```python
# In Colab, before starting server:
from local_image_generator import LocalImageGenerator
gen = LocalImageGenerator(lazy_load=False)
test_img = gen.generate_single("Aldar Kose walking")
test_img.save("test.png")
```

### Tip 4: Monitor GPU Usage
```python
# In Colab:
!nvidia-smi

# Check memory:
import torch
print(f"Used: {torch.cuda.memory_allocated()/1e9:.2f} GB")
```

### Tip 5: Batch Multiple Frames
When generating a full storyboard, Colab will:
- Load model once (90 seconds)
- Generate 6 frames at ~20s each
- Total: ~3 minutes vs 18 minutes locally

---

## 📖 Additional Resources

**Files to Read:**
- `COLAB_SETUP.md` - Detailed setup guide
- `COLAB_QUICKSTART.md` - Command reference
- `COLAB_INTEGRATION_SUMMARY.md` - Architecture & troubleshooting

**External Links:**
- ngrok: https://ngrok.com/docs
- Colab: https://research.google.com/colaboratory/faq.html
- Diffusers: https://huggingface.co/docs/diffusers

**Support:**
- Open GitHub issue with error logs
- Include both Colab and local terminal output

---

## ✅ Success Indicators

You know it's working when:

1. ✅ Colab shows: `Device: cuda, GPU: Tesla T4`
2. ✅ Local app shows: `✓ Using Colab GPU for generation`
3. ✅ First frame: ~90 seconds (model loading)
4. ✅ Other frames: ~20 seconds each
5. ✅ Total 6-frame storyboard: ~3 minutes
6. ✅ Images saved to `static/generated/`

**If all ✅ → You're successfully using free GPU! 🎉**

---

## 🚦 Quick Start Commands

```bash
# 1. Setup (in Colab)
!git clone https://github.com/YOUR-USERNAME/qylysh-higgsfiled.git
%cd qylysh-higgsfiled
# Run server cell, copy ngrok URL

# 2. Configure (local)
echo "COLAB_API_URL=https://YOUR-URL.ngrok.io" >> .env

# 3. Test (local)
source .venv/bin/activate
python colab_client.py

# 4. Run (local)
python app.py

# 5. Use (browser)
open http://localhost:8080
```

**Total time: 5 minutes → 10x speed boost! 🚀**
