import sqlite3
import re
import json

print("="*80)
print("FIXING INGREDIENT SPACING IN DATABASE")
print("="*80)

conn = sqlite3.connect('models/recipes.db')
cursor = conn.cursor()

print("\nFetching all recipes...")
cursor.execute("SELECT idx, cleaned_ingredients FROM recipes")
rows = cursor.fetchall()

print(f"Found {len(rows):,} recipes")
print("\nFixing ingredient spacing...")

def clean_ingredients_properly(text):
    """Convert JSON array or comma-separated to space-separated"""
    if not text or text == 'nan':
        return ''
    
    text = str(text).lower().strip()
    
    # Try to parse as JSON array first
    if text.startswith('['):
        try:
            # Try parsing as JSON
            text_fixed = text.replace("'", '"')
            parsed = json.loads(text_fixed)
            if isinstance(parsed, list):
                # Join with spaces
                return ' '.join(str(item).strip() for item in parsed if str(item).strip())
        except:
            pass
        
        # Fallback: extract quoted strings
        matches = re.findall(r'["\']([^"\']+)["\']', text)
        if matches:
            return ' '.join(matches)
    
    # Remove brackets, quotes, commas
    text = text.strip('[]').replace('"', '').replace("'", '')
    
    # Replace commas with spaces
    text = text.replace(',', ' ')
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# Update in batches
batch_size = 5000
total_updated = 0

for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    
    updates = []
    for idx, ingredients in batch:
        cleaned = clean_ingredients_properly(ingredients)
        updates.append((cleaned, idx))
    
    cursor.executemany("UPDATE recipes SET cleaned_ingredients = ? WHERE idx = ?", updates)
    conn.commit()
    total_updated += len(updates)
    
    progress = min(i + batch_size, len(rows))
    print(f"  Processed {progress:,} / {len(rows):,} recipes...")

print(f"\n✓ Updated {total_updated:,} recipes")

# Verify
print("\nVerifying samples:")
cursor.execute("SELECT name, cleaned_ingredients FROM recipes LIMIT 5")
samples = cursor.fetchall()

for name, ingredients in samples:
    print(f"\n{name}")
    print(f"  Ingredients: {ingredients}")

conn.close()

print("\n" + "="*80)
print("✅ INGREDIENTS FIXED!")
print("="*80)
print("\nNext steps:")
print("  1. python retrain_tfidf.py")
print("  2. python retrain_embeddings_final.py")
print("  3. python app.py")
