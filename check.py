import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('models/recipes.db')

# Check table structure
print("="*80)
print("DATABASE STRUCTURE")
print("="*80)

cursor = conn.cursor()
cursor.execute("PRAGMA table_info(recipes)")
columns = cursor.fetchall()

print("\nColumns in recipes table:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Sample some recipes
print("\n" + "="*80)
print("SAMPLE RECIPES (First 3)")
print("="*80)

df_sample = pd.read_sql_query("SELECT * FROM recipes LIMIT 3", conn)

for idx, row in df_sample.iterrows():
    print(f"\n--- Recipe {idx+1}: {row['name']} ---")
    print(f"Cuisine: {row.get('cuisine', 'N/A')}")
    print(f"Course: {row.get('course', 'N/A')}")
    print(f"Diet: {row.get('diet', 'N/A')}")
    print(f"Description: {str(row.get('description', 'N/A'))[:100]}...")
    print(f"Cleaned ingredients: {str(row.get('cleaned_ingredients', 'N/A'))[:100]}...")
    print(f"Ingredients (raw): {str(row.get('ingredients', 'N/A'))[:100]}...")

# Check data quality stats
print("\n" + "="*80)
print("DATA QUALITY STATS")
print("="*80)

stats_query = """
SELECT 
    COUNT(*) as total_recipes,
    SUM(CASE WHEN cuisine IS NOT NULL AND cuisine != 'nan' AND cuisine != '' THEN 1 ELSE 0 END) as has_cuisine,
    SUM(CASE WHEN course IS NOT NULL AND course != 'nan' AND course != '' THEN 1 ELSE 0 END) as has_course,
    SUM(CASE WHEN diet IS NOT NULL AND diet != 'nan' AND diet != '' THEN 1 ELSE 0 END) as has_diet,
    SUM(CASE WHEN description IS NOT NULL AND description != 'nan' AND description != '' AND LENGTH(description) > 20 THEN 1 ELSE 0 END) as has_description
FROM recipes
"""

stats = pd.read_sql_query(stats_query, conn)
print(f"\nTotal recipes: {stats['total_recipes'].iloc[0]:,}")
print(f"Has cuisine: {stats['has_cuisine'].iloc[0]:,} ({stats['has_cuisine'].iloc[0]/stats['total_recipes'].iloc[0]*100:.1f}%)")
print(f"Has course: {stats['has_course'].iloc[0]:,} ({stats['has_course'].iloc[0]/stats['total_recipes'].iloc[0]*100:.1f}%)")
print(f"Has diet: {stats['has_diet'].iloc[0]:,} ({stats['has_diet'].iloc[0]/stats['total_recipes'].iloc[0]*100:.1f}%)")
print(f"Has description: {stats['has_description'].iloc[0]:,} ({stats['has_description'].iloc[0]/stats['total_recipes'].iloc[0]*100:.1f}%)")

conn.close()
