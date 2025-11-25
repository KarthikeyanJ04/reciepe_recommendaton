import sqlite3

conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Search for Biryani
cursor.execute("SELECT name, ingredients FROM recipes WHERE name LIKE '%biryani%' LIMIT 10")
results = cursor.fetchall()

print(f"Found {len(results)} Biryani recipes:")
for name, ingredients in results:
    print(f"\n{name}")
    print(f"Ingredients: {ingredients[:150]}...")

conn.close()
