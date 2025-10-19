# How to Find the ngrok URL in Google Colab

## 📍 Quick Answer

After running **Cell 6** in the Colab notebook, look for this output **directly below the cell**:

```
======================================================================
🌐 COLAB API ENDPOINT:
   https://abc123-456-789.ngrok-free.app    👈 COPY THIS URL!
======================================================================

Add this to your local .env file:
   COLAB_API_URL=https://abc123-456-789.ngrok-free.app
```

---

## Step-by-Step Visual Guide

### 1. Find Cell 6 in Google Colab

Scroll down in your Colab notebook until you see:

```python
# Cell 6: Start Server
from pyngrok import ngrok
import threading
...
```

### 2. Run the Cell

Click the **Play button (▶️)** on the left side of Cell 6.

```
┌──────────────────────────────────┐
│  [▶️] Cell 6: Start Server       │  ← Click this play button
└──────────────────────────────────┘
```

### 3. Wait for Output

After 10-30 seconds, you'll see output appear in a box **below** the cell.

### 4. Look in the Output Box

The output box is the **white/gray area directly under the code cell**. It looks like this:

```
╔════════════════════════════════════════════════╗
║  OUTPUT AREA (appears below the code cell)     ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Loading SDXL model on GPU...                  ║
║  ✓ Model ready                                 ║
║  ══════════════════════════════════════════    ║
║  🌐 COLAB API ENDPOINT:                        ║
║     https://1a2b3c4d.ngrok-free.app           ║  👈 THIS IS IT!
║  ══════════════════════════════════════════    ║
║                                                ║
║  Add this to your local .env file:             ║
║     COLAB_API_URL=https://1a2b3c4d...          ║
║                                                ║
║  ⚠️  Keep this cell running to maintain API    ║
╚════════════════════════════════════════════════╝
```

### 5. Copy the URL

**Triple-click** on the URL line to select it, then press **Cmd+C** (Mac) or **Ctrl+C** (Windows).

The URL will look like:
- `https://abc123.ngrok-free.app`
- `https://1234-567-890.ngrok.io`
- `https://randomtext.ngrok-free.app`

---

## ⚠️ Important Things to Know

### The URL Changes Every Time
- Each time you restart the Colab notebook, you get a **new URL**
- You must update your local `.env` file with the new URL

### The Cell Must Keep Running
- **Don't stop Cell 6** or the URL will stop working
- If you see a **stop button (■)** next to the cell, that's good - it means it's running
- If the cell stops, just run it again and get the new URL

### Where NOT to Look
❌ Don't look in the code cell itself (the Python code)  
❌ Don't look at the cell number  
✅ Look in the **OUTPUT** area below the cell  

---

## 🎯 What to Do With the URL

Once you have the URL, go to your **local terminal** and run:

```bash
# Navigate to your project
cd qylysh-higgsfiled

# Add the URL to your .env file (replace with YOUR actual URL)
echo 'COLAB_API_URL=https://YOUR-ACTUAL-URL.ngrok-free.app' >> .env
```

**Real example:**
```bash
echo 'COLAB_API_URL=https://1a2b3c4d-567e.ngrok-free.app' >> .env
```

### Verify It Was Added

```bash
# Check your .env file
cat .env

# You should see:
# OPENAI_API_KEY=sk-...
# COLAB_API_URL=https://1a2b3c4d.ngrok-free.app
```

---

## 🔍 Troubleshooting

### "I don't see any output"

**Possible causes:**
1. Cell is still running - wait 30 seconds more
2. Cell hasn't been executed - click the ▶️ button
3. Scroll down - output might be below the visible area

**Solution:** Click the ▶️ button and wait for the output to appear.

---

### "I see errors in red text"

**Common errors and fixes:**

**Error: "ngrok token not configured"**
```
Solution: Go back to Cell 4 and enter your ngrok token
```

**Error: "No module named 'flask'"**
```
Solution: Go back to Cell 2 and re-run the installation cell
```

**Error: "CUDA out of memory"**
```
Solution: Runtime → Restart runtime, then run all cells again
```

---

### "The output disappeared"

**Solution:** Click anywhere in the output area to expand it, or re-run Cell 6.

---

### "Which URL do I copy?"

If you see multiple URLs, copy the one that appears after:
```
🌐 COLAB API ENDPOINT:
```

**Example - CORRECT URL to copy:**
```
🌐 COLAB API ENDPOINT:
   https://abc123.ngrok-free.app    👈 Copy this one
```

**Don't copy:**
- URLs from other cells
- URLs in the code itself
- URLs with extra text before/after

---

## 📋 Quick Checklist

Before moving to the next step, make sure:

- [ ] Cell 6 is running (shows ■ stop button or spinning animation)
- [ ] You can see the output box below Cell 6
- [ ] You found the line starting with `https://`
- [ ] You copied the complete URL
- [ ] The URL ends with `.ngrok-free.app` or `.ngrok.io`

---

## 🎬 What Happens Next

After adding the URL to your `.env` file:

1. **Test the connection:**
   ```bash
   python colab_client.py
   ```

2. **Start your local app:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   ```bash
   open http://localhost:8080
   ```

4. **Generate a storyboard** and watch it use Colab's GPU! ⚡

---

## 💡 Pro Tip

**Bookmark the ngrok dashboard:** https://dashboard.ngrok.com/endpoints/status

You can see all your active tunnels there, including the current URL, even if you lose the Colab tab!

---

## Need More Help?

- **Can't find the output?** → Take a screenshot of your Colab page and check if Cell 6 is running
- **URL not working?** → Make sure Cell 6 is still running (don't close Colab tab)
- **Need to restart?** → Just re-run Cell 6 and get a new URL

**Remember:** The ngrok URL is free and temporary. It's normal to get a new one each session!
