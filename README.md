# Aldar Köse Storyboard Generator

Transform any idea into a visual Aldar Köse story! This web application automatically creates illustrated storyboards featuring the beloved Kazakh folk hero.

## Features

- **Automatic Aldar Köse Integration**: Any prompt you enter will be transformed into an Aldar Köse story
- **AI-Powered Storyboard**: GPT-4 creates 6-10 coherent story frames
- **Beautiful Illustrations**: DALL-E 3 generates high-quality images
- **Multi-Language Support**: Works in English, Kazakh (Қазақша), and Russian (Русский)
- **Cultural Authenticity**: Respects Kazakh traditions, settings, and values

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project
cd qylysh-higgsfiled

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your API key
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Run the Application

```bash
python app.py
```

Then visit: http://localhost:5000

## How It Works

1. **User Input**: Enter any story idea (e.g., "A merchant learns about generosity")
2. **Story Creation**: GPT-4 transforms your idea into an Aldar Köse tale
3. **Storyboard Planning**: AI generates 6-10 visual frames with descriptions
4. **Image Generation**: DALL-E 3 creates illustrations for each frame
5. **Display**: Beautiful web interface shows your complete storyboard

## Example Prompts

- "Someone learns the importance of hospitality"
- "A greedy person gets outsmarted"
- "Helping a stranger leads to unexpected rewards"
- "Тамақпен бөліспейтін адам" (Kazakh)
- "Жадный человек учится щедрости" (Russian)

## Project Structure

```
qylysh-higgsfiled/
├── app.py                      # Flask web server
├── storyboard_generator.py     # Core generation logic
├── requirements.txt            # Python dependencies
├── .env                        # API keys (create this)
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   ├── js/
│   │   └── app.js             # Frontend logic
│   └── generated/             # Generated images
└── README.md                  # This file
```

## API Endpoints

- `GET /` - Main web interface
- `POST /api/generate` - Generate storyboard from prompt
- `GET /api/health` - Health check

## Technologies

- **Backend**: Flask (Python)
- **AI Models**: GPT-4-Turbo, DALL-E 3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Image Processing**: Pillow

## Cultural Notes

**Aldar Köse** is a beloved trickster hero in Kazakh folklore, known for:
- Cleverness and wit
- Helping the poor and oppressed
- Teaching moral lessons
- Outsmarting the greedy and unjust

This application respects Kazakh culture by:
- Maintaining consistent character design (chapan, felt hat, mustache)
- Using authentic settings (steppe, yurts, bazaars)
- Incorporating traditional values (hospitality, generosity, wisdom)

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection

## Troubleshooting

**Images not generating?**
- Check your OpenAI API key in `.env`
- Ensure you have API credits available
- Placeholder images will be shown if API is unavailable

**Slow generation?**
- DALL-E 3 takes 30-60 seconds per image
- Complete storyboard (8 frames) may take 5-8 minutes
- Be patient, quality takes time!

## License

This project celebrates Kazakh folklore and culture. Use responsibly and respectfully.

## Credits

- Aldar Köse character: Traditional Kazakh folklore
- AI Generation: OpenAI GPT-4 and DALL-E 3
- Development: Built with love for Kazakh culture
