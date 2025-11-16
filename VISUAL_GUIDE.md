# 🍳 AI Cooking Assistant - Visual Guide

## The Three Panels Layout

```
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃   AVATAR    ┃      RECIPE STEPS & TIMERS       ┃ INGREDIENTS ┃
┃   PANEL     ┃                                  ┃   & INFO    ┃
┃             ┃  ╔════════════════════════════╗  ┃             ┃
┃   [3D 👨]   ┃  ║ 1 Preheat oven             ║  ┃ RECIPE INFO ┃
┃             ┃  ╠════════════════════════════╣  ┃ • Prep: 30m ┃
┃   Smiling & ┃  ║ 2 Mix ingredients          ║  ┃ • Type: Veg ┃
┃   Waving    ┃  ╠════════════════════════════╣  ┃             ┃
┃             ┃  ║✓ 3 Let it rest for 15 min  ║  ┃ INGREDIENTS ┃
┃   "Keep up  ┃  ║   [Start] [Pause] [Stop]   ║  ┃ ✓ Flour     ┃
┃    the great║  ║   ⏱ 15:00                  ║  ┃ ✓ Sugar     ┃
┃    work!"   ┃  ╠════════════════════════════╣  ┃ ✓ Eggs      ┃
┃             ┃  ║ 4 Bake for 30 minutes      ║  ┃ ✓ Butter    ┃
┃             ┃  ║   [Start] [Pause] [Stop]   ║  ┃ ✓ Vanilla   ┃
┃             ┃  ║   ⏱ 30:00                  ║  ┃             ┃
┃             ┃  ╠════════════════════════════╣  ┃ NAVIGATION  ┃
┃             ┃  ║ 5 Cool and serve           ║  ┃ [Next Step] ┃
┃             ┃  ╚════════════════════════════╝  ┃ [Previous]  ┃
┗━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━┛
```

## Step-by-Step User Flow

### 1️⃣ HOME PAGE - Search for Recipe
```
┌──────────────────────────────────────┐
│     AI RECIPE FINDER                 │
│                                      │
│  [Search Box] "Biryani"              │
│                                      │
│  Search Results:                     │
│  • Hyderabadi Biryani                │
│  • Kolkata Biryani                   │
│  • Lucknowi Biryani                  │
│                                      │
│  ► Click any result                  │
└──────────────────────────────────────┘
```

### 2️⃣ COOKING ASSISTANT OPENS
```
Avatar Panel          Steps Panel              Info Panel
┌─────────────┐      ┌──────────────────┐    ┌──────────┐
│   [3D 👨]   │      │ LET'S COOK!      │    │ PREP: 1H │
│             │      │                  │    │ TYPE: VEG│
│  "Let's     │      │ 1 ▪ Soak rice   │    │          │
│   cook!"    │      │ 2 ▪ Heat oil     │    │ INGREDS: │
│             │      │ 3 ✓ Boil water  │    │ • Rice   │
│             │      │ 4 ▪ Mix masala  │    │ • Oil    │
│             │      │ 5 ▪ Layer rice  │    │ • Salt   │
│             │      │                  │    │          │
└─────────────┘      └──────────────────┘    │ [Next]   │
                                             │ [Prev]   │
                                             └──────────┘
```

### 3️⃣ WORKING ON A STEP WITH TIMER
```
Avatar                Steps                    Info
┌─────────────┐      ┌──────────────────┐    ┌──────────┐
│   [3D 👨]   │      │ LET'S COOK!      │    │ PREP: 1H │
│             │      │                  │    │ TYPE: VEG│
│  "Almost    │      │ 3 ▪ Boil water   │    │          │
│   done!     │      │    for 20 mins   │    │ INGREDS: │
│   Keep      │      │    [Start] ⏸️ ⏹️  │    │ • Rice   │
│   going!"   │      │    ⏱️ 20:00       │    │ • Oil    │
│             │      │ 4 ✓ Mix masala  │    │ • Salt   │
│             │      │ 5 ▪ Layer rice  │    │          │
│             │      │                  │    │ [Next]   │
└─────────────┘      └──────────────────┘    │ [Prev]   │
                                             └──────────┘
```

### 4️⃣ TIMER RUNNING
```
Avatar                Steps                    Info
┌─────────────┐      ┌──────────────────┐    ┌──────────┐
│   [3D 👨]   │      │ LET'S COOK!      │    │ PREP: 1H │
│   Blink     │      │                  │    │ TYPE: VEG│
│   Blink     │      │ 3 ▪ Boil water   │    │          │
│             │      │    for 20 mins   │    │ INGREDS: │
│  "Waiting   │      │    [Start] ⏸️ ⏹️  │    │ • Rice   │
│   for      │      │    ⏱️ 18:45  🔴  │    │ • Oil    │
│   timer!"   │      │    (pulsing)     │    │ • Salt   │
│             │      │ 4 ✓ Mix masala  │    │          │
│             │      │ 5 ▪ Layer rice  │    │ [Next]   │
└─────────────┘      └──────────────────┘    │ [Prev]   │
                                             └──────────┘
```

### 5️⃣ TIMER COMPLETE - AUTO ADVANCE
```
Avatar                Steps                    Info
┌─────────────┐      ┌──────────────────┐    ┌──────────┐
│   [3D 👨]   │      │ LET'S COOK!      │    │ PREP: 1H │
│   Happy!    │      │                  │    │ TYPE: VEG│
│   💚 💚     │      │ 3 ✓ Boil water  │    │          │
│             │      │ 4 ▪ Mix masala  │    │ INGREDS: │
│  "Perfect!  │      │    for 5 mins   │    │ • Rice   │
│   Done!     │      │    [Start] ⏸️ ⏹️  │    │ • Oil    │
│   Moving    │      │    ⏱️ 5:00       │    │ • Salt   │
│   to next!" │      │ 5 ▪ Layer rice  │    │          │
│             │      │                  │    │ [Next]   │
└─────────────┘      └──────────────────┘    │ [Prev]   │
                                             └──────────┘
```

## Timer Button Actions

```
                    [Start]
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
     Countdown Active      No Change
      (0:00 to N:MM)      (No Timer)
           │
    [Pause] │ [Stop]
      ▼     │      ▼
    Paused  │    Reset
      │     │      ▲
      └─────┴──────┘
      [Resume/Start]
```

## Progress Tracking

```
Step 1:  ░░░░░░░░░░░░░░░░░░░░ 100% (Completed)
         ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓

Step 2:  ░░░░░░░░░░░░░░░░░░░░ 100% (Completed)
         ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓

Step 3:  ████████████░░░░░░░░  60% (In Progress)
         ✓ ✓ ✓ ✓ ✓ ✓ ► ░ ░ ░

Step 4:  ░░░░░░░░░░░░░░░░░░░░   0% (Not Started)
         ░ ░ ░ ░ ░ ░ ░ ░ ░ ░

Step 5:  ░░░░░░░░░░░░░░░░░░░░   0% (Not Started)
         ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
```

## Timer Format Display

```
Minutes Format:
20 minutes → "20:00" → "19:59" → ... → "0:00" → "Done!"

Hours Format:
2 hours → "120:00" → "119:59" → ... → "0:00" → "Done!"

Mixed Format:
1 hour 30 mins → "90:00" → "89:59" → ... → "0:00" → "Done!"
```

## Mobile View (Tablet/Phone)

```
┌────────────────────────────┐
│  AI COOKING ASSISTANT      │
├────────────────────────────┤
│   LET'S COOK!              │
│                            │
│ 1 ▪ Soak rice             │
│ 2 ▪ Heat oil              │
│ 3 ▪ Boil water for 20min  │
│    [Start] ⏸️ ⏹️           │
│    ⏱️ 20:00               │
│ 4 ▪ Mix masala            │
│ 5 ▪ Layer rice            │
├────────────────────────────┤
│       RECIPE INFO          │
│ • Prep: 1 hour            │
│ • Type: Vegetarian        │
│                            │
│ Ingredients:              │
│ ✓ Rice                    │
│ ✓ Oil                     │
│ ✓ Salt                    │
│                            │
│ [Next Step]  [Previous]    │
└────────────────────────────┘
```

## Color States

```
┌─────────────────────────────────────────┐
│ STEP COLOR CODING                       │
├─────────────────────────────────────────┤
│                                         │
│ ░ Inactive Step                         │
│   Gray background, 50% opacity          │
│   ↓ Click to navigate                   │
│                                         │
│ ■ Current Step (ACTIVE)                 │
│   Light purple background, highlight    │
│   ↓ This is what you're doing now       │
│                                         │
│ ✓ Completed Step (DONE)                 │
│   Green checkmark, normal opacity       │
│   ↓ You've already finished this        │
│                                         │
│ ⏱️ Step with Timer                       │
│    Orange badge showing duration        │
│    [Start] [Pause] [Stop] buttons       │
│                                         │
│ 🔴 Active Timer (RUNNING)               │
│    Pulsing animation                    │
│    Countdown visible                    │
│                                         │
└─────────────────────────────────────────┘
```

## Message Examples

```
Avatar Messages Based on Progress:

🎬 Start: "Let's cook something delicious today!"
👨: "You're doing amazing! 🌟"
👨: "Keep up the great work! 👨‍🍳"
👨: "Follow the steps carefully! 📝"

⏱️ Timer Running: "Waiting for timer..."
⏱️ Timer Done: "Great! Timer finished. Move to the next step! ⏰"

✅ All Done: "Congratulations! You've completed the recipe!"
```

## Keyboard & Touch Shortcuts

```
Desktop:
- Click step number → Jump to that step
- Click "Next Step" → Move forward
- Click "Previous" → Move backward
- Click "Start" → Begin timer

Mobile/Tablet:
- Tap step number → Jump to that step
- Tap "Next Step" → Move forward
- Tap "Previous" → Move backward
- Tap "Start" → Begin timer
- Swipe → Scroll through ingredients
```

## Complete Flow Summary

```
START
  │
  ├─→ Search Recipe
  │
  ├─→ Click Result
  │
  ├─→ Cooking Assistant Opens
  │     • Avatar initializes
  │     • Steps load
  │     • Current step highlighted
  │
  ├─→ Read Step Instructions
  │
  ├─→ If Timer Needed:
  │     ├─→ Click "Start"
  │     ├─→ Watch Countdown
  │     ├─→ Avatar watches too
  │     └─→ Auto-advance when done
  │
  ├─→ Complete Step
  │     └─→ Mark as Done ✓
  │
  ├─→ Click "Next Step"
  │
  ├─→ Repeat for all steps
  │
  └─→ END - Recipe Complete!
```

---

**Enjoy cooking with your AI assistant! 🎉**
