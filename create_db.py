# create_db.py
"""
Complete database creation for recipe system
For local machine with data/ folder structure
"""

import sqlite3
import pandas as pd
import os
import re
import json
import ast

def create_database(db_file='recipes.db'):
    """Create SQLite database"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
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
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            search_text TEXT,
            category TEXT,
            source TEXT
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON recipes(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search ON recipes(search_text)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cuisine ON recipes(cuisine)')
    
    conn.commit()
    conn.close()
    print(f"✅ Database created\n")

def clean_text(text):
    """Clean text"""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\r\n', ' ').replace('\n', ' ')
    return text

def parse_json_list(text):
    """Parse JSON/Python list"""
    if pd.isna(text) or not text:
        return []
    
    text = str(text).strip()
    
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip().strip('"\'') for item in parsed if item]
    except:
        pass
    
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(item).strip().strip('"\'') for item in parsed if item]
    except:
        pass
    
    for sep in ['|', '\n', ',']:
        if sep in text:
            items = [item.strip().strip('"\'') for item in text.split(sep) if item.strip()]
            if items:
                return items
    
    return [text.strip()] if text.strip() else []

def parse_instructions(text):
    """Parse instructions"""
    if pd.isna(text) or not text:
        return []
    
    text = str(text).strip()
    
    parsed = parse_json_list(text)
    if parsed and len(parsed[0]) > 10:
        cleaned = []
        for step in parsed:
            step = step.strip()
            if len(step) > 5:
                step = re.sub(r'^\d+[\.\):\-\s]+', '', step)
                if not step.endswith('.'):
                    step += '.'
                cleaned.append(step)
        return cleaned
    
    steps = re.split(r'\.\s+(?=[A-Z0-9])', text)
    cleaned = []
    for step in steps:
        step = step.strip()
        if len(step) > 5:
            step = re.sub(r'^\d+[\.\):\-\s]+', '', step)
            if not step.endswith('.'):
                step += '.'
            cleaned.append(step)
    
    return cleaned

def get_value(row, *names):
    """Get value from row"""
    for name in names:
        if name in row.index and not pd.isna(row[name]):
            return row[name]
    return ""

def determine_category(ingredients, diet, veg_or_nonveg, name):
    """Determine category"""
    if veg_or_nonveg:
        v = str(veg_or_nonveg).lower()
        if 'non' in v or 'meat' in v:
            return 'non_vegetarian'
        if 'veg' in v:
            return 'vegetarian'
    
    diet_str = str(diet).lower()
    if 'non' in diet_str or 'meat' in diet_str:
        return 'non_vegetarian'
    if 'vegetarian' in diet_str:
        return 'vegetarian'
    
    text = f"{ingredients} {name}".lower()
    non_veg = ['chicken', 'mutton', 'fish', 'meat', 'egg', 'prawn', 
               'lamb', 'beef', 'pork', 'seafood', 'shrimp', 'turkey', 'bacon']
    
    return 'non_vegetarian' if any(w in text for w in non_veg) else 'vegetarian'

def process_row(row, source_name):
    """Process row"""
    name = clean_text(get_value(row, 'dish', 'name', 'title'))
    if not name or len(name) < 2:
        return None
    
    ingredients_raw = get_value(row, 'ingredients')
    ingredients_list = parse_json_list(ingredients_raw)
    
    if not ingredients_list:
        ner_raw = get_value(row, 'NER', 'ner')
        ingredients_list = parse_json_list(ner_raw)
    
    if not ingredients_list:
        return None
    
    ingredients_list = [
        re.sub(r'\s+', ' ', ing.strip().strip('"\''))
        for ing in ingredients_list if ing.strip()
    ]
    
    instructions_raw = get_value(row, 'recipe', 'instructions', 'directions')
    instructions_list = parse_instructions(instructions_raw)
    
    if not instructions_list:
        return None
    
    image_url = clean_text(get_value(row, 'image_url'))
    description = clean_text(get_value(row, 'description'))
    cuisine = clean_text(get_value(row, 'cuisine_type', 'cuisine')) or 'Indian'
    course = clean_text(get_value(row, 'course', 'meal_type'))
    diet = clean_text(get_value(row, 'diet'))
    
    prep_raw = get_value(row, 'estimated_time', 'prep_time', 'cooktime', 'cook_time')
    if prep_raw and str(prep_raw).replace('.', '').isdigit():
        prep_time = f"{prep_raw} min"
    else:
        prep_time = clean_text(prep_raw)
    
    difficulty = clean_text(get_value(row, 'difficulty'))
    spice_level = clean_text(get_value(row, 'spice_level'))
    meal_type = clean_text(get_value(row, 'meal_type'))
    veg_or_nonveg = get_value(row, 'veg_or_nonveg')
    
    category = determine_category(' '.join(ingredients_list), diet, veg_or_nonveg, name)
    
    search_parts = [name, description, cuisine, course, ' '.join(ingredients_list), ' '.join(instructions_list)]
    search_text = ' '.join([p for p in search_parts if p]).lower()
    
    return {
        'name': name,
        'image_url': image_url,
        'description': description,
        'cuisine': cuisine,
        'course': course,
        'diet': diet,
        'prep_time': prep_time,
        'difficulty': difficulty,
        'spice_level': spice_level,
        'meal_type': meal_type,
        'ingredients': '|'.join(ingredients_list),
        'instructions': '|'.join(instructions_list),
        'search_text': search_text,
        'category': category,
        'source': source_name
    }

def load_file(file_path):
    """Load file"""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.csv':
            return pd.read_csv(file_path, encoding='utf-8')
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, sheet_name=0)
    except UnicodeDecodeError:
        if ext == '.csv':
            return pd.read_csv(file_path, encoding='latin-1')
    return None

def files_to_database(files, db_file='recipes.db', clear_existing=False):
    """Convert files to database"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if clear_existing:
        cursor.execute('DELETE FROM recipes')
        conn.commit()
        print("🗑️  Cleared existing data\n")
    
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠️  Not found: {file_path}\n")
            continue
        
        print(f"📂 Processing: {os.path.basename(file_path)}")
        source_name = os.path.basename(file_path).split('.')[0]
        
        try:
            df = load_file(file_path)
            if df is None:
                continue
                
            print(f"   Rows: {len(df):,}")
            
            success = 0
            batch_size = 500
            batch_records = []
            
            for idx, row in df.iterrows():
                try:
                    record = process_row(row, source_name)
                    if record:
                        batch_records.append(record)
                        success += 1
                        
                        if len(batch_records) >= batch_size:
                            cursor.executemany('''
                                INSERT INTO recipes (name, image_url, description, cuisine, 
                                                   course, diet, prep_time, difficulty, spice_level,
                                                   meal_type, ingredients, instructions, 
                                                   search_text, category, source)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', [tuple(r.values()) for r in batch_records])
                            conn.commit()
                            batch_records = []
                except:
                    continue
            
            if batch_records:
                cursor.executemany('''
                    INSERT INTO recipes (name, image_url, description, cuisine, 
                                       course, diet, prep_time, difficulty, spice_level,
                                       meal_type, ingredients, instructions, 
                                       search_text, category, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [tuple(r.values()) for r in batch_records])
                conn.commit()
            
            print(f"   ✅ Inserted: {success:,}/{len(df):,}\n")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
    
    cursor.execute('SELECT COUNT(*) FROM recipes')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE category='vegetarian'")
    veg = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE category='non_vegetarian'")
    non_veg = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT cuisine) FROM recipes")
    cuisines = cursor.fetchone()[0]
    
    conn.close()
    
    print("=" * 60)
    print(f"📊 Final Statistics:")
    print(f"   Total: {total:,}")
    print(f"   Veg: {veg:,} ({veg/total*100:.1f}%)")
    print(f"   Non-veg: {non_veg:,} ({non_veg/total*100:.1f}%)")
    print(f"   Cuisines: {cuisines}")
    print("=" * 60)

if __name__ == "__main__":
    print("🔧 Recipe Database Creator")
    print("=" * 60 + "\n")
    
    create_database()
    
    # Files in data/ folder
    files = [
        'data/Indian_Recipes_Dataset.xlsx',
        'data/RecipeNLG_dataset.csv',
        'data/cuisines.csv'
    ]
    
    files_to_database(files, clear_existing=True)
    print("\n✅ Database ready!")
