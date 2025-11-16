# AI Recipe Recommendation & Cooking Assistant

A sophisticated culinary recommendation system with an interactive AI cooking assistant that guides you through recipes with voice guidance and automatic timers.

## Features

### 🔍 Smart Recipe Search
- Search recipes by ingredients
- Filter by category (Vegetarian, Non-Vegetarian)
- Hybrid search using TF-IDF and sentence embeddings
- Dark/Light theme support
- Responsive design for all devices

### 👨‍🍳 AI Cooking Assistant
The interactive cooking assistant features:

- **Avatar-Based Guidance**: A friendly chef avatar that communicates with you
- **Text-to-Speech**: Natural voice narration of recipe steps
- **Animated Avatar**: Visual feedback when the assistant speaks
- **Step-by-Step Navigation**: Clear progression through recipe steps
- **Automatic Timer Management**: Extracts and manages timers from recipe instructions
- **Pause/Resume Capability**: Control timers while cooking
- **Audio Notifications**: Beeping sound when timer completes
- **Progress Tracking**: Visual progress bar showing cooking completion
- **Completion Celebration**: Special message when recipe is done

## Installation

### Requirements
- Python 3.10+
- Flask 3.0+
- scikit-learn 1.5+
- sentence-transformers 2.7+
- PyTorch 2.0+
- NumPy 1.24+
- SciPy 1.11+

### Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python create_db.py
```

4. Build the ML models:
```bash
python build_models.py
```

5. Run the application:
```bash
python app.py
```

6. Open browser to `http://localhost:5000`

## Usage

### Finding Recipes
1. Enter ingredients in the search box (e.g., "chicken, rice, tomato")
2. Filter by category if desired
3. Browse results with detailed ingredients and instructions
4. Click "Cook with AI Assistant" to start cooking

### Using the AI Assistant
1. **Start**: Click "Start Cooking" to begin
2. **Listen**: The AI reads each step aloud with avatar animation
3. **Timer**: Automatic timers start for cooking time requirements
4. **Control**: Pause/resume timers as needed
5. **Progress**: Next Step button advances when timer finishes
6. **Complete**: Celebration message when recipe is done

## API Endpoints

### `/` (GET)
Main recipe search page

### `/cooking-assistant` (GET)
Interactive cooking assistant page
- Parameter: `recipe_id` - ID of the recipe to cook

### `/search` (POST)
Search for recipes
```json
{
  "query": "chicken",
  "category": "all|vegetarian|non-vegetarian"
}
```

### `/cook-with-ai` (POST)
Get parsed recipe with timers
```json
{
  "recipe_id": 1
}
```

## Project Structure

```
.
├── app.py                  # Main Flask application
├── build_models.py        # TF-IDF and embedding model builder
├── create_db.py           # Database creation and data loading
├── nlg_generator.py       # Natural Language Generation for descriptions
├── requirements.txt       # Python dependencies
├── recipes.db             # SQLite database
├── recipe_models.pkl      # Pickled ML models
├── model_chunks/          # Chunked embeddings and TF-IDF matrices
├── templates/
│   ├── index.html         # Main search page
│   └── cooking_assistant.html  # AI cooking assistant
└── static/
    ├── app.js             # Frontend JavaScript
    └── style.css          # Styling
```

## How the AI Assistant Works

### Step Processing
1. Extracts instructions from recipe database
2. Normalizes and cleans instruction text
3. Identifies timing information (minutes, hours)
4. Creates a guided step-by-step experience

### Text-to-Speech
- Uses Web Speech API for browser-based voice synthesis
- Customizable speech rate and pitch
- Fallback for unsupported browsers

### Timer Management
- Extracts numeric time values from instructions
- Converts all times to minutes for consistency
- Displays countdown in MM:SS format
- Plays notification sound when complete

### AI Avatar Animation
- Pulses continuously as idle state
- Scales up when speaking
- Visual feedback enhances interaction
- Emoji-based friendly appearance

## Technologies Used

- **Backend**: Flask (Python web framework)
- **ML Models**: scikit-learn (TF-IDF), Sentence Transformers (embeddings)
- **Database**: SQLite
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Speech**: Web Speech API
- **Audio**: Web Audio API

## Configuration

### Model Parameters
- **TF-IDF**: HashingVectorizer with 2^18 features, bigrams
- **Embeddings**: all-MiniLM-L6-v2 model
- **Chunk Size**: 10,000 recipes per chunk
- **Batch Size**: 64 (GPU) or 16 (CPU)

### Database
- **Engine**: SQLite3
- **Tables**: recipes (with indices on category, search text, cuisine)
- **Capacity**: Supports 2M+ recipes

## Performance Notes

- Large models load during startup (~15-20 seconds)
- Search queries run in ~200-500ms depending on index size
- Timer extraction is real-time (< 10ms)
- Chunked processing enables efficient memory usage

## Troubleshooting

### Models Not Loading
- Ensure `recipe_models.pkl` exists
- Verify all chunks are in `model_chunks/` directory
- Check Python version compatibility

### Timer Not Showing
- Browser must have JavaScript enabled
- Web Speech API may not work in all browsers
- Check browser console for errors

### Voice Not Working
- Verify Web Speech API support
- Check system audio settings
- Some browsers require HTTPS

## Future Enhancements

- [ ] Multi-language support
- [ ] Recipe variations and substitutions
- [ ] Calorie and nutrition tracking
- [ ] Ingredient shopping list generation
- [ ] Real-time camera-based step verification
- [ ] Integration with smart kitchen devices
- [ ] Cloud synchronization across devices

## License

MIT License - Feel free to use and modify

## Author

Karthikeyan J
GitHub: [KarthikeyanJ04](https://github.com/KarthikeyanJ04)
