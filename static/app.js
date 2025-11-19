// static/app.js

/* ==========================================
   UTILITIES
   ========================================== */

function escapeHtml(str){
  if(str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* ==========================================
   THEME & INIT
   ========================================== */

const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;
const currentTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', currentTheme);

if(themeToggle){
  themeToggle.addEventListener('click', () => {
    const current = htmlElement.getAttribute('data-theme');
    const newTheme = current === 'light' ? 'dark' : 'light';
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  });
}

const searchBtnEl = document.getElementById('searchBtn');
const searchInputEl = document.getElementById('searchInput');

if(searchBtnEl) searchBtnEl.addEventListener('click', searchRecipes);
if(searchInputEl) searchInputEl.addEventListener('keypress', (e) => { if(e.key==='Enter') searchRecipes(); });

/* ==========================================
   CORE LOGIC
   ========================================== */

let recipeDataStore = {};

async function searchRecipes(){
  const query = (document.getElementById('searchInput')||{value:''}).value.trim();
  if(!query) return;

  const searchBtn = document.getElementById('searchBtn');
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');

  if(searchBtn) searchBtn.disabled = true;
  if(loading) loading.style.display = 'block';
  if(results) results.innerHTML = '';

  try {
    const response = await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await response.json();
    
    if(data.success){
      displayResults(data.recipes);
    } else {
      results.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">No recipes found.</div>`;
    }
  } catch(e) {
    console.error(e);
    results.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">An error occurred.</div>`;
  } finally {
    if(searchBtn) searchBtn.disabled = false;
    if(loading) loading.style.display = 'none';
  }
}

function displayResults(recipes){
  const results = document.getElementById('results');
  if(!results) return;

  results.innerHTML = recipes.map(recipe => {
    recipeDataStore[recipe.id] = { recipe: recipe, parsed_steps: recipe.parsed_steps };
    return getRecipeCardHtml(recipe);
  }).join('');
}

function getRecipeCardHtml(recipe) {
  const visibleIngredients = recipe.ingredients.slice(0, 6);
  const remaining = recipe.ingredients.length - 6;

  return `
    <div class="recipe-card" id="card-${recipe.id}">
      <div class="recipe-header">
        <span class="ai-badge">AI Generated</span>
        <h2 class="recipe-title">${escapeHtml(recipe.name)}</h2>
        <p class="recipe-desc">${escapeHtml(recipe.description)}</p>
      </div>
      
      <div class="recipe-body">
        <div>
          <h3 class="mini-section-title">Ingredients</h3>
          <div class="ingredient-tags">
            ${visibleIngredients.map(ing => `<span class="ing-tag">${escapeHtml(ing)}</span>`).join('')}
            ${remaining > 0 ? `<span class="ing-tag" style="opacity:0.5">+${remaining}</span>` : ''}
          </div>
        </div>
        
        <div class="action-area">
          <button class="cook-btn" onclick="openCookingAssistant('${recipe.id}')">
            Start Cooking
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>
    </div>
  `;
}

async function openCookingAssistant(recipeId) {
  const recipeData = recipeDataStore[recipeId];
  if (!recipeData) {
    alert('Could not find recipe data. Please try again.');
    return;
  }

  try {
    const response = await fetch('/cooking-assistant-recipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(recipeData)
    });

    if (response.ok) {
      const result = await response.json();
      if (result.success) {
        document.open();
        document.write(result.html);
        document.close();
      } else {
        console.error('Failed to load recipe page:', result.error);
        alert('Could not load the cooking assistant. Please try again.');
      }
    } else {
      throw new Error(`Server responded with status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error opening cooking assistant:', error);
    alert('An error occurred while trying to load the recipe. Please check the console for details.');
  }
}