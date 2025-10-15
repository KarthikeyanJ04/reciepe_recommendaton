# convert_to_sqlite.py
"""
Convert CSV to SQLite database for efficient querying
Run this ONCE after training
"""

import pandas as pd
import sqlite3
import time

print("Converting recipe CSV to SQLite database...")
print("This makes loading MUCH faster and uses less RAM")

start = time.time()

# Read CSV
print("\nReading CSV...")
df = pd.read_csv('models/recipe_train_data.csv')
print(f"✓ Loaded {len(df):,} recipes")

# Create SQLite database
print("\nCreating database...")
conn = sqlite3.connect('models/recipes.db')

# Save to database
df.to_sql('recipes', conn, if_exists='replace', index=True, index_label='idx')

# Create index for fast lookups
print("Creating index...")
conn.execute('CREATE INDEX IF NOT EXISTS idx_index ON recipes (idx)')
conn.commit()
conn.close()

print(f"\n✓ Database created in {time.time() - start:.2f}s")
print("  File: models/recipes.db")

import os
db_size = os.path.getsize('models/recipes.db') / 1024**2
print(f"  Size: {db_size:.2f} MB")
print("\nNow use the SQLite version of recommender.py")
