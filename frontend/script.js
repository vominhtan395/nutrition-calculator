/**
 * Nutrition Calculator – script.js (PRODUCTION REFACTOR)
 * Microservices via API Gateway: http://localhost:8000
 */

const API_BASE = 'http://localhost:8000';

const CATEGORY_EMOJI = {
  'fruit': '🍎',
  'vegetable': '🥦',
  'meat': '🥩',
  'seafood': '🦐',
  'grain': '🌾',
  'dairy': '🧀',
  'dessert': '🍰',
  'beverage': '🥤',
  'vietnamese food': '🍜',
  'snack': '🍿',
  'legume': '🫘',
  'nut': '🥜',
  'egg': '🥚',
  'soup': '🍲',
  'noodle': '🍝',
  'rice': '🍚',
  'fast food': '🍔',
  'protein': '🍖',
  'drink': '🥤',
  'staple food': '🍚'
};

function categoryEmoji(cat = '') {
  return CATEGORY_EMOJI[String(cat).toLowerCase()] || '🥗';
}

const foodInput = document.getElementById('food-input');
const weightInput = document.getElementById('weight-input');
const errorBox = document.getElementById('error-box');
const errorMessage = document.getElementById('error-message');
const resultSection = document.getElementById('result-section');
const popularGrid = document.getElementById('popular-grid');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

function showLoading(msg = 'Đang xử lý...') {
  loadingText.textContent = msg;
  loadingOverlay.hidden = false;
}

function hideLoading() {
  loadingOverlay.hidden = true;
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorBox.hidden = false;
  resultSection.hidden = true;
}

function clearError() {
  errorBox.hidden = true;
}

async function handleSearch(prefillFood = null, prefillWeight = null) {
  const foodName = (prefillFood ?? foodInput.value).trim();
  const weight = parseInt(prefillWeight ?? weightInput.value, 10);

  if (!foodName) return showError('Vui lòng nhập tên món ăn.');
  if (!weight || weight <= 0) return showError('Vui lòng nhập khối lượng hợp lệ.');

  clearError();
  resultSection.hidden = true;

  try {
    showLoading('Đang phân tích món ăn (Fuzzy Search)...');

    const foodData = await searchFood(foodName);
    if (foodData.error) {
        return showError(foodData.detail || 'Không có món ăn này trong từ điển.');
    }

    showLoading('Đang tải dữ liệu từ USDA FoodData Central...');

    const nutritionData = await getNutrition(foodData.query, weight);
    if (nutritionData.error) {
        return showError(nutritionData.detail || 'USDA: Không tìm thấy dữ liệu dinh dưỡng.');
    }

    renderResult(foodData, nutritionData);
    resultSection.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    console.error(err);
    showError('Lỗi Server: Không thể kết nối tới API Gateway hoặc Timeout.');
  } finally {
    hideLoading();
  }
}

async function searchFood(keyword) {
  const res = await fetch(
    `${API_BASE}/api/foods/search?name=${encodeURIComponent(keyword)}`
  );
  const data = await res.json();
  if (!res.ok) return { error: true, detail: data.detail };
  return data;
}

async function getNutrition(food, weight) {
  const res = await fetch(
    `${API_BASE}/api/nutrition?food=${encodeURIComponent(food)}&weight=${weight}`
  );
  const data = await res.json();
  if (!res.ok) return { error: true, detail: data.detail };
  return data;
}

async function fetchPopularFoods() {
  const res = await fetch(`${API_BASE}/api/foods/popular`);
  if (!res.ok) throw new Error('Popular API error');
  return res.json();
}

function renderResult(foodData, nutritionData) {
  const { displayName, category } = foodData;
  const { calories, protein, fat, carbohydrates, weight } = nutritionData;

  // Thêm watermark USDA để chuyên nghiệp
  document.getElementById('result-food-name').textContent =
    `${categoryEmoji(category)} ${displayName} · ${weight}g (Nguồn: USDA)`;

  document.getElementById('ring-cal').textContent = Math.round(calories || 0);
  document.getElementById('macro-protein').textContent = (protein || 0).toFixed(1);
  document.getElementById('macro-fat').textContent = (fat || 0).toFixed(1);
  document.getElementById('macro-carb').textContent = (carbohydrates || 0).toFixed(1);
  document.getElementById('macro-weight').textContent = weight;

  drawRing(protein || 0, fat || 0, carbohydrates || 0);
  resultSection.hidden = false;
}

function drawRing(protein, fat, carb) {
  const R = 70;
  const C = 2 * Math.PI * R;
  const GAP = 6;
  const total = protein + fat + carb;
  
  if (total <= 0) return;

  const scale = v => ((v / total) * (C - 3 * GAP));
  const p = scale(protein);
  const f = scale(fat);
  const c = scale(carb);

  setRing('ring-protein', p, 0, C);
  setRing('ring-fat', f, p + GAP, C);
  setRing('ring-carb', c, p + GAP + f + GAP, C);
}

function setRing(id, len, offset, C) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.strokeDasharray = `${len} ${C - len}`;
  el.style.strokeDashoffset = -offset;
}

async function loadPopularFoods() {
  try {
    const foods = await fetchPopularFoods();
    popularGrid.innerHTML = foods.map((f, i) => `
      <div class="popular-card"
        style="animation-delay:${i * 50}ms"
        onclick="quickLookup('${escapeHtml(f.displayName)}','${escapeHtml(f.query)}')">

        <span class="popular-emoji">${categoryEmoji(f.category)}</span>
        <div class="popular-name">${escapeHtml(f.displayName)}</div>
        <span class="popular-category">${escapeHtml(f.category)}</span>
      </div>
    `).join('');
  } catch (e) {
    popularGrid.innerHTML = `<p>Lỗi tải dữ liệu phổ biến</p>`;
  }
}

function quickLookup(name, query) {
  foodInput.value = name;
  weightInput.value = weightInput.value || 100;
  setTimeout(() => handleSearch(), 200);
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

foodInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') handleSearch();
});

weightInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') handleSearch();
});

document.addEventListener('DOMContentLoaded', () => {
  loadPopularFoods();
});