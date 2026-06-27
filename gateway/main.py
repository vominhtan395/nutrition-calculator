from fastapi import FastAPI, HTTPException, Response
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
async def search_food(name: str, response: Response):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{FOOD_SERVICE}/foods/search", params={"name": name})
            response.status_code = res.status_code  # Proxy đúng status code về frontend
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Food Service Unavailable: {str(e)}")


@app.get("/api/foods/popular")
async def popular_foods(response: Response):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{FOOD_SERVICE}/foods/popular")
            response.status_code = res.status_code
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Food Service Unavailable: {str(e)}")


# ───────────────────────── NUTRITION ROUTES ─────────────────────────

@app.get("/api/nutrition")
async def nutrition(food: str, weight: float, response: Response):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"{NUTRITION_SERVICE}/nutrition",
                params={"food": food, "weight": weight}
            )
            response.status_code = res.status_code
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Nutrition Service Unavailable: {str(e)}")