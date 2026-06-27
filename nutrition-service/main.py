from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Nutrition Service",
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

# ================= NUTRITION DATA =================
nutrition_db = {
    "apple": {
        "calories": 52,
        "protein": 0.3,
        "fat": 0.2,
        "carbohydrates": 14
    },
    "banana": {
        "calories": 89,
        "protein": 1.1,
        "fat": 0.3,
        "carbohydrates": 23
    },
    "rice": {
        "calories": 130,
        "protein": 2.4,
        "fat": 0.2,
        "carbohydrates": 28
    },
    "beef pho": {
        "calories": 120,
        "protein": 8,
        "fat": 3,
        "carbohydrates": 15
    },
    "pizza": {
        "calories": 266,
        "protein": 11,
        "fat": 10,
        "carbohydrates": 33
    },
    "egg": {
        "calories": 155,
        "protein": 13,
        "fat": 11,
        "carbohydrates": 1.1
    }
}

# ================= ROOT =================
@app.get("/")
def home():
    return {
        "service": "Nutrition Service",
        "status": "running"
    }

# ================= MAIN API =================
@app.get("/nutrition")
def get_nutrition(food: str, weight: float):

    key = food.strip().lower()

    if key not in nutrition_db:
        raise HTTPException(
            status_code=404,
            detail="Nutrition data not found"
        )

    base = nutrition_db[key]

    factor = weight / 100

    return {
        "food": food,
        "weight": weight,
        "calories": round(base["calories"] * factor, 2),
        "protein": round(base["protein"] * factor, 2),
        "fat": round(base["fat"] * factor, 2),
        "carbohydrates": round(base["carbohydrates"] * factor, 2)
    }