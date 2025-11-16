# 🍳 AI Cooking Assistant - Quick Start Guide

## What's New?

Your recipe app now includes an **AI Cooking Assistant with a 3D Avatar** that:
- Provides step-by-step cooking guidance
- Automatically detects timers in recipes (e.g., "Simmer 15 minutes")
- Shows interactive countdowns with Start/Pause/Stop controls
- Auto-advances to the next step when timer completes
- Displays an animated 3D avatar that guides you through the recipe

## How to Use

### Step 1: Search for a Recipe
1. Open the app at `http://localhost:5000/`
2. Enter a recipe name (e.g., "Biryani", "Butter Chicken")
3. Browse the results

### Step 2: Start Cooking
1. Click on any recipe result
2. The **Cooking Assistant** page opens automatically
3. You'll see:
   - **Left**: 3D Avatar with encouragement messages
   - **Center**: Recipe steps with instructions
   - **Right**: Ingredients list and navigation buttons

### Step 3: Follow Steps
- Each step shows the cooking instruction
- Click any step to jump to it
- Use "Next Step" / "Previous" buttons to navigate
- Current step is highlighted in blue

### Step 4: Use Timers (NEW!)
For steps that mention time (e.g., "Simmer for 15 minutes"):

1. **Start Timer**: Click the "Start" button
   - Timer begins counting down (MM:SS format)
   - Avatar displays status
2. **Pause Timer**: Click "Pause" to temporarily stop
3. **Stop Timer**: Click "Stop" to reset
4. **Auto-Advance**: When timer hits 0:00:
   - Page shows "Done!"
   - Automatically moves to next step after 2 seconds
   - Avatar celebrates your progress

### Step 5: Complete Recipe
- Follow all steps
- Each completed step shows a green checkmark
- Progress bar shows overall completion

## Timer Examples

The assistant automatically detects timers like:
- ✓ "Preheat oven for 10 minutes"
- ✓ "Simmer for 20 mins"
- ✓ "Cook for 2 hours"
- ✓ "Rest for 5 min"
- ✓ "Bake 45 minutes"
- ✓ "Soak for 2 hours and 30 minutes"

## Avatar Features

The 3D animated avatar:
- Displays relevant cooking advice
- Shows messages like "Great! Timer finished. Move to the next step!"
- Animates smoothly with rotating head and body
- Blinks realistically (every ~10 seconds)
- Changes messages based on your progress

## Tips & Tricks

1. **Mobile Friendly**: Use on tablet while cooking (avatar hides to save space)
2. **Multi-Timer**: Each step has its own timer - manage multiple at once
3. **Quick Navigation**: Click any step number to jump directly to it
4. **Progress Tracking**: Green checkmark shows completed steps
5. **Read Ahead**: You can always look at upcoming steps

## Keyboard Shortcuts
- Click "Next Step" button or just click next step
- Use mobile gestures to scroll through steps

## Troubleshooting

**Timer not appearing?**
- The step must mention a time duration (e.g., "15 minutes")
- Currently supports minutes, hours, and seconds

**Avatar not showing?**
- This is normal on mobile/tablet (to save space)
- Desktop users should see it on the left side

**Timer won't start?**
- Click the exact "Start" button for that step
- Make sure you're clicking the right step's timer

**Page looks slow?**
- Avatar animation is GPU-intensive
- Close other browser tabs for better performance

## Video Walkthrough

No video? Here's the flow:
```
Home Page → Search Recipe → Click Result → Cooking Assistant Opens
                                ↓
                        See Steps & Avatar
                                ↓
                        Click "Start" on Timer
                                ↓
                        Watch Countdown
                                ↓
                        Timer finishes → Auto-advance
                                ↓
                        Repeat for each step
                                ↓
                        Recipe Complete!
```

## Features Coming Soon

- Voice-guided instructions
- Sound alerts when timer finishes
- Save your cooking progress
- Scale recipe (1x, 2x, etc.)
- Customize avatar appearance
- Multiple languages

## Getting Help

If something isn't working:
1. Check browser console (F12 → Console tab) for errors
2. Refresh the page (Ctrl+Shift+R)
3. Try a different recipe
4. Clear browser cache

---

**Enjoy your cooking! 🍽️**

The AI Cooking Assistant is here to make cooking easier and more fun. Whether you're a beginner or an experienced cook, let your digital cooking companion guide you through every step!
