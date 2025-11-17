// static/app.js

// Small helper library to normalize and safely render recipe instructions.
// These helpers are used by the UI rendering below.
function escapeHtml(str){
  if(str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function decodeUnicodeEscapes(s){
  try{
    return s.replace(/\\u[0-9a-fA-F]{4}/g, function(m){
      return String.fromCharCode(parseInt(m.slice(2),16));
    });
  }catch(e){ return s; }
}

function fixMojibake(s){
  if(!s) return s;
  return s
    .replace(/â[\u0092\u0093\u0094]/g, '"')
    .replace(/â/g, "'")
    .replace(/â/g, '-')
    .replace(/â/g, '--')
    .replace(/â/g, '')
    .replace(/Â/g, '')
    .replace(/ðŸ/g, '')
    .replace(/ï/gi, '');
}

function normalizeInstruction(raw){
  if(!raw) return '';
  let s = String(raw).trim();

  // If the field is a JSON array encoded as a string, try to parse it.
  if((s.startsWith('[') && s.endsWith(']')) || (s.startsWith('("[') && s.endsWith('\"]\)'))){
    try{
      const parsed = JSON.parse(s);
      if(Array.isArray(parsed)){
        s = parsed.join('\n');
      } else if(typeof parsed === 'string'){
        s = parsed;
      }
    }catch(e){ /* ignore parse errors */ }
  }

  s = decodeUnicodeEscapes(s);
  s = fixMojibake(s);
  s = s.replace(/\|/g, '\n');
  s = s.replace(/^[\[\]\(\)\"']+|[\[\]\(\)\"']+$/g, '');
  s = s.replace(/\r/g, '');
  s = s.replace(/\n{2,}/g, '\n');
  s = s.trim();
  return s;
}

function renderInstructions(recipe){
  if(!recipe || !recipe.instructions) return '';
  return recipe.instructions.map(function(rawStep){
    const step = normalizeInstruction(rawStep);
    return '<div class="instruction-step">' + escapeHtml(step).replace(/\n/g, '<br>') + '</div>';
  }).join('');
}

// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;

// Check for saved theme preference or default to 'light'
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

// Original app logic
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
if(searchInputEl) searchInputEl.addEventListener('keypress', function(e) { if (e.key === 'Enter') searchRecipes(); });

async function searchRecipes(){
  const query = (document.getElementById('searchInput')||{value:''}).value.trim();
  if(!query){ alert('Please enter some ingredients!'); return; }

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
      if(results) results.innerHTML = `<div class="no-results">${escapeHtml(data.message || 'No recipes found')}</div>`;
    }
  }catch(e){
    if(results) results.innerHTML = '<div class="no-results">Error fetching recipes. Please try again.</div>';
  }finally{
    if(searchBtn) searchBtn.disabled = false;
    if(loading) loading.style.display = 'none';
  }
}

async function displayResults(recipes, query){
  const results = document.getElementById('results');
  if(!results) return;

  if(!recipes || recipes.length === 0){
    results.innerHTML = '<div class="no-results">No recipes found. Try different ingredients!</div>';
    return;
  }

  // Create cards with loading state
  results.innerHTML = recipes.map(recipe => `
    <div class="recipe-card" id="card-${recipe.id}">
      <div class="recipe-header">
        <h2 class="recipe-title">${escapeHtml(recipe.name)}</h2>
        <div class="recipe-meta">
          <span>Loading details...</span>
        </div>
      </div>
      <div class="recipe-body">
        <div style="text-align:center;padding:20px;color:#999;">
          <div class="spinner"></div>
          <p>Generating recipe with AI...</p>
        </div>
      </div>
    </div>
  `).join('');

  // Now fetch AI-generated details for each recipe, passing recipe_id from DB
  for (const recipe of recipes) {
    await fetchRecipeDetails(recipe.id, recipe.name, query);
  }
}

async function fetchRecipeDetails(recipeId, dishName, query){
  try {
    const response = await fetch('/cook-with-ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        recipe_id: recipeId,
        query: query
      })
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
    } else {
      updateRecipeCardError(recipeId, data.error || 'Failed to load recipe');
    }
  } catch(e) {
    console.error('Error fetching recipe details:', e);
    updateRecipeCardError(recipeId, 'Error loading recipe');
  }
}

function updateRecipeCard(recipeId, details){
  const card = document.getElementById(`card-${recipeId}`);
  if(!card) return;

  const sourceLabel = details.from_db ? 'DB + AI Enhanced' : 'AI Generated';

  card.innerHTML = `
    <div class="recipe-header">
      <h2 class="recipe-title">${escapeHtml(details.name)}</h2>
      <div class="recipe-meta">
        <span>${sourceLabel} Recipe</span>
      </div>
      ${details.description ? `<div class="recipe-description">${escapeHtml(details.description)}</div>` : ''}
    </div>
    <div class="recipe-body">
      <div class="ingredients-section">
        <h3 class="section-title">Ingredients</h3>
        <div class="ingredients-list">
          ${details.ingredients.map(ing => `<div class="ingredient-item">✓ ${escapeHtml(ing)}</div>`).join('')}
        </div>
      </div>

      <div class="instructions-section">
        <h3 class="section-title">Cooking Steps</h3>
        <div class="instructions-list">
          ${details.instructions.map((step, idx) => `
            <div class="instruction-step">
              <strong>Step ${idx + 1}:</strong> ${escapeHtml(step).replace(/\n/g, '<br>')}
            </div>
          `).join('')}
        </div>
      </div>
      
      <div class="recipe-actions">
        <button class="cook-ai-btn" onclick="openCookingAssistant(${recipeId})">
          👨‍🍳 Cook with AI Assistant
        </button>
      </div>
    </div>
  `;
}

function updateRecipeCardError(recipeId, error){
  const card = document.getElementById(`card-${recipeId}`);
  if(!card) return;

  card.innerHTML = `
    <div class="recipe-body">
      <div style="color:#e74c3c;padding:20px;text-align:center;">
        <p>${escapeHtml(error)}</p>
      </div>
    </div>
  `;
}

function openCookingAssistant(recipeId) {
  window.location.href = `/cooking-assistant?recipe_id=${recipeId}`;
}
