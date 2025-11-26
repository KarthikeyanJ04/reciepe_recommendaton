# REQUIREMENT SPECIFICATION
## AI Recipe Recommendation & Cooking Assistant

---

## 1. PROJECT OVERVIEW

### 1.1 Project Description
An AI-powered culinary recommendation system that helps users discover recipes based on available ingredients and provides an interactive cooking assistant with voice guidance and automatic timer management. The system uses hybrid search combining TF-IDF and sentence embeddings to find relevant recipes, then enhances them using local LLM (Mistral via Ollama) to adapt recipes to user's specific ingredients.

### 1.2 Key Objectives
- Enable ingredient-based recipe search with high accuracy
- Provide AI-enhanced recipe recommendations that strictly use user's available ingredients
- Offer interactive step-by-step cooking guidance with voice narration
- Support large-scale recipe database (2M+ recipes)
- Maintain fast query response times (<500ms)
- Reduce food waste by adapting recipes to available ingredients

### 1.3 Target Users
- Home cooks looking to use available ingredients
- People wanting to reduce food waste
- Users seeking guided cooking experiences
- Anyone looking for recipe inspiration based on what they have

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Technology Stack

#### Backend
- **Framework:** Flask 3.0+
- **Language:** Python 3.10+
- **Database:** SQLite3
- **ML Libraries:**
  - scikit-learn 1.5+ (TF-IDF vectorization)
  - sentence-transformers 2.7+ (semantic embeddings)
  - PyTorch 2.0+ (deep learning backend)
  - NumPy 1.24+ (numerical computations)
  - SciPy 1.11+ (sparse matrix operations)
- **LLM Integration:** Ollama (Mistral model for recipe generation)

#### Frontend
- **Languages:** HTML5, CSS3, Vanilla JavaScript
- **APIs:** Web Speech API (text-to-speech), Web Audio API (notifications)
- **Design:** Responsive design with dark/light theme support

#### Data Processing
- **Libraries:** pandas 2.0+, openpyxl 3.1+
- **Progress Tracking:** tqdm 4.66+

### 2.2 System Components

#### Core Modules
1. **app.py** - Main Flask application with search and AI generation endpoints
2. **create_db.py** - Database creation and data ingestion pipeline
3. **build_models.py** - ML model training and chunked storage
4. **nlg_generator.py** - Natural language generation for descriptions

#### Frontend Components
1. **index.html** - Recipe search interface
2. **cooking_assistant.html** - Interactive AI cooking assistant
3. **app.js** - Frontend logic and API communication
4. **style.css** - Responsive styling with theme support

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 Recipe Search & Discovery

#### FR-1: Ingredient-Based Search
- **Description:** Users can search for recipes by entering available ingredients
- **Input:** Free-form text query (e.g., "chicken, rice, tomato")
- **Processing:** Hybrid search using TF-IDF + sentence embeddings
- **Output:** Top 10 relevant recipes from each method (up to 20 total, deduplicated)

#### FR-2: Category Filtering
- **Description:** Filter recipes by dietary category
- **Options:** All, Vegetarian, Non-Vegetarian
- **Implementation:** Automatic categorization based on ingredients and metadata

#### FR-3: Hybrid Search Algorithm
- **TF-IDF Component:**
  - HashingVectorizer with 2^18 features
  - Bigram support (1-2 word combinations)
  - Chunked processing for memory efficiency
- **Embedding Component:**
  - all-MiniLM-L6-v2 sentence transformer model
  - 384-dimensional embeddings
  - Cosine similarity matching
- **Combination:** Top 10 from each method, merged and deduplicated

### 3.2 AI Recipe Generation

#### FR-4: Database-Enhanced Recipe Generation
- **Description:** Generate adapted recipes using retrieved database recipes as context
- **Process:**
  1. Retrieve top 20 similar recipes from hybrid search
  2. Use recipes as inspiration for Mistral LLM
  3. Generate 10 new recipes adapted to user's specific ingredients
  4. Ensure strict adherence to user's ingredients (plus basic staples)
- **Output:** JSON array of recipe objects with name, description, ingredients, instructions

#### FR-5: Ingredient Adherence
- **Constraint:** Generated recipes must use ONLY user-provided ingredients plus basic staples
- **Basic Staples:** salt, pepper, oil, water, sugar
- **Philosophy:** Reduce food waste by using what's available

### 3.3 Interactive Cooking Assistant

#### FR-6: AI Avatar Guidance
- **Features:**
  - Friendly chef avatar (emoji-based)
  - Visual feedback during speech (pulsing animation)
  - Idle state animation (continuous pulse)
  - Speaking state animation (scale up)

#### FR-7: Text-to-Speech Narration
- **Technology:** Web Speech API
- **Features:**
  - Natural voice narration of each step
  - Customizable speech rate and pitch
  - Browser-based synthesis (no external API)
  - Fallback for unsupported browsers

#### FR-8: Automatic Timer Management
- **Extraction:** Regex-based detection of time values in instructions
- **Patterns:** Detects "X min", "X minutes", "X hours"
- **Conversion:** All times normalized to minutes
- **Display:** MM:SS countdown format
- **Controls:** Pause/resume capability
- **Notification:** Audio beep when timer completes

#### FR-9: Step-by-Step Navigation
- **Features:**
  - Clear step numbering
  - Progress bar showing completion percentage
  - "Next Step" button (enabled when timer finishes)
  - Automatic advancement through recipe
  - Completion celebration message

#### FR-10: Instruction Normalization
- **Processing:**
  - Split multi-step instructions into individual steps
  - Remove numbering/bullets from steps
  - Handle various instruction formats (JSON, plain text, numbered lists)
  - Ensure each step is a single actionable instruction

---

## 4. NON-FUNCTIONAL REQUIREMENTS

### 4.1 Performance

#### NFR-1: Query Response Time
- **Target:** <500ms for search queries
- **Actual:** ~200-500ms depending on database size
- **Method:** Chunked processing and indexed database queries

#### NFR-2: Model Loading Time
- **Target:** <30 seconds on startup
- **Actual:** ~15-20 seconds
- **Components:** TF-IDF vectorizer, sentence transformer, chunked embeddings

#### NFR-3: Timer Extraction Speed
- **Target:** <10ms per recipe
- **Method:** Real-time regex processing

### 4.2 Scalability

#### NFR-4: Database Capacity
- **Supported:** 2M+ recipes
- **Current Implementation:** Tested with 2.2 million recipes
- **Storage:** SQLite with indexed columns (category, search_text, cuisine)

#### NFR-5: Memory Efficiency
- **Method:** Chunked processing
- **Chunk Size:** 10,000 recipes per chunk
- **Batch Size:** 64 (GPU) or 16 (CPU) for embeddings
- **Storage:** Separate files for TF-IDF and embedding chunks

### 4.3 Accuracy

#### NFR-6: Search Relevance
- **Method:** Hybrid TF-IDF + semantic embeddings
- **Deduplication:** Removes duplicate results from combined search
- **Ranking:** Preserves score-based ordering from each method

#### NFR-7: Category Classification
- **Method:** Keyword-based detection + metadata analysis
- **Keywords:** Comprehensive list of non-vegetarian ingredients
- **Fallback:** Uses diet/veg_or_nonveg metadata when available

### 4.4 Usability

#### NFR-8: Responsive Design
- **Support:** All device sizes (desktop, tablet, mobile)
- **Method:** CSS media queries and flexible layouts
- **Theme:** Dark/light mode support

#### NFR-9: Browser Compatibility
- **Required:** Modern browsers with JavaScript enabled
- **Speech API:** Chrome, Edge, Safari (limited Firefox support)
- **Fallback:** Graceful degradation when features unavailable

#### NFR-10: User Feedback
- **Visual:** Loading states, progress indicators, animations
- **Audio:** Timer completion beep
- **Status:** Clear error messages and success confirmations

### 4.5 Reliability

#### NFR-11: Error Handling
- **Database:** Connection error handling and retry logic
- **LLM:** Timeout handling (180s), fallback messages
- **Parsing:** Robust JSON/list parsing with multiple fallback methods
- **Session:** Recipe data stored in Flask session for persistence

#### NFR-12: Data Validation
- **Input:** Query sanitization and validation
- **Output:** JSON schema validation for generated recipes
- **Instructions:** Normalization to ensure consistent format

---

## 5. DATA REQUIREMENTS

### 5.1 Database Schema

#### recipes Table
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_url TEXT,
    description TEXT,
    cuisine TEXT,
    course TEXT,
    diet TEXT,
    prep_time TEXT,
    difficulty TEXT,
    spice_level TEXT,
    meal_type TEXT,
    ingredients TEXT NOT NULL,      -- Pipe-separated list
    instructions TEXT NOT NULL,     -- Pipe-separated list
    search_text TEXT,               -- Concatenated searchable text
    category TEXT,                  -- vegetarian/non_vegetarian
    source TEXT                     -- Source dataset name
)
```

#### Indexes
- `idx_category` on category
- `idx_search` on search_text
- `idx_cuisine` on cuisine

### 5.2 Data Sources

#### Supported Formats
- CSV files (UTF-8, Latin-1 encoding)
- Excel files (.xlsx, .xls)

#### Expected Columns
- **Required:** dish/name/title, ingredients, recipe/instructions
- **Optional:** image_url, description, cuisine, course, diet, prep_time, difficulty, spice_level, meal_type, veg_or_nonveg, NER

#### Data Processing
- JSON/Python list parsing for ingredients and instructions
- Text cleaning and normalization
- Automatic category determination
- Search text generation from all fields

### 5.3 Model Storage

#### Metadata File: recipe_models.pkl
- TF-IDF vectorizer
- Recipe IDs list
- Chunk directory path
- File references

#### Chunked Files (model_chunks/)
- `tfidf_chunk_*.npz` - Sparse TF-IDF matrices
- `emb_chunk_*.npy` - Dense embedding matrices
- Chunk size: 10,000 recipes per file

---

## 6. INTERFACE REQUIREMENTS

### 6.1 API Endpoints

#### GET /
- **Description:** Main recipe search page
- **Response:** HTML template (index.html)

#### GET /cooking_assistant.html
- **Description:** Interactive cooking assistant page
- **Response:** HTML template (cooking_assistant.html)

#### POST /search
- **Description:** Search and generate recipes
- **Request Body:**
  ```json
  {
    "query": "chicken, rice, tomato"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "recipes": [
      {
        "id": "ai-0",
        "name": "Recipe Name",
        "description": "Description",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": ["step1", "step2"],
        "parsed_steps": [
          {
            "step_number": 1,
            "text": "Step text",
            "timers": [10],
            "has_timer": true
          }
        ]
      }
    ]
  }
  ```
- **Error Response:**
  ```json
  {
    "success": false,
    "error": "Error message"
  }
  ```

#### POST /cook-with-ai
- **Description:** Get specific recipe from session
- **Request Body:**
  ```json
  {
    "recipe_id": "ai-0"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "recipe": { /* recipe object */ },
    "parsed_steps": [ /* parsed steps array */ ]
  }
  ```

### 6.2 User Interface

#### Search Page (index.html)
- **Components:**
  - Search input field
  - Category filter dropdown
  - Search button
  - Results grid with recipe cards
  - "Cook with AI Assistant" button per recipe
  - Theme toggle (dark/light)

#### Cooking Assistant (cooking_assistant.html)
- **Components:**
  - AI avatar (animated emoji)
  - Recipe title and description
  - Ingredients list
  - Current step display
  - Timer display (MM:SS)
  - Pause/Resume button
  - Next Step button
  - Progress bar
  - Completion message

---

## 7. SYSTEM CONSTRAINTS

### 7.1 Technical Constraints

#### TC-1: Ollama Requirement
- **Constraint:** Ollama must be running with Mistral model
- **Command:** `ollama run mistral`
- **Port:** Default 11434
- **Timeout:** 180 seconds for generation

#### TC-2: GPU Support
- **Optional:** CUDA-compatible GPU for faster embeddings
- **Fallback:** CPU processing with reduced batch size
- **Detection:** Automatic via PyTorch

#### TC-3: Browser Requirements
- **JavaScript:** Must be enabled
- **Web Speech API:** Required for voice features
- **Local Storage:** Used for theme preference

### 7.2 Business Constraints

#### BC-1: Open Source
- **License:** MIT License
- **Dependencies:** All open-source libraries
- **LLM:** Local Ollama (no API costs)

#### BC-2: Local Deployment
- **Hosting:** Localhost (Flask development server)
- **Port:** 5000
- **Access:** http://localhost:5000

### 7.3 Data Constraints

#### DC-1: Recipe Quality
- **Minimum:** Name, ingredients, instructions required
- **Validation:** Recipes without these fields are skipped
- **Cleaning:** Automatic text normalization and parsing

#### DC-2: Ingredient Parsing
- **Formats:** JSON arrays, pipe-separated, comma-separated, newline-separated
- **Fallback:** Multiple parsing strategies attempted
- **NER Support:** Uses NER field if ingredients field missing

---

## 8. SECURITY REQUIREMENTS

### 8.1 Data Security
- **Session:** Flask secret key (random 24 bytes)
- **Database:** Local SQLite (no network exposure)
- **Input Sanitization:** Query text cleaning and validation

### 8.2 API Security
- **CORS:** Not configured (local-only access)
- **Rate Limiting:** Not implemented (local use)
- **Authentication:** Not required (local application)

---

## 9. DEPLOYMENT REQUIREMENTS

### 9.1 Installation Steps

1. **Create Virtual Environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Database:**
   ```bash
   python create_db.py
   ```

4. **Build ML Models:**
   ```bash
   python build_models.py
   ```

5. **Start Ollama:**
   ```bash
   ollama run mistral
   ```

6. **Run Application:**
   ```bash
   python app.py
   ```

7. **Access Application:**
   - Open browser to http://localhost:5000

### 9.2 System Requirements

#### Minimum
- Python 3.10+
- 8 GB RAM
- 20 GB disk space
- Dual-core CPU

#### Recommended
- Python 3.11+
- 16 GB RAM
- 50 GB SSD
- Quad-core CPU
- CUDA-compatible GPU (optional)

---

## 10. TESTING REQUIREMENTS

### 10.1 Unit Tests
- Database creation and data loading
- Text parsing and normalization
- Timer extraction from instructions
- Category determination logic

### 10.2 Integration Tests
- Hybrid search functionality
- LLM integration and response parsing
- Session management
- API endpoint responses

### 10.3 Performance Tests
- Search query response time
- Model loading time
- Memory usage during chunked processing
- Concurrent user handling

---

## 11. MAINTENANCE REQUIREMENTS

### 11.1 Model Updates
- **Frequency:** As needed when new recipes added
- **Process:** Re-run `build_models.py`
- **Downtime:** Models reload on app restart

### 11.2 Database Updates
- **Method:** Run `create_db.py` with new data files
- **Location:** Place CSV/Excel files in `data/` folder
- **Backup:** Manual backup of `recipes.db` recommended

### 11.3 Logging
- **Server Log:** `server.log`
- **Error Log:** `error.log`
- **Output Log:** `output.log`
- **Console:** Real-time debug output

---

## 12. FUTURE ENHANCEMENTS

### Planned Features
- [ ] Multi-language support for international recipes
- [ ] Recipe variations and ingredient substitutions
- [ ] Calorie and nutrition tracking
- [ ] Ingredient shopping list generation
- [ ] Real-time camera-based step verification
- [ ] Integration with smart kitchen devices
- [ ] Cloud synchronization across devices
- [ ] User accounts and saved recipes
- [ ] Social sharing features
- [ ] Recipe rating and review system

---

## 13. REFERENCES

### Documentation
- Flask: https://flask.palletsprojects.com/
- Sentence Transformers: https://www.sbert.net/
- Ollama: https://ollama.ai/
- Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

### Author
- **Name:** Karthikeyan J
- **GitHub:** [KarthikeyanJ04](https://github.com/KarthikeyanJ04)
- **Project:** Recipe Recommendation System

---

## APPENDIX A: Configuration Parameters

### Model Configuration
```python
# TF-IDF
n_features = 2**18  # 262,144 features
ngram_range = (1, 2)  # Unigrams and bigrams

# Embeddings
model_name = 'all-MiniLM-L6-v2'
embedding_dim = 384
chunk_size = 10000
batch_size_gpu = 64
batch_size_cpu = 16

# Search
top_k_tfidf = 10
top_k_embeddings = 10
max_results = 20  # After deduplication

# LLM
model = 'mistral'
temperature = 0.7
timeout = 180  # seconds
num_recipes = 10
```

### Database Configuration
```python
db_file = 'recipes.db'
batch_size = 500  # For inserts
encoding_primary = 'utf-8'
encoding_fallback = 'latin-1'
```

### Flask Configuration
```python
host = '0.0.0.0'
port = 5000
debug = False
secret_key = os.urandom(24)
```

---

*Document Version: 1.0*  
*Last Updated: 2025-11-26*  
*Status: Production*
