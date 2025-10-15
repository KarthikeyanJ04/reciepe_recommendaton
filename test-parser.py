# test_parser.py
import re

def parse_llm_output(generated_text):
    """Test the parsing logic"""
    lines = [l.strip() for l in generated_text.split('\n') if l.strip()]
    
    ingredients_list = []
    directions_list = []
    
    for line in lines:
        line_lower = line.lower()
        
        # Skip section headers
        if line_lower in ['instructions:', 'directions:', 'method:']:
            continue
        
        # Check if direction (full sentence)
        is_direction = (
            '.' in line or
            len(line.split()) > 6 or
            any(verb in line_lower for verb in ['heat', 'add', 'mix', 'cook', 'stir', 'wash', 'cut', 'sauté', 'boil', 'fry', 'pour', 'serve', 'turn', 'allow', 'we will'])
        )
        
        if is_direction:
            directions_list.append(line)
        else:
            ingredients_list.append(line)
    
    # Extract title
    recipe_name = "AI Generated Recipe"
    if ingredients_list and len(ingredients_list[0]) < 50:
        first_line = ingredients_list[0]
        if ',' not in first_line and len(first_line.split()) <= 4:
            recipe_name = first_line.title()
            ingredients_list = ingredients_list[1:]
    
    return recipe_name, ingredients_list, directions_list

# Test with actual output
test_output = """paneer
cream
tomato
onion
cumin powder (jeera)
turmeric powder
green chillies
sunflower oil

Instructions:
we will first make the paneer masala.
heat oil in a kadai/wok.
add the onion and sauté till the onions soften.add the chopped  green chillies,  turmeric powder, coriander powder, salt and cook till the onions are cooked.
now add the paneer masala and mix well.
once done, turn off the heat and transfer to a bowl.
garnish with chopped  coriander leaves, chopped coriander leaves and serve paneer masala along with kadhi raita and a glass of kadhi chai for a weekday meal."""

name, ingredients, directions = parse_llm_output(test_output)

print("="*70)
print(f"TITLE: {name}")
print("="*70)
print("\nINGREDIENTS:")
for i, ing in enumerate(ingredients, 1):
    print(f"  {i}. {ing}")

print("\nDIRECTIONS:")
for i, dir in enumerate(directions, 1):
    print(f"  {i}. {dir}")