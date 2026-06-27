import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI(title="API Gateway", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đọc URL nội bộ từ biến môi trường (Linh hoạt cho Local và Render)
FOOD_SERVICE = os.getenv("FOOD_SERVICE_URL", "https://food-service-pzpi.onrender.com")
NUTRITION_SERVICE = os.getenv("NUTRITION_SERVICE_URL", "https://nutrition-service-pzpi.onrender.com")
TIMEOUT = 15.0

# ───────────────────────── API ROUTES (PHẢI KHAI BÁO TRƯỚC STATIC FILES) ─────────────────────────

@app.get("/api/foods/search")
async def search_food(name: str, response: Response):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            res = await client.get(f"{FOOD_SERVICE}/foods/search", params={"name": name})
            response.status_code = res.status_code
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Food Service Unavailable: {str(e)}")

@app.get("/api/foods/popular")
async def popular_foods(response: Response):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            res = await client.get(f"{FOOD_SERVICE}/foods/popular")
            response.status_code = res.status_code
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Food Service Unavailable: {str(e)}")

@app.get("/api/nutrition")
async def nutrition(food: str, weight: float, response: Response):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            res = await client.get(
                f"{NUTRITION_SERVICE}/nutrition",
                params={"food": food, "weight": weight}
            )
            response.status_code = res.status_code
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Nutrition Service Unavailable: {str(e)}")

# ───────────────────────── SERVE FRONTEND (STATIC FILES) ─────────────────────────
# Định vị thư mục frontend (Nằm cùng cấp với main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount toàn bộ nội dung thư mục frontend. html=True để tự động phục vụ index.html tại route "/"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")