# Quick Start - 3 Steps to Your First Storyboard

## Step 1: Install (1 minute)

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Key (1 minute)

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get key from: https://platform.openai.com/api-keys
```

Your `.env` should look like:
```
OPENAI_API_KEY=sk-proj-abc123...your_real_key_here
```

## Step 3: Run (10 seconds)

```bash
python app.py
```

Then visit: **http://localhost:5000**

---

## Your First Storyboard

1. **Type a prompt** in the input box:
   - "A greedy merchant learns about sharing"

2. **Click "Generate Storyboard"**

3. **Wait 5-7 minutes** (AI is working!)

4. **Enjoy your Aldar Köse storyboard!**

---

## What Happens Automatically

**ANY prompt you enter becomes an Aldar Köse story!**

| You Enter | System Creates |
|-----------|----------------|
| "Someone learns to be kind" | "Aldar Köse teaches a lesson about kindness..." |
| "Finding lost treasure" | "Алдар Көсе табылған байлықты бөліседі..." |
| "Помощь старику" | "Алдар Кёсе помогает старику и получает..." |

The system automatically:
- ✅ Adds Aldar Köse as the main character
- ✅ Creates a proper story structure (beginning → middle → end)
- ✅ Adds Kazakh cultural elements (yurts, steppe, chapan)
- ✅ Generates 6-10 illustrated frames
- ✅ Maintains character consistency
- ✅ Includes moral lessons

---

## Troubleshooting

**Can't run the app?**
```bash
# Make sure you're in the right folder
cd qylysh-higgsfiled

# Check Python version (need 3.8+)
python --version

# Install dependencies again
pip install -r requirements.txt
```

**Getting "No API key" error?**
1. Check `.env` file exists: `ls -la .env`
2. Check it has your key: `cat .env`
3. Make sure key starts with `sk-`
4. Restart the app: `python app.py`

**Images not generating?**
- Check you have OpenAI API credits
- Visit: https://platform.openai.com/usage
- Placeholder images will show if API unavailable

---

## That's It!

You're ready to create unlimited Aldar Köse storyboards!

For more details, see:
- [README.md](README.md) - Full documentation
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup guide
- Run `python test_api.py` to test your configuration
