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

function normalizeInstruction(raw){
  if(!raw) return '';
  let s = String(raw).trim();
  // Simple cleanup logic
  s = s.replace(/^[\[\]\(\)\"']+|[\[\]\(\)\"']+$/g, '').replace(/\\n/g, '\n');
  return s;
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

let selectedCategory = 'all';
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    selectedCategory = this.dataset.category;
  });
});

const searchBtnEl = document.getElementById('searchBtn');
const searchInputEl = document.getElementById('searchInput');

if(searchBtnEl) searchBtnEl.addEventListener('click', searchRecipes);
if(searchInputEl) searchInputEl.addEventListener('keypress', (e) => { if(e.key==='Enter') searchRecipes(); });

/* ==========================================
   CORE LOGIC
   ========================================== */

async function searchRecipes(){
  const query = (document.getElementById('searchInput')||{value:''}).value.trim();
  if(!query) return;

  const searchBtn = document.getElementById('searchBtn');
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');

  if(searchBtn) searchBtn.disabled = true;
  if(loading) loading.style.display = 'block';
  if(results) results.innerHTML = '';

  try{
    const response = await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, category: selectedCategory })
    });
    const data = await response.json();
    
    if(data.success){
      displayResults(data.recipes, query);
    } else {
      results.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">No recipes found.</div>`;
    }
  }catch(e){
    console.error(e);
  }finally{
    if(searchBtn) searchBtn.disabled = false;
    if(loading) loading.style.display = 'none';
  }
}

function displayResults(recipes, query){
  const results = document.getElementById('results');
  if(!results) return;

  // Render Skeleton
  results.innerHTML = recipes.map(recipe => `
    <div class="recipe-card" id="card-${recipe.id}">
      <div class="recipe-header">
        <div class="ai-badge">Loading...</div>
        <h2 class="recipe-title">${escapeHtml(recipe.name)}</h2>
      </div>
      <div class="recipe-body">
        <div style="height:100px; display:flex; align-items:center; justify-content:center; color:var(--text-light);">
          Processing...
        </div>
      </div>
    </div>
  `).join('');

  recipes.forEach(r => fetchRecipeDetails(r.id, r.name, query));
}

async function fetchRecipeDetails(recipeId, dishName, query){
  try {
    const response = await fetch('/cook-with-ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipe_id: recipeId, query: query })
    });
    const data = await response.json();
    
    if(data.success && data.recipe){
      updateRecipeCard(recipeId, {
        name: data.recipe.name,
        ingredients: data.recipe.ingredients || [],
        description: data.recipe.description || '',
        instructions: data.recipe.instructions || [],
        from_db: true
      });
    }
  } catch(e) { console.error(e); }
}

function updateRecipeCard(recipeId, details){
  const card = document.getElementById(`card-${recipeId}`);
  if(!card) return;

  const visibleIngredients = details.ingredients.slice(0, 6);
  const remaining = details.ingredients.length - 6;

  // Modern Card HTML Structure
  card.innerHTML = `
    <div class="recipe-header">
      <span class="ai-badge">AI Curated</span>
      <h2 class="recipe-title">${escapeHtml(details.name)}</h2>
      <p class="recipe-desc">${escapeHtml(details.description)}</p>
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
        <button class="cook-btn" onclick="openCookingAssistant(${recipeId})">
          Start Cooking
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
      </div>
    </div>
  `;
}

function openCookingAssistant(recipeId) {
  window.location.href = `/cooking-assistant?recipe_id=${recipeId}`;
}