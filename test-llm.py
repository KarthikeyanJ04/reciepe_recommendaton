from transformers import pipeline

print("Loading KhaanaGPT model...")
pl = pipeline(
    task='text-generation',
    model='models/khaanaGPT',
    device=0  # Use GPU, -1 for CPU
)
print("✓ Model loaded!\n")

def create_prompt(ingredients):
    ingredients = ','.join([x.strip().lower() for x in ingredients.split(',')])
    ingredients = ingredients.strip().replace(',', '\n')
    s = f"<|startoftext|>Ingredients:\n{ingredients}\n"
    return s

# Test cases
test_ingredients = [
    'paneer, cream, tomato, onion',
    'chicken, tomatoes, aloo, jeera, curry powder',
    'rice, potatoes, spinach',
]

for ing in test_ingredients:
    print("="*70)
    print(f"INPUT: {ing}")
    print("="*70)
    
    prompt = create_prompt(ing)
    
    output = pl(
        prompt,
        max_new_tokens=512,
        penalty_alpha=0.6,
        top_k=4,
        pad_token_id=50259
    )[0]['generated_text']
    
    # Show full output
    print(output)
    print("\n")
