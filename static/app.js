// static/app.js
let selectedCategory = 'all';

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedCategory = this.dataset.category;
    });
});

document.getElementById('searchBtn').addEventListener('click', searchRecipes);
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchRecipes();
});

async function searchRecipes() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        alert('Please enter some ingredients!');
        return;
    }

    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    searchBtn.disabled = true;
    loading.style.display = 'block';
    results.innerHTML = '';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, category: selectedCategory })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.recipes);
        } else {
            results.innerHTML = `<div class="no-results">❌ ${data.error}</div>`;
        }
    } catch (error) {
        results.innerHTML = '<div class="no-results">❌ Search failed</div>';
    } finally {
        searchBtn.disabled = false;
        loading.style.display = 'none';
    }
}

function displayResults(recipes) {
    const results = document.getElementById('results');
    
    if (recipes.length === 0) {
        results.innerHTML = '<div class="no-results">🔍 No recipes found. Try different ingredients!</div>';
        return;
    }

    results.innerHTML = recipes.map(recipe => `
        <div class="recipe-card">
            <div class="recipe-header">
                <div class="recipe-title">${recipe.name}</div>
                <div class="recipe-meta">
                    <span>📊 Match: ${(recipe.similarity * 100).toFixed(1)}%</span>
                    <span>🥘 ${recipe.ingredients.length} ingredients</span>
                    <span>${recipe.category === 'vegetarian' ? '🥗 Veg' : '🍗 Non-Veg'}</span>
                    ${recipe.cuisine ? `<span>🌍 ${recipe.cuisine}</span>` : ''}
                    ${recipe.prep_time ? `<span>⏱️ ${recipe.prep_time}</span>` : ''}
                </div>
                ${recipe.description ? `<div class="recipe-description">${recipe.description}</div>` : ''}
            </div>
            
            <div class="recipe-body">
                <div class="section-title">🥘 Ingredients</div>
                <div class="ingredients-grid">
                    ${recipe.ingredients.map(ing => `
                        <div class="ingredient-item">${ing}</div>
                    `).join('')}
                </div>

                <div class="section-title">👨‍🍳 Instructions</div>
                <div class="instructions-list">
                    ${recipe.instructions.map(step => `
                        <div class="instruction-step">${step}</div>
                    `).join('')}
                </div>

                ${recipe.tips && recipe.tips.length > 0 ? `
                    <div class="tips-section">
                        <div class="section-title" style="color: #856404; border-bottom-color: #ffeaa7;">💡 Cooking Tips</div>
                        ${recipe.tips.map(tip => `<div class="tip-item">${tip}</div>`).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}
