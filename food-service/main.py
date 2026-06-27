from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rapidfuzz import process, fuzz
import json
import os
from utils import normalize_vietnamese

app = FastAPI(title="Food Catalog Service", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "food_dictionary.json")

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        foods = json.load(f)
except Exception as e:
    print("❌ ERROR loading food_dictionary.json:", e)
    foods = []

# Xây dựng index tra cứu phẳng (Flat Index) để fuzzy search chạy nhanh
# Dạng: {"tao": {"displayName": "Táo", "query": "apple", ...}, "tao do": {...}}
lookup_index = {}
for food in foods:
    for alias in food.get("aliases", []):
        normalized_alias = normalize_vietnamese(alias)
        lookup_index[normalized_alias] = food

@app.get("/")
def home():
    return {"service": "Food Catalog Service", "status": "running"}

@app.get("/foods/search")
def search_food(name: str):
    keyword_norm = normalize_vietnamese(name)
    
    # 1. Exact match (Tìm chính xác)
    if keyword_norm in lookup_index:
        return extract_food_data(lookup_index[keyword_norm])
    
    # 2. Fuzzy match (Tìm xấp xỉ nếu gõ sai chính tả)
    choices = list(lookup_index.keys())
    # Lấy ra kết quả tốt nhất, score từ 0-100
    best_match = process.extractOne(keyword_norm, choices, scorer=fuzz.WRatio)
    
    # best_match có dạng (chuỗi_khớp, điểm_số, index)
    if best_match and best_match[1] >= 80: # Ngưỡng tự tin 80%
        matched_key = best_match[0]
        return extract_food_data(lookup_index[matched_key])

    raise HTTPException(status_code=404, detail="Không tìm thấy món ăn trong từ điển")

@app.get("/foods/popular")
def get_popular_foods():
    popular_names = ["Phở bò", "Cơm tấm", "Bánh mì", "Chuối", "Trứng gà", "Cà phê", "Trà sữa", "Cơm trắng", "Táo"]
    result = []
    for food in foods:
        if food["displayName"] in popular_names:
            result.append(extract_food_data(food))
    return result

def extract_food_data(food_obj: dict) -> dict:
    return {
        "displayName": food_obj["displayName"],
        "query": food_obj["query"], # Tên tiếng Anh chuẩn để gọi USDA
        "category": food_obj["category"]
    }