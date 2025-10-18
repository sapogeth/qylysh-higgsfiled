# Aldar Köse Storyboard Generator - Setup Guide

## Overview

This application transforms **any user prompt** into a visual Aldar Köse storyboard automatically. Users simply enter an idea, and the system creates a complete illustrated story featuring the Kazakh folk hero.

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- OpenAI (GPT-4 & DALL-E 3)
- Pillow (image processing)
- python-dotenv (environment variables)
- requests (HTTP client)

### 2. Configure OpenAI API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-...your_key_here...
```

**Get your API key:**
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it to your `.env` file

### 3. Test the Setup (Optional but Recommended)

```bash
python test_api.py
```

This will:
- Verify your API key is configured
- Test the story generation
- Test the frame generation
- Show you a sample output

### 4. Run the Application

**Option A: Using the run script**
```bash
./run.sh
```

**Option B: Direct Python**
```bash
python app.py
```

### 5. Open in Browser

Visit: **http://localhost:5000**

## How to Use

### Step 1: Enter a Prompt
Type any story idea in the input box. Examples:

**English:**
- "A merchant refuses to help travelers"
- "Someone learns the value of honesty"
- "Greed leads to unexpected consequences"

**Kazakh (Қазақша):**
- "Тамақпен бөліспейтін адам"
- "Ашкөз бей мал тонауды ойлайды"
- "Кедейге көмектесу"

**Russian (Русский):**
- "Жадный торговец и путники"
- "Урок щедрости"
- "Помощь незнакомцу"

### Step 2: Generate
Click "Generate Storyboard" and wait 5-8 minutes.

The system will:
1. Transform your prompt into an Aldar Köse story (15 seconds)
2. Create 6-10 storyboard frames (30 seconds)
3. Generate images with DALL-E 3 (5-7 minutes)

### Step 3: View & Download
- See your complete illustrated storyboard
- Each frame shows:
  - Beautiful AI-generated image
  - Rhyming caption
  - Description
  - Moral lesson
  - Shot type
  - Setting and objects
- Download all images with one click

## How It Works

```
User Prompt: "A greedy person learns generosity"
         ↓
┌─────────────────────────────────────────┐
│  GPT-4: Transform into Aldar Köse story │
│  Output: "Алдар Көсе жәрмеңкеде..."    │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  GPT-4-Turbo: Generate storyboard       │
│  Output: 6-10 frames with descriptions  │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  DALL-E 3: Generate images              │
│  Output: High-quality illustrations     │
└─────────────────────────────────────────┘
         ↓
   Beautiful Web Display
```

## Key Features

### 1. Automatic Aldar Köse Integration
**Any prompt automatically becomes an Aldar Köse story.**

Input: "Someone finds a lost child"
→ Output: "Алдар Көсе helps a mother find her lost child in the marketplace..."

### 2. Cultural Authenticity
- Traditional Kazakh clothing (chapan, kalpak)
- Authentic settings (steppe, yurts, bazaars)
- Moral lessons (kindness, wisdom, hospitality)
- Respectful character design

### 3. Visual Consistency
- Aldar Köse appears the same in every frame
- Consistent lighting across scenes
- Professional storyboard structure
- Varied camera shots (wide, close-up, etc.)

### 4. Multi-Language Support
The system detects your language and responds accordingly:
- English → English storyboard
- Қазақша → Қазақ тіліндегі сценарий
- Русский → Сценарий на русском

## Troubleshooting

### Problem: "No API key configured"
**Solution:**
1. Create `.env` file: `cp .env.example .env`
2. Add your key: `OPENAI_API_KEY=sk-...`
3. Restart: `python app.py`

### Problem: "Generation taking too long"
**Reason:** DALL-E 3 is slow but high-quality
- 1 image = ~40 seconds
- 8 images = ~5-6 minutes
- This is normal!

**Tip:** Start with shorter prompts to test faster

### Problem: "API rate limit error"
**Solution:**
- Your OpenAI account has limits
- Wait a few minutes and try again
- Check your usage at: https://platform.openai.com/usage

### Problem: Images not displaying
**Check:**
1. `static/generated/` folder exists
2. Flask has write permissions
3. Browser console for errors (F12)

### Problem: Placeholder images showing
**Reason:** API key not working or API down
- Check your API key is correct
- Verify you have API credits
- Test with: `python test_api.py`

## Project Structure

```
qylysh-higgsfiled/
│
├── app.py                      # Flask web server
│   ├── Routes: /, /api/generate, /api/health
│   └── Serves HTML and handles API calls
│
├── storyboard_generator.py     # Core AI logic
│   ├── StoryboardGenerator class
│   ├── _create_aldar_story()   → GPT-4 story creation
│   ├── _generate_frames()      → GPT-4 storyboard planning
│   └── _generate_images()      → DALL-E 3 image generation
│
├── templates/
│   └── index.html              # Web interface
│       ├── Input section (prompt entry)
│       └── Output section (storyboard display)
│
├── static/
│   ├── css/style.css           # Beautiful styling
│   ├── js/app.js               # Frontend logic
│   └── generated/              # Generated images saved here
│
├── .env                        # Your API key (create this!)
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

## API Reference

### POST /api/generate
Generate storyboard from prompt

**Request:**
```json
{
  "prompt": "A merchant learns generosity"
}
```

**Response:**
```json
{
  "success": true,
  "storyboard": [
    {
      "frame_number": 1,
      "rhyme": "Aldar Köse arrives at the market square",
      "moral": "wisdom",
      "shot_type": "establishing",
      "setting": "Kazakh marketplace at noon",
      "key_objects": ["Aldar Köse", "marketplace", "merchants"],
      "lighting_hint": "sunlight from the left, warm daylight",
      "description": "Aldar Köse walks into a bustling bazaar...",
      "image_url": "/static/generated/frame_001_20251018_143022.png"
    }
  ],
  "metadata": {
    "original_prompt": "A merchant learns generosity",
    "aldar_story": "Алдар Көсе жәрмеңкеде...",
    "num_frames": 8,
    "generated_at": "2025-10-18T14:30:22.123456"
  }
}
```

### GET /api/health
Health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T14:30:22.123456"
}
```

## Performance Tips

### Faster Generation
1. **Use shorter prompts** (1-2 sentences)
2. **Request fewer frames** (modify default in code)
3. **Use DALL-E 2** instead of DALL-E 3 (lower quality)

### Better Quality
1. **Detailed prompts** work better
2. **Specific morals** (kindness, wisdom, etc.)
3. **Clear settings** (marketplace, steppe, yurt)

### Cost Optimization
- GPT-4-Turbo: ~$0.01 per storyboard
- DALL-E 3: ~$0.04 per image
- **Total:** ~$0.35 per 8-frame storyboard

**Tip:** Use template fallbacks for testing (no API key)

## Examples

### Example 1: English Prompt
**Input:**
```
A greedy bay refuses to share his vast herds
```

**Output:**
- 8-frame storyboard
- Aldar Köse teaches the bay about generosity
- Traditional Kazakh steppe setting
- Moral lesson about sharing

### Example 2: Kazakh Prompt
**Input:**
```
Алдар Көсе базарда ашкөз саудагерді ұялтады
```

**Output:**
- Storyboard entirely in Kazakh
- Marketplace setting with yurts
- Aldar Köse outsmarts greedy merchant
- Cultural authenticity maintained

### Example 3: Russian Prompt
**Input:**
```
Старик помогает путникам, и получает награду
```

**Output:**
- Russian language storyboard
- Story adapted to Aldar Köse character
- Traditional Kazakh hospitality theme
- Beautiful illustrations

## Advanced Configuration

### Change Number of Frames
Edit `storyboard_generator.py`:
```python
# In _generate_frames() fallback, change return array length
# Or modify GPT prompt to request specific number
```

### Change Image Size
Edit `storyboard_generator.py`:
```python
# In _generate_single_image()
size="1024x1024"  # Change to "1792x1024" for landscape
```

### Change Model
Edit `storyboard_generator.py`:
```python
# For story generation
model="gpt-4"  # Change to "gpt-3.5-turbo" for speed

# For image generation
model="dall-e-3"  # Change to "dall-e-2" for cost savings
```

## Deployment

### Local Development
```bash
python app.py
# Runs on http://localhost:5000
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Support

### Common Issues
- Slow generation → Normal for DALL-E 3
- Placeholder images → Check API key
- Rate limits → Wait and retry
- Memory errors → Reduce concurrent requests

### Resources
- OpenAI Documentation: https://platform.openai.com/docs
- Flask Documentation: https://flask.palletsprojects.com
- Project Issues: Check README.md

## Credits

- **Aldar Köse**: Traditional Kazakh folklore character
- **AI Models**: OpenAI GPT-4 & DALL-E 3
- **Framework**: Flask (Python web framework)
- **Design**: Custom responsive CSS

Built with respect for Kazakh culture and traditions.

---

**Ready to start?**
```bash
./run.sh
```

Visit http://localhost:5000 and create your first Aldar Köse storyboard!
