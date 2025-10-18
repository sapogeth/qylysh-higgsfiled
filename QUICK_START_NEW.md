# Quick Start Guide - Aldar Köse Storyboard Generator

## 🚀 Get Running in 5 Minutes

### Prerequisites Check

Before starting, ensure you have:
- ✅ macOS with M1/M2/M3 chip
- ✅ Python 3.9+ installed
- ✅ At least 15GB free disk space
- ✅ OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd qylysh-higgsfiled

# Run automated setup
python3 setup.py
```

This will install all required packages (~3GB download).

### Step 2: Configure API Key (30 seconds)

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Step 3: Setup Character (2 minutes, first time only)

```bash
python3 train_aldar_lora.py
```

This downloads the SDXL model (~7GB) and configures character consistency.

**Note**: This is a one-time setup. Subsequent runs will be much faster.

### Step 4: Start the Server (instant)

```bash
python3 app.py
```

You should see:
```
Aldar Köse Storyboard Generator
Starting web server...
Visit: http://localhost:8080
```

### Step 5: Generate Your First Storyboard

1. Open http://localhost:8080 in your browser
2. Enter a prompt like: `A greedy merchant learns about sharing`
3. Click "Generate Storyboard"
4. Wait 30-60 seconds
5. Enjoy your custom Aldar Köse story!

---

## 📝 Example Prompts to Try

**English:**
- `A village needs help during a drought`
- `Someone learns the importance of hospitality`
- `Aldar teaches children about kindness`

**Kazakh:**
- `Қонақжайлылық туралы оқиға`
- `Сараң адам бөлісуді үйренеді`
- `Ауылдағы дау-жанжалды шешу`

**Russian:**
- `Жадный человек учится щедрости`
- `История о гостеприимстве`
- `Алдар Көсе помогает бедной семье`

---

## ⚡ Performance Tips

### For Faster Generation:

Edit [config.py](config.py#L60):
```python
NUM_INFERENCE_STEPS = 25  # Default is 35
PARALLEL_BATCH_SIZE = 3   # If you have 16GB RAM
```

### For Better Quality:

```python
NUM_INFERENCE_STEPS = 45  # Higher quality, slower
GUIDANCE_SCALE = 8.5      # Stronger adherence to prompt
```

---

## 🔧 Troubleshooting

### "Model download failed"
- **Fix**: Check internet connection
- **Or**: Manually download:
  ```bash
  python3 -c "from diffusers import StableDiffusionXLPipeline; StableDiffusionXLPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0')"
  ```

### "Out of memory"
- **Fix**: Reduce batch size in [config.py](config.py#L67):
  ```python
  PARALLEL_BATCH_SIZE = 1
  ```

### "Images don't look like Aldar Köse"
- **Fix**: Ensure all 5 reference images (aldar1-5.png) are present
- **Fix**: Run `python3 train_aldar_lora.py` again
- **Fix**: Check `models/aldar_character_config.json` exists

### "Generation is too slow"
- **First run**: Model download takes 5-10 minutes (one time only)
- **Subsequent runs**: Should take 30-60 seconds
- **If still slow**: Reduce `NUM_INFERENCE_STEPS` to 20-25

---

## 📊 What to Expect

### First Run:
- ⏱️ **Setup**: 10-15 minutes (downloads ~10GB of models)
- ⏱️ **First generation**: 60-90 seconds
- 💾 **Disk usage**: ~12GB

### Subsequent Runs:
- ⏱️ **Startup**: 5-10 seconds (loads model into memory)
- ⏱️ **Generation**: 30-60 seconds per storyboard
- 💰 **Cost**: ~$0.02 per storyboard (GPT-4 only, images are free)

---

## 🎨 Output

Each storyboard includes:
- **5-9 frames** (typically 7)
- **1024x1024 images** in PNG format
- **Cultural elements**: yurts, traditional clothing, steppe landscapes
- **Consistent character**: Aldar Köse appears the same in every frame
- **Story coherence**: Beginning → middle → end with moral lesson

Images are saved in: `static/generated/`

---

## 🆘 Need Help?

1. **Check logs** in terminal for error messages
2. **Review** [README_NEW.md](README_NEW.md) for detailed documentation
3. **Run tests**:
   ```bash
   python3 test_api.py
   python3 prompt_enhancer.py
   python3 quality_validator.py
   ```

---

## 🎯 Next Steps

Once you're comfortable with basic generation:

1. **Customize prompts**: Edit [prompt_enhancer.py](prompt_enhancer.py)
2. **Adjust quality**: Modify [config.py](config.py) settings
3. **Train LoRA**: For perfect character consistency (optional, advanced)
4. **Batch generate**: Create multiple storyboards programmatically

---

## ✨ Tips for Best Results

### Writing Prompts:
- ✅ **Be specific**: "A merchant refuses to share food" → Better than "sharing"
- ✅ **Include moral**: "learns about generosity", "discovers kindness"
- ✅ **Set scene**: "in a Kazakh village", "on the steppe"
- ❌ **Avoid**: Modern elements unless intentional

### Character Consistency:
- System uses your 5 reference images (aldar1-5.png)
- Aldar will have similar appearance, clothing, and proportions
- 2D storybook style, not 3D CGI
- Warm, earthy color palette

### Quality:
- First image might take longer (model warmup)
- System auto-regenerates poor-quality images
- If unhappy with result, generate again (different seed)

---

**Happy storytelling! 🇰🇿**

For detailed documentation, see [README_NEW.md](README_NEW.md)
