# Complete Google Colab Setup Guide
## From Zero to GPU-Powered Image Generation in 10 Minutes

This guide will walk you through **every single step** to set up GPU-accelerated image generation using Google Colab, even if you've never used it before.

---

## 📋 What You'll Need

- [ ] Google account (Gmail)
- [ ] Internet connection
- [ ] 10 minutes of time
- [ ] Your local project already set up (`qylysh-higgsfiled` folder)

---

## Part 1: Get Your ngrok Token (3 minutes)

### Step 1.1: Create ngrok Account

1. Open your browser and go to: **https://ngrok.com/**
2. Click the **"Sign up"** button (top right corner)
3. Sign up with:
   - **Recommended:** Click "Sign up with Google" (fastest)
   - **Or:** Enter your email and create a password
4. Verify your email if needed (check your inbox)

### Step 1.2: Get Your Auth Token

1. After signing in, you'll see the ngrok dashboard
2. On the left sidebar, click **"Your Authtoken"** or go to:  
   **https://dashboard.ngrok.com/get-started/your-authtoken**
3. You'll see a token that looks like:
   ```
   2abc123def456ghi789jkl0mno1pqr2stu3vwx4
   ```
4. Click the **"Copy"** button next to the token
5. **Paste it somewhere safe** (like a text file) - you'll need it soon!

✅ **Checkpoint:** You should have a long string of random characters saved somewhere.

---

## Part 2: Upload Notebook to Google Colab (2 minutes)

### Step 2.1: Find the Notebook File

1. On your computer, open the folder: **`qylysh-higgsfiled`**
2. Find the file named: **`colab_setup.ipynb`**
3. **Remember where this file is** (you'll upload it in a moment)

### Step 2.2: Open Google Colab

1. Open a new browser tab
2. Go to: **https://colab.research.google.com/**
3. You might see a welcome popup - click **"Cancel"** or close it
4. You should now see the Colab homepage

### Step 2.3: Upload the Notebook

**Option A: Upload from Computer (Recommended)**

1. In Colab, click **"File"** in the top menu
2. Click **"Upload notebook"**
3. In the popup window, click the **"Upload"** tab
4. Click **"Choose File"** button
5. Navigate to your `qylysh-higgsfiled` folder
6. Select **`colab_setup.ipynb`**
7. Click **"Open"**
8. Wait 5-10 seconds for the upload to complete

**Option B: Upload from GitHub (If you pushed to GitHub)**

1. In Colab, click **"File"** → **"Upload notebook"**
2. Click the **"GitHub"** tab
3. Paste your repo URL: `https://github.com/sapogeth/qylysh-higgsfiled`
4. Click the search icon (🔍)
5. Click on **`colab_setup.ipynb`** when it appears
6. The notebook will open

✅ **Checkpoint:** You should see a notebook with multiple cells of code.

---

## Part 3: Enable GPU (1 minute) ⚡ IMPORTANT!

### Step 3.1: Change Runtime Type

1. At the top of Colab, click **"Runtime"** in the menu bar
2. Click **"Change runtime type"**
3. A popup window appears titled "Notebook settings"
4. Under **"Hardware accelerator"**, click the dropdown
5. Select **"GPU"** (not "None" or "TPU")
6. Under **"GPU type"**, select **"T4"** (this is the free option)
7. Click **"Save"** at the bottom of the popup

✅ **Checkpoint:** You should see "GPU" in the top right corner of Colab (might say "T4" or "Connected").

---

## Part 4: Run the Setup Cells (4 minutes)

Now you'll run each cell in order. Here's how to run a cell:

**How to Run a Cell:**
- **Method 1:** Click the **Play button (▶️)** on the left side of the cell
- **Method 2:** Click inside the cell and press **Shift + Enter**

### 📝 Cell 1: Check GPU

**What it looks like:**
```python
# Check GPU availability
!nvidia-smi
```

**What to do:**
1. Find this cell (it should be the first one)
2. Click the **▶️ button** on the left
3. Wait 5-10 seconds

**What you should see:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx.xx            Driver Version: 535.xx.xx    CUDA: 12.2  |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Type         | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla T4            ...  | 00000000:00:04.0 Off |                    0 |
| N/A   xx°C    P8    xx/70W    |      0MiB / 15360MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

**What this means:** ✅ GPU is working! (You should see "Tesla T4" or similar)

**⚠️ If you see an error:** Go back to Part 3 and make sure you enabled GPU.

---

### 📝 Cell 2: Install Dependencies

**What it looks like:**
```python
# Install required packages
!pip install -q flask python-dotenv pillow requests openai
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install -q diffusers transformers accelerate safetensors peft scipy omegaconf
!pip install -q pyngrok

print("✓ Dependencies installed")
```

**What to do:**
1. Click the **▶️ button** on Cell 2
2. **Wait 2-3 minutes** (this installs a lot of packages)
3. You'll see lots of text scrolling - this is normal!

**What you should see at the end:**
```
✓ Dependencies installed
```

**⚠️ If you see red text:** Don't worry unless the last line says "ERROR". Some warnings are normal.

---

### 📝 Cell 3: Clone Repository

**What it looks like:**
```python
# Option A: Clone from GitHub
!git clone https://github.com/sapogeth/qylysh-higgsfiled.git
%cd qylysh-higgsfiled

print("✓ Repository loaded")
```

**What to do:**
1. **IMPORTANT:** Check if the GitHub URL is correct (`sapogeth/qylysh-higgsfiled`)
2. If it's different, update the URL to match your GitHub username
3. Click the **▶️ button**
4. Wait 10-20 seconds

**What you should see:**
```
Cloning into 'qylysh-higgsfiled'...
/content/qylysh-higgsfiled
✓ Repository loaded
```

**⚠️ Alternative - Manual Upload (if GitHub fails):**

If cloning doesn't work, replace Cell 3 with this:

```python
# Upload files manually
from google.colab import files
import zipfile
import os

print("Please upload your qylysh-higgsfiled.zip file:")
uploaded = files.upload()

# Extract
zip_name = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall('.')

# Navigate to folder
os.chdir('qylysh-higgsfiled')
print("✓ Repository loaded from zip")
```

Then:
1. Zip your `qylysh-higgsfiled` folder on your computer
2. Run the cell
3. Click "Choose Files" and select the zip
4. Wait for upload to complete

---

### 📝 Cell 4: Configure ngrok

**What it looks like:**
```python
# Create .env file with your OpenAI API key
import os
from getpass import getpass

# Optional: For GPT-based story generation
api_key = getpass("Enter your OpenAI API key (or press Enter to skip): ")
if api_key:
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY={api_key}\n')
    print("✓ API key saved")
else:
    print("⚠️  No API key - will use fallback story generation")

# Update config.py for CUDA device
import torch
print(f"\n✓ PyTorch version: {torch.__version__}")
print(f"✓ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
```

**What to do:**
1. Click the **▶️ button**
2. You'll see a text box appear asking for your OpenAI API key
3. **If you have an API key:** Paste it and press Enter
4. **If you don't have one:** Just press Enter to skip (you can still use Colab GPU)

**What you should see:**
```
✓ API key saved
✓ PyTorch version: 2.x.x
✓ CUDA available: True
✓ GPU: Tesla T4
```

---

### 📝 Cell 5: Setup ngrok

**What it looks like:**
```python
# Get ngrok auth token from: https://dashboard.ngrok.com/get-started/your-authtoken
from pyngrok import ngrok, conf
from getpass import getpass

ngrok_token = getpass("Enter your ngrok auth token: ")
conf.get_default().auth_token = ngrok_token

print("✓ ngrok configured")
```

**What to do:**
1. Click the **▶️ button**
2. A text box will appear asking for your ngrok token
3. **Paste the ngrok token** you saved from Part 1
4. Press **Enter**

**What you should see:**
```
✓ ngrok configured
```

**⚠️ If you see an error:** Make sure you pasted the complete token (it's a long string with no spaces).

---

### 📝 Cell 6: Create API Server

**What it looks like:**
```python
# Create a Colab-optimized API server
with open('colab_api.py', 'w') as f:
    f.write('''
from flask import Flask, request, jsonify
...
''')

# Install CORS support
!pip install -q flask-cors

print("✓ API server created")
```

**What to do:**
1. Click the **▶️ button**
2. Wait 5-10 seconds

**What you should see:**
```
✓ API server created
```

**This cell creates the server file - nothing will start yet!**

---

### 📝 Cell 7: Start API Server 🚀 MOST IMPORTANT!

**What it looks like:**
```python
# Start API server with ngrok
from pyngrok import ngrok
import threading
import time

# Start ngrok tunnel
public_url = ngrok.connect(5000)
api_url = f"{public_url}/generate"

print("\n" + "="*70)
print("🌐 COLAB API ENDPOINT:")
print(f"   {public_url}")
print("="*70)
print("\nAdd this to your local .env file:")
print(f"   COLAB_API_URL={public_url}")
print("\n⚠️  Keep this cell running to maintain the API")

# Run Flask in background
def run_api():
    os.system('python colab_api.py')

api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nAPI stopped")
```

**What to do:**
1. Click the **▶️ button**
2. **Wait 60-90 seconds** (this loads the HUGE model - be patient!)
3. Watch for the output to appear

**What you should see after waiting:**
```
Loading SDXL model on GPU...
Loading pipeline components...: 100%|██████████| 7/7 [00:45<00:00, 6.57s/it]
✓ Model ready
 * Serving Flask app 'colab_api'
 * Running on http://127.0.0.1:5000

======================================================================
🌐 COLAB API ENDPOINT:
   https://abc123-456-789.ngrok-free.app    👈👈👈 COPY THIS!
======================================================================

Add this to your local .env file:
   COLAB_API_URL=https://abc123-456-789.ngrok-free.app

⚠️  Keep this cell running to maintain the API
```

**🎯 ACTION REQUIRED:**
1. **Find the URL** that starts with `https://` (in the output above)
2. **Copy the entire URL** (triple-click to select, then Cmd+C or Ctrl+C)
3. **Keep this tab open!** Don't close it or stop the cell!

✅ **Checkpoint:** You have a URL that looks like `https://something.ngrok-free.app`

---

## Part 5: Connect Your Local App (3 minutes)

### Step 5.1: Add URL to Your .env File

1. **Open your terminal** (on your computer, not Colab)
2. **Navigate to your project:**
   ```bash
   cd qylysh-higgsfiled
   ```
3. **Add the Colab URL** (replace with YOUR actual URL from Cell 7):
   ```bash
   echo 'COLAB_API_URL=https://YOUR-ACTUAL-URL.ngrok-free.app' >> .env
   ```

**Real example:**
```bash
echo 'COLAB_API_URL=https://1a2b-34c5-6789.ngrok-free.app' >> .env
```

### Step 5.2: Verify It Was Added

```bash
cat .env
```

**You should see:**
```
OPENAI_API_KEY=sk-...
COLAB_API_URL=https://1a2b-34c5-6789.ngrok-free.app
```

### Step 5.3: Test the Connection

```bash
# Activate your virtual environment
source .venv/bin/activate

# Test connection to Colab
python colab_client.py
```

**You should see:**
```
✓ Connected to Colab API
  Device: cuda
  GPU: Tesla T4
Generating test image...
✓ Test successful! Image saved to: test_colab_output.png
```

**⚠️ If you see an error:**
- Make sure Cell 7 is still running in Colab (don't close the tab!)
- Check that you copied the complete URL with `https://`
- Verify the URL in `.env` has no extra spaces or quotes

---

## Part 6: Start Your Local App & Generate! 🎨

### Step 6.1: Start the Server

```bash
# Make sure you're in the project folder and venv is activated
python app.py
```

**You should see:**
```
✓ Using Colab GPU for generation
======================================================================
🚀 Server starting on http://localhost:8080
======================================================================
```

### Step 6.2: Open in Browser

```bash
# macOS:
open http://localhost:8080

# Linux:
xdg-open http://localhost:8080

# Windows:
start http://localhost:8080

# Or just type in browser: http://localhost:8080
```

### Step 6.3: Generate Your First Storyboard!

1. Enter a story idea in the text box, for example:
   ```
   A greedy merchant learns to share
   ```
2. Click **"Generate Storyboard"**
3. **Wait 60-90 seconds** for the first image (model is loading in Colab)
4. After the first one, each image takes only **15-20 seconds**! ⚡

---

## 🎉 Success!

If you see images appearing one by one, **congratulations!** You're now using free GPU acceleration!

**Performance you should see:**
- First image: ~90 seconds (one-time model load)
- Images 2-6: ~20 seconds each
- Total for 6 frames: ~3 minutes (vs 18 minutes on local CPU!)

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to Colab API"

**Check these things:**

1. **Is Cell 7 still running in Colab?**
   - Go to your Colab tab
   - Look for Cell 7 - it should show a **stop button (■)** not a play button
   - If it stopped, click ▶️ to run it again (you'll get a new URL)

2. **Did you copy the correct URL?**
   - Go back to Colab Cell 7 output
   - Find the line with `https://`
   - Make sure you copied the COMPLETE URL

3. **Is the URL in your .env file correct?**
   ```bash
   cat .env | grep COLAB
   ```
   - Should show: `COLAB_API_URL=https://...`
   - No quotes, no extra spaces

**Fix:**
```bash
# Remove old URL
nano .env  # or open in any text editor
# Delete the COLAB_API_URL line
# Save and exit

# Add new URL
echo 'COLAB_API_URL=https://NEW-URL.ngrok-free.app' >> .env

# Test again
python colab_client.py
```

---

### Problem: "Generation taking forever (more than 2 minutes)"

**Possible causes:**

1. **GPU not enabled in Colab**
   - Go to Colab: Runtime → Change runtime type → GPU → Save
   - Restart all cells from Cell 1

2. **Model still loading**
   - First generation can take 90 seconds
   - Second generation should be faster (~20s)
   - If still slow, check Colab output for errors

3. **Colab session expired**
   - Colab disconnects after 90 minutes of inactivity
   - Look at Colab tab - does it say "Reconnecting"?
   - If yes: Re-run Cell 7, get new URL, update .env

---

### Problem: Red errors in Colab cells

**Common errors and fixes:**

**Error: "ngrok token invalid"**
```
Fix: Go back to Cell 5, paste the correct token from ngrok.com
```

**Error: "Repository not found"**
```
Fix: In Cell 3, make sure the GitHub URL is correct:
https://github.com/YOUR-USERNAME/qylysh-higgsfiled.git
```

**Error: "CUDA out of memory"**
```
Fix: Runtime → Restart runtime → Re-run all cells
```

**Error: "ModuleNotFoundError"**
```
Fix: Go back to Cell 2 and re-run the installation
```

---

### Problem: "Port 8080 already in use"

```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Start again
python app.py
```

---

## 💡 Pro Tips

### Tip 1: Keep Colab Alive

Colab disconnects after 90 minutes of no activity. To prevent this:

**Add this cell after Cell 7:**
```python
# Keep alive cell
import time
from IPython.display import clear_output

while True:
    time.sleep(60)
    clear_output(wait=True)
    print(f"✓ Active at {time.strftime('%H:%M:%S')}")
```

Run this cell and it will print the time every minute, keeping your session alive.

---

### Tip 2: Save Your Notebook

1. In Colab: **File → Save a copy in Drive**
2. Next time: **File → Open notebook → Google Drive**
3. Your notebook will remember your code changes!

---

### Tip 3: Restart After Long Break

If you come back after hours:

1. Check if Cell 7 is still running (look for ■ button)
2. If it stopped: Just click ▶️ on Cell 7 again
3. Copy the **new URL** (it changes each time)
4. Update your local `.env` with the new URL
5. Restart local app: `python app.py`

---

### Tip 4: Monitor GPU Usage

Add this cell to check GPU memory:

```python
!nvidia-smi
```

Run it anytime to see:
- GPU temperature
- Memory usage
- Current processes

---

### Tip 5: ngrok Dashboard

Go to https://dashboard.ngrok.com/endpoints/status

You can see:
- All your active tunnels
- Request count
- Traffic data

Useful if you lose the Colab tab!

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| **First image** | 60-90 seconds (model loading) |
| **Subsequent images** | 15-25 seconds each |
| **Full 6-frame storyboard** | 2-3 minutes |
| **Speed vs local CPU** | **10-20x faster** ⚡ |

---

## 🔄 Restarting Everything

If something goes wrong and you want a fresh start:

### In Google Colab:
1. **Runtime → Restart runtime**
2. **Runtime → Run all** (or run cells 1-7 manually)
3. Wait for Cell 7 to show the ngrok URL
4. Copy the new URL

### On Your Local Machine:
```bash
# Update .env with new URL
nano .env  # Edit COLAB_API_URL line

# Restart app
python app.py
```

---

## 📝 Quick Reference

### Colab Session Limits (Free Tier)
- **Maximum runtime:** 12 hours
- **Idle disconnect:** 90 minutes
- **Concurrent notebooks:** 1 at a time

### When You Need to Update the URL
- ❌ Every time you restart Colab
- ❌ After 12 hours (session expires)
- ❌ If idle timeout happens
- ✅ URL stays same if Cell 7 keeps running

### Essential Commands

**Test Colab connection:**
```bash
python colab_client.py
```

**Start local server:**
```bash
source .venv/bin/activate
python app.py
```

**Check .env file:**
```bash
cat .env
```

**Update URL:**
```bash
echo 'COLAB_API_URL=https://NEW-URL.ngrok-free.app' >> .env
```

---

## ✅ Final Checklist

Before you start generating, make sure:

- [ ] Cell 7 in Colab is running (shows ■ button)
- [ ] You can see "Model ready" in Cell 7 output
- [ ] You copied the ngrok URL from Cell 7
- [ ] The URL is in your local `.env` file
- [ ] `python colab_client.py` test passed
- [ ] Local app started with `python app.py`
- [ ] Browser opened to http://localhost:8080
- [ ] You can see the UI with text input box

**If all checked: You're ready to generate! 🎨**

---

## 🎬 What's Next?

Now that Colab is set up:

1. **Generate your first storyboard** - Try a simple prompt
2. **Experiment with different stories** - Each takes only 2-3 minutes
3. **Enable Identity Lock** - Edit `config.py` for stronger character consistency
4. **Monitor performance** - Watch the speed difference!

---

## 📚 More Resources

- **Full setup guide:** `COLAB_SETUP.md`
- **Quick commands:** `COLAB_QUICKSTART.md`
- **Architecture details:** `COLAB_INTEGRATION_SUMMARY.md`
- **ngrok troubleshooting:** `HOW_TO_FIND_NGROK_URL.md`

---

## 🆘 Still Need Help?

**Common questions:**

**Q: Do I need to pay for Colab?**  
A: No! The free tier is perfect for this project.

**Q: Do I need to pay for ngrok?**  
A: No! Free tier works great. The URL just changes each session.

**Q: Can I use this in production?**  
A: For heavy use, consider Colab Pro ($10/month) or deploy to a real server.

**Q: Will my session expire during generation?**  
A: No, as long as you're generating images, Colab stays active.

**Q: Can I close the Colab tab?**  
A: No! Keep it open. Closing it stops the server.

---

**🎉 Congratulations on setting up GPU acceleration! Enjoy your 10-20x faster image generation!**
