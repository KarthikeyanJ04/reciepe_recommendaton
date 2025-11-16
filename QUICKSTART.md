# 🚀 Quick Start Guide - AI Cooking Assistant

## Installation & Setup (5 minutes)

### Step 1: Install Dependencies
```bash
# Activate virtual environment
cd reciepe_recommend_local
.\.venv\Scripts\activate

# Install packages (if not already done)
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python app.py
```

You should see:
```
============================================================
AI Recipe Finder (Chunk-based)
============================================================

Loading models...
Loaded metadata for 2,236,367 recipes
Starting server on http://localhost:5000
```

### Step 3: Open Browser
Visit: **http://localhost:5000**

---

## Using the App (2 minutes)

### 1️⃣ **Search for a Recipe**
```
Search Input: "chicken" or "vegetarian pasta"
Filter: Choose "Vegetarian" or "Non-Vegetarian"
Click: "Search Recipes"
```

### 2️⃣ **Pick a Recipe**
- Scroll through results
- Read ingredients and instructions
- Find one you like

### 3️⃣ **Start Cooking with AI**
- Click: **"👨‍🍳 Cook with AI Assistant"** button
- New window opens with your personal chef

### 4️⃣ **Follow Along**
```
1. Read recipe name at top
2. Click "Start Cooking"
3. Listen to step instructions
4. Follow along manually
5. Timers start automatically
6. Click "Next Step" when ready
7. Celebrate when done! 🎉
```

---

## Features You Have

| What | How to Use |
|------|-----------|
| 🎤 **Voice Narration** | Listen to each step |
| ⏱️ **Timers** | Automatic countdown for cooking times |
| ⏸️ **Pause Timer** | Click "Pause Timer" during countdown |
| 📊 **Progress Bar** | See how far you've come |
| 🔔 **Alert Sound** | Beep when timer finishes |
| 👨‍🍳 **Avatar Feedback** | Chef animates while speaking |
| ✅ **Step Tracking** | See completed vs. current steps |
| 🎉 **Completion** | Celebration when done |

---

## Example Workflow

### You Want to Make: "Chicken Biryani"

**In the Search:**
- Search: `chicken biryani`
- Category: `All` or `Non-Vegetarian`
- Click: `Search Recipes`

**In the Recipe View:**
- See ingredients
- See instructions
- Click: `👨‍🍳 Cook with AI Assistant`

**In the Cooking Assistant:**
```
Window Opens
├─ Top: "Chicken Biryani • Indian • 45 min"
├─ Avatar: 👨‍🍳 Chef AI
├─ Says: "Let's cook Chicken Biryani. 
│          I'll guide you through 12 steps."
│
├─ You Click: "Start Cooking"
│
├─ Step 1: "Soak 2 cups basmati rice..."
│  └─ Chef reads it aloud
│
├─ Step 2: "Heat 4 tbsp ghee in a pot..."
│  └─ Chef reads it aloud
│
├─ Step 3: "Add marinated chicken..."
│  └─ Timer starts: 30 minutes!
│  └─ You see: "30:00" counting down
│  └─ You can pause or continue
│
├─ Timer finishes → BEEP! 🔔
│  └─ Chef says: "Timer finished!"
│  └─ You click: "Next Step"
│
├─ ... Continue through all steps...
│
└─ Final: 🎉 Cooking Complete!
   └─ Chef celebrates with you!
```

---

## Tips & Tricks

### 🎧 For Best Experience
- Use headphones for clearer voice
- Keep device nearby while cooking
- Have recipe visible in case you miss something
- Use pause if you need extra time

### 🔊 Voice Not Working?
- Check browser supports Web Speech API
- Enable microphone/speaker permissions
- Try different browser (Chrome works best)
- Close other apps that may block audio

### ⏱️ Timer Issues?
- Some steps might not have times
- You can manually click "Next Step"
- Timers are approximate - trust your instincts
- Pause if you need adjustment time

### 📱 On Mobile?
- Open in portrait mode for best layout
- Touch controls work same as desktop
- Voice works with mobile speakers
- Keep screen on during cooking

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Search recipes |
| `Space` | Play/Pause (when timer is running) |
| `N` | Next Step |
| `P` | Pause Timer |

---

## Troubleshooting

### 🔴 App Won't Start
```bash
# Make sure you're in the right directory
cd reciepe_recommend_local

# Activate virtual environment
.\.venv\Scripts\activate

# Try again
python app.py
```

### 🔴 Page Won't Load
```
Try: http://localhost:5000/
or:  http://127.0.0.1:5000/
```

### 🔴 Can't Find Recipes
- Try simpler search terms
- Try different ingredients
- Use single words instead of full meals

### 🔴 Timer Not Counting
- Check browser console (F12)
- Refresh the page
- Try a different recipe
- Check browser JavaScript is enabled

---

## What You Can Do Now

✅ Search through 2 million+ recipes  
✅ Get personalized recommendations  
✅ Have an AI guide you through cooking  
✅ Never miss a timer again  
✅ Enjoy cooking stress-free  
✅ Share with friends  

---

## Advanced Usage

### For Developers

**Add More Recipes:**
```bash
# Edit data/ folder with CSV/XLSX files
python create_db.py
python build_models.py
python app.py
```

**Customize Avatar:**
Edit `cooking_assistant.html` line with emoji:
```html
<div class="avatar-image" id="avatar">👨‍🍳</div>
<!-- Change to: 👩‍🍳 or 🤖 or 👨‍🔬 etc -->
```

**Adjust Speech Rate:**
Edit `cooking_assistant.html`:
```javascript
utterance.rate = 0.95;  // Change 0.95 to 0.5-1.5
```

---

## File Locations

```
project/
├── app.py           ← Main application
├── requirements.txt ← Dependencies
├── recipes.db       ← Recipe database
├── templates/
│   ├── index.html           ← Search page
│   └── cooking_assistant.html ← Chef page (NEW!)
└── static/
    ├── app.js      ← Frontend code (UPDATED)
    └── style.css   ← Styling (UPDATED)
```

---

## Next Steps

1. **Try it out** - Start the app and search for a recipe
2. **Cook with AI** - Click the button and follow along
3. **Give feedback** - Works well? Share with others!
4. **Customize** - Edit colors, sounds, avatar, etc.
5. **Expand** - Add more recipes to database

---

## Support

- **Issues?** Check the FEATURES.md file
- **Code questions?** Read the README.md
- **Feature requests?** Edit the templates/static files
- **Report bugs?** Check app.py and browser console

---

## Summary

```
3 Simple Steps:
1. python app.py
2. Open http://localhost:5000
3. Search recipe → Cook with AI → Follow steps → Enjoy! 🍽️
```

**Happy Cooking!** 👨‍🍳✨

---

*Last Updated: November 2025*  
*AI Cooking Assistant v1.0*
