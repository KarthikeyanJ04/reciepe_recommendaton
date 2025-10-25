# nlg_generator.py
"""
Natural Language Generation for recipe descriptions
"""

import random

class RecipeNLG:
    """Generate natural language descriptions for recipes"""
    
    def generate_intro(self, recipe_name, category, cuisine='Indian'):
        """Generate recipe introduction"""
        veg_label = "vegetarian" if category == 'vegetarian' else "non-vegetarian"
        
        templates = [
            f"Discover the delicious {recipe_name}, a {veg_label} {cuisine} dish.",
            f"Learn how to make authentic {recipe_name}, a classic {veg_label} recipe.",
            f"{recipe_name} is a flavorful {cuisine} {veg_label} dish.",
            f"This {recipe_name} brings together traditional {cuisine} flavors.",
        ]
        
        return random.choice(templates)
    
    def generate_ingredient_summary(self, ingredients_list):
        """Generate natural description of ingredients"""
        if len(ingredients_list) <= 3:
            return f"Key ingredients: {', '.join(ingredients_list[:3])}."
        elif len(ingredients_list) <= 6:
            return f"Main ingredients are {', '.join(ingredients_list[:3])}, along with aromatic spices."
        else:
            return f"Features {', '.join(ingredients_list[:3])}, complemented by traditional spices."
    
    def generate_full_description(self, recipe_data):
        """Generate complete description"""
        name = recipe_data.get('name', 'Dish')
        category = recipe_data.get('category', 'vegetarian')
        cuisine = recipe_data.get('cuisine', 'Indian')
        ingredients = recipe_data.get('ingredients', [])
        
        intro = self.generate_intro(name, category, cuisine)
        
        if ingredients:
            ing_summary = self.generate_ingredient_summary(ingredients[:5])
            return f"{intro} {ing_summary}"
        
        return intro
    
    def generate_tips(self, recipe_data):
        """Generate cooking tips"""
        category = recipe_data.get('category', 'vegetarian')
        
        tips = [
            "💡 Prep all ingredients before cooking for a smoother process.",
            "💡 Use fresh spices for the best flavor.",
            "💡 Adjust spice levels to your taste preference.",
        ]
        
        if category == 'vegetarian':
            tips.append("💡 Add paneer or tofu for extra protein.")
        else:
            tips.append("💡 Marinating enhances tenderness and flavor.")
        
        return random.sample(tips, min(2, len(tips)))

# Global instance
nlg = RecipeNLG()
