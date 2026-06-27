from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(
    title="Food Catalog Service",
    version="1.0"
)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# LOAD DATA (FIXED FOR DOCKER)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "food_dictionary.json")

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        foods = json.load(f)
except Exception as e:
    print("❌ ERROR loading food_dictionary.json:", e)
    foods = []


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {
        "service": "Food Catalog Service",
        "status": "running"
    }


# =========================
# GET ALL FOODS (DEBUG)
# =========================
@app.get("/foods")
def get_all_foods():
    return foods


# =========================
# SEARCH FOOD (VIETNAMESE + ENGLISH)
# =========================
@app.get("/foods/search")
def search_food(name: str):

    keyword = name.strip().lower()

    for food in foods:
        aliases = [a.lower() for a in food.get("aliases", [])]

        if keyword in aliases:
            return {
                "displayName": food["displayName"],
                "query": food["query"],
                "category": food["category"]
            }

    raise HTTPException(
        status_code=404,
        detail=f"Food not found: {name}"
    )


# =========================
# POPULAR FOODS
# =========================
@app.get("/foods/popular")
def get_popular_foods():

    popular = [
        "Phở bò",
        "Cơm tấm",
        "Bánh mì",
        "Chuối",
        "Trứng gà",
        "Cà phê",
        "Trà sữa"
    ]

    result = []

    for food in foods:
        if food["displayName"] in popular:
            result.append({
                "displayName": food["displayName"],
                "query": food["query"],
                "category": food["category"]
            })

    return result