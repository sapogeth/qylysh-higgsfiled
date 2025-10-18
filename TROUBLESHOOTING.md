# Troubleshooting Guide

## Common Issues and Solutions

### Port 5000 Already in Use (macOS)

**Problem:**
```
Address already in use
Port 5000 is in use by another program
```

**Reason:** macOS uses port 5000 for AirPlay Receiver service.

**Solution 1: Use Port 8080 (Recommended)**
The app now defaults to port 8080. Just run:
```bash
python app.py
```
Visit: **http://localhost:8080**

**Solution 2: Disable AirPlay Receiver**
1. Open System Preferences (System Settings on macOS 13+)
2. Go to General → AirDrop & Handoff
3. Turn off "AirPlay Receiver"
4. Restart the app

**Solution 3: Use Custom Port**
Edit `app.py` and change the port number:
```python
port = 8080  # Change to any available port (8080, 3000, 8000, etc.)
```

---

## Installation Issues

### Problem: pip install fails

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Try with specific Python version
python3 -m pip install -r requirements.txt

# If on macOS and getting SSL errors
pip install --upgrade certifi
```

### Problem: Python version too old

**Check version:**
```bash
python --version  # Need 3.8+
```

**Solution:**
- Install Python 3.8+ from python.org
- Or use: `brew install python@3.11` (macOS with Homebrew)

---

## API Key Issues

### Problem: "No API key configured"

**Check if .env exists:**
```bash
ls -la .env
```

**If not, create it:**
```bash
cp .env.example .env
```

**Edit .env and add your key:**
```
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

**Verify it worked:**
```bash
python test_api.py
```

### Problem: API key not working

**Check the key format:**
- Should start with `sk-`
- No spaces or quotes around it
- No extra newlines

**Test your key:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Get a new key:**
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy it immediately (shown only once!)
4. Paste into `.env` file

---

## Generation Issues

### Problem: "Generation taking too long"

**This is normal!**
- DALL-E 3: ~40 seconds per image
- 8 frames: ~5-7 minutes total
- Don't refresh the page!

**Speed it up:**
- Use fewer frames (edit code to generate 6 instead of 8)
- Use DALL-E 2 instead (lower quality, faster)
- Start with simpler prompts for testing

### Problem: Getting placeholder images instead of AI images

**Reasons:**
1. No API key configured
2. API key invalid
3. No API credits remaining
4. OpenAI API temporarily down

**Diagnosis:**
```bash
python test_api.py
```

**Check your usage/credits:**
https://platform.openai.com/usage

### Problem: "Rate limit exceeded"

**Reason:** Too many requests too quickly

**Solutions:**
- Wait 1-2 minutes and try again
- Upgrade your OpenAI plan for higher limits
- Space out your requests

---

## Image Issues

### Problem: Images not displaying

**Check folder exists:**
```bash
ls -la static/generated/
```

**If missing, create it:**
```bash
mkdir -p static/generated
```

**Check permissions:**
```bash
# Make sure Flask can write to the folder
chmod 755 static/generated
```

**Check browser console:**
- Press F12 in browser
- Look for errors in Console tab
- Check Network tab for failed requests

### Problem: Images download as corrupted files

**Solution:**
- Clear browser cache
- Try different browser
- Check disk space: `df -h`

---

## Frontend Issues

### Problem: Page doesn't load

**Check server is running:**
```bash
# You should see:
# * Running on http://0.0.0.0:8080
```

**Try different browser:**
- Chrome, Firefox, Safari all work

**Check URL:**
- Should be `http://localhost:8080` (not https)
- Port 8080 (not 5000)

### Problem: "Generate" button doesn't work

**Open browser console (F12):**
- Look for JavaScript errors
- Check Network tab for failed API calls

**Verify API is working:**
```bash
curl http://localhost:8080/api/health
# Should return: {"status":"healthy","timestamp":"..."}
```

**Hard refresh:**
- Chrome/Firefox: Ctrl+Shift+R (Cmd+Shift+R on Mac)
- Safari: Cmd+Option+R

---

## Dependencies Issues

### Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: "ModuleNotFoundError: No module named 'PIL'"

**Solution:**
```bash
pip install Pillow
```

### Problem: Multiple Python versions conflicting

**Use virtual environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

---

## Testing Issues

### Problem: test_api.py fails

**Run with verbose output:**
```bash
python -v test_api.py
```

**Check common issues:**
1. No .env file → Create it
2. Wrong API key → Verify on OpenAI dashboard
3. No internet connection → Check network
4. OpenAI API down → Check status.openai.com

---

## Performance Issues

### Problem: Server is slow

**Increase Flask workers (production):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Problem: Out of memory

**Reduce concurrent requests:**
- Generate one storyboard at a time
- Close other applications
- Restart the server between requests

---

## macOS Specific Issues

### Problem: "Permission denied" when running run.sh

**Make it executable:**
```bash
chmod +x run.sh
./run.sh
```

### Problem: Python command not found

**Try:**
```bash
python3 app.py  # Instead of python app.py
```

### Problem: SSL certificate errors

**Update certificates:**
```bash
/Applications/Python\ 3.11/Install\ Certificates.command
# (Adjust version number as needed)
```

---

## Windows Specific Issues

### Problem: Scripts not running

**Use Python explicitly:**
```bash
python app.py  # Instead of ./run.sh
```

### Problem: Path issues

**Use absolute paths in .env:**
```
OPENAI_API_KEY=sk-your-key
```

---

## Quick Diagnostics

Run these commands to diagnose issues:

```bash
# 1. Check Python version
python --version

# 2. Check dependencies
pip list | grep -E "flask|openai|pillow"

# 3. Check if .env exists
cat .env

# 4. Test API configuration
python test_api.py

# 5. Check if port is free
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# 6. Test server health
curl http://localhost:8080/api/health
```

---

## Still Having Issues?

### Get More Help

1. **Check the logs:**
   - Flask prints errors to terminal
   - Look for red error messages

2. **Check OpenAI status:**
   - Visit: https://status.openai.com

3. **Verify API credits:**
   - Visit: https://platform.openai.com/usage

4. **Review documentation:**
   - [README.md](README.md)
   - [SETUP_GUIDE.md](SETUP_GUIDE.md)

5. **Start fresh:**
   ```bash
   # Deactivate any virtual environment
   deactivate

   # Create new virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Reinstall everything
   pip install --upgrade pip
   pip install -r requirements.txt

   # Configure API key
   cp .env.example .env
   # Edit .env with your key

   # Test
   python test_api.py

   # Run
   python app.py
   ```

---

## Error Messages Reference

| Error | Meaning | Solution |
|-------|---------|----------|
| "Address already in use" | Port busy | Use port 8080 or different port |
| "No module named 'flask'" | Dependencies not installed | Run `pip install -r requirements.txt` |
| "No API key configured" | Missing .env or OPENAI_API_KEY | Create .env with valid key |
| "Rate limit exceeded" | Too many API requests | Wait 1-2 minutes |
| "Invalid API key" | Wrong or expired key | Get new key from OpenAI |
| "Insufficient credits" | No OpenAI credits | Add credits to your account |
| "Connection refused" | Server not running | Start server with `python app.py` |
| "404 Not Found" | Wrong URL | Use `http://localhost:8080` |
| "Template not found" | Missing templates folder | Run from project root directory |

---

**Most Common Solution:**
```bash
# 90% of issues are solved by:
cd /Users/ilaszajsenbaev/qylysh-higgsfiled
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python app.py
```

**Then visit:** http://localhost:8080
