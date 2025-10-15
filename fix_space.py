import sqlite3

print("="*80)
print("FIXING INGREDIENT SPACING (SQL VERSION)")
print("="*80)

conn = sqlite3.connect('models/recipes.db')

print("\nExecuting SQL update...")
print("This will take 2-3 minutes for 2.2M recipes...")
print("(Be patient, no progress bar but it's working!)")

# Remove quotes, brackets, and replace commas with spaces
cursor = conn.execute("""
    UPDATE recipes 
    SET cleaned_ingredients = 
        TRIM(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                LOWER(cleaned_ingredients),
                                '[', ''
                            ),
                            ']', ''
                        ),
                        '"', ''
                    ),
                    "'", ''
                ),
                ',', ' '
            )
        )
""")

conn.commit()

print(f"\n✓ Updated {cursor.rowcount:,} recipes")

# Clean up multiple spaces
print("\nCleaning up multiple spaces...")
cursor = conn.execute("""
    UPDATE recipes 
    SET cleaned_ingredients = 
        REPLACE(
            REPLACE(
                REPLACE(
                    cleaned_ingredients,
                    '  ', ' '
                ),
                '  ', ' '
            ),
            '  ', ' '
        )
""")

conn.commit()

print(f"✓ Cleaned {cursor.rowcount:,} recipes")

# Verify
print("\nVerifying samples:")
cursor = conn.execute("SELECT name, cleaned_ingredients FROM recipes LIMIT 5")
samples = cursor.fetchall()

for name, ingredients in samples:
    print(f"\n{name}")
    print(f"  Ingredients: {ingredients[:100]}")

conn.close()

print("\n" + "="*80)
print("✅ INGREDIENTS FIXED!")
print("="*80)
print("\nNext steps:")
print("  1. python retrain_tfidf.py")
print("  2. python retrain_embeddings_final.py")
print("  3. python app.py")
