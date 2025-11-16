# AI Cooking Assistant with 3D Avatar - Feature Documentation

## Overview
The AI Cooking Assistant is an interactive, step-by-step recipe guide with a 3D animated avatar that helps users follow recipes and manage cooking timers.

## Features

### 1. **3D Animated Avatar**
- Built with Three.js library
- Realistic 3D character with:
  - Spherical head with skin texture
  - Animated eyes with blinking effect
  - Stylized body with capsule geometry
  - Professional lighting setup
  - Smooth rotation animations
- Displays encouraging messages as you progress through recipes

### 2. **Smart Timer Detection & Management**
The backend automatically extracts time information from recipe instructions using regex patterns:
- Detects: "15 minutes", "2 hours", "30 secs", etc.
- Converts all times to minutes for consistency
- Supports multiple timer formats (min/mins, hour/hrs, sec/secs)

Each step with a detected timer includes:
- **Start Button**: Begin countdown
- **Pause Button**: Temporarily pause the timer
- **Stop Button**: Cancel and reset timer
- **Visual Display**: MM:SS format with pulsing animation
- **Auto-Advance**: Automatically moves to next step when timer completes

### 3. **Interactive Step Navigation**
- Visual step-by-step display
- Current step highlighted with blue background
- Completed steps marked with green checkmark
- Click any step to jump directly to it
- Next/Previous buttons for sequential navigation
- Progress bar showing completion percentage

### 4. **Responsive Layout**
Three-column design:
- **Left Panel**: 3D Avatar with messaging
- **Center Panel**: Recipe steps and instructions
- **Right Panel**: Recipe info, ingredients list, navigation buttons

On mobile/tablet, avatar panel hides to save space.

### 5. **Recipe Integration**
- Displays full recipe details
- Lists all ingredients with checkmarks
- Shows prep time and category
- Links from main search to cooking assistant

## Technical Implementation

### Backend (/cook-with-ai Endpoint)
```python
@app.route('/cook-with-ai', methods=['POST'])
def cook_with_ai():
    # Extracts recipe details
    # Parses instructions for timer patterns
    # Returns structured step data with timers
```

### Timer Extraction Algorithm
```python
time_patterns = [
    r'(\d+)\s*(?:minutes?|mins?)',      # Matches: 15 minutes, 5 mins
    r'(\d+)\s*(?:hours?|hrs?)',         # Matches: 2 hours, 1 hr
    r'(\d+)\s*(?:seconds?|secs?)'       # Matches: 30 seconds, 45 secs
]
```

### Data Structure (parsed_steps)
```json
{
    "step_number": 1,
    "text": "Preheat oven to 350F for 15 minutes",
    "timers": [15],
    "has_timer": true
}
```

### Frontend Components
- **Canvas Element**: Renders 3D avatar
- **Message Box**: Displays avatar messages and hints
- **Step Container**: Shows all cooking steps
- **Timer Controls**: Start/Pause/Stop buttons per step
- **Progress Indicator**: Visual progress bar

## User Workflow

1. **Search for Recipe**
   - User searches for a recipe on the main page
   - Clicks on desired recipe result

2. **Enter Cooking Assistant**
   - Recipe ID passed via URL parameter: `?recipe_id=123`
   - Page loads recipe details and parses instructions

3. **Follow Steps**
   - Read current step in center panel
   - Avatar provides encouraging messages
   - View ingredients on right panel

4. **Manage Timers**
   - If step contains time (e.g., "Simmer 15 minutes"):
     - Timer badge appears below step
     - Click "Start" to begin countdown
     - Timer updates every second in MM:SS format
     - "Done!" message shows when complete
     - Auto-advances to next step

5. **Complete Recipe**
   - All steps marked as completed
   - Avatar displays completion message

## Styling Features

- **Color Scheme**: Purple gradient background (#667eea to #764ba2)
- **Step States**:
  - Inactive: 50% opacity, gray background
  - Current: 100% opacity, light purple background, highlighted border
  - Completed: Green checkmark indicator
- **Animations**:
  - Smooth transitions on step selection
  - Pulsing effect on active timer
  - Avatar rotating with blinking eyes
- **Typography**: Clean, readable sans-serif font (Segoe UI)
- **Spacing**: Proper padding and gaps for mobile-friendly design

## Browser Compatibility

- Chrome/Edge: ✅ Full support (Three.js WebGL)
- Firefox: ✅ Full support
- Safari: ✅ Full support (requires WebGL enabled)
- Mobile Browsers: ✅ Responsive design (avatar hidden on small screens)

## Performance Considerations

- Three.js avatar rendered at canvas resolution
- Timers use native JavaScript intervals (1 second precision)
- Minimal DOM updates for timer display
- CSS animations use GPU acceleration
- Efficient event delegation for step selection

## Future Enhancements

Possible improvements:
- Voice guidance using Web Speech API
- Audio notification when timer completes
- Saving cooking progress
- Adjustable avatar appearance
- Multi-language support
- Integration with smart home devices
- Recipe scaling (1x, 2x, etc.)
- Nutritional information display

## File Locations

- Frontend: `templates/cooking_assistant_3d.html`
- Backend: `app.py` (routes: `/cooking-assistant`, `/cook-with-ai`)
- Dependencies: Three.js (CDN), Flask, Python regex

## Testing the Feature

1. Start the app: `python app.py`
2. Navigate to: `http://localhost:5000/`
3. Search for any recipe
4. Click on result to open cooking assistant
5. Click "Start" on any step with a timer
6. Watch the countdown and auto-advance!
