import sqlite3

print("Exporting ALL recipes to train.txt...")

conn = sqlite3.connect('models/recipes.db')
cursor = conn.execute("""
    SELECT name, cleaned_ingredients, ingredients_raw, instructions, cuisine, diet
    FROM recipes
""")

with open('train.txt', 'w', encoding='utf-8') as f:
    count = 0
    for row in cursor.fetchall():
        name, ingredients, ingredients_raw, instructions, cuisine, diet = row

        # Skip if missing minimal requirements
        if not ingredients or not instructions or not name:
            continue

        # Format ingredients (prefer cleaned)
        ing_str = str(ingredients)
        ing_str = ing_str.replace('[', '').replace(']', '').replace('"', '').replace("'", '').replace(',', '\n')

        recipe_block = f"""<|startoftext|>
Recipe: {name}
Cuisine: {cuisine}
Diet: {diet}

Ingredients:
{ing_str}

Instructions:
{instructions}
<|endoftext|>

"""
        f.write(recipe_block)
        count += 1

print(f"✓ Done! {count:,} recipes exported to train.txt")
conn.close()
