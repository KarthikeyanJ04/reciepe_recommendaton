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
      displayResults(data.recipes);
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

function displayResults(recipes){
  const results = document.getElementById('results');
  if(!results) return;

  if(!recipes || recipes.length === 0){
    results.innerHTML = '<div class="no-results">No recipes found. Try different ingredients!</div>';
    return;
  }

  results.innerHTML = recipes.map(recipe => `
    <div class="recipe-card">
      <div class="recipe-header">
        <h2 class="recipe-title">${escapeHtml(recipe.name)}</h2>
        <div class="recipe-meta">
          <span> ${escapeHtml(recipe.course || 'Main Course')}</span>
        </div>
        ${recipe.description ? `<div class="recipe-description">${escapeHtml(recipe.description)}</div>` : ''}
      </div>
      <div class="recipe-body">
        <div class="ingredients-section">
          <h3 class="section-title">Ingredients</h3>
          <div class="ingredients-list">
            ${ (recipe.ingredients||[]).map(ing => `<div class="ingredient-item"> ${escapeHtml(ing)}</div>`).join('') }
          </div>
        </div>

        <div class="instructions-section">
          <h3 class="section-title">Instructions</h3>
          <div class="instructions-list">
            ${ renderInstructions(recipe) }
          </div>
        </div>
        
        <div class="recipe-actions">
          <button class="cook-ai-btn" onclick="openCookingAssistant(${recipe.id})">
            👨‍🍳 Cook with AI Assistant
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

function openCookingAssistant(recipeId) {
  window.open(`/cooking-assistant?recipe_id=${recipeId}`, 'cooking_window', 'width=1000,height=800');
}
