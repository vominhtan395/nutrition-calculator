from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway", version="1.0")

# CORS cho frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FOOD_SERVICE = "http://food-service:8001"
NUTRITION_SERVICE = "http://nutrition-service:8002"


@app.get("/")
def home():
    return {"service": "API Gateway", "status": "running"}


# ───────────────────────── FOOD ROUTES ─────────────────────────

@app.get("/api/foods/search")
async def search_food(name: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{FOOD_SERVICE}/foods/search", params={"name": name})
        return res.json()


@app.get("/api/foods/popular")
async def popular_foods():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{FOOD_SERVICE}/foods/popular")
        return res.json()


# ───────────────────────── NUTRITION ROUTES ─────────────────────────

@app.get("/api/nutrition")
async def nutrition(food: str, weight: float):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{NUTRITION_SERVICE}/nutrition",
            params={"food": food, "weight": weight}
        )
        return res.json()