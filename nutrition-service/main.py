from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import usda_client

app = FastAPI(title="Nutrition Service", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YÊU CẦU 14: Tối ưu - Cache kết quả USDA (Lưu tối đa 1000 món, tồn tại trong 24 tiếng)
cache = TTLCache(maxsize=1000, ttl=86400)

@app.get("/")
def home():
    return {"service": "Nutrition Service", "status": "running", "source": "USDA API"}

@app.get("/nutrition")
async def get_nutrition(food: str, weight: float):
    query_key = food.strip().lower()

    # Kiểm tra Cache trước
    if query_key in cache:
        base_nutrients = cache[query_key]
    else:
        # Gọi USDA nếu chưa có trong cache
        try:
            base_nutrients = await usda_client.fetch_nutrition_from_usda(query_key)
            if not base_nutrients:
                # YÊU CẦU 5: Fallback cắt bỏ các từ phụ để thử lại
                fallback_query = query_key.split()[0] # Chỉ lấy từ đầu tiên
                if fallback_query != query_key:
                    base_nutrients = await usda_client.fetch_nutrition_from_usda(fallback_query)

            if not base_nutrients:
                raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu dinh dưỡng từ USDA.")
            
            # Lưu vào cache
            cache[query_key] = base_nutrients

        except Exception as e:
            # Xử lý lỗi Timeout, 429...
            raise HTTPException(status_code=500, detail=str(e))

    # Tính toán theo khối lượng người dùng nhập (base_nutrients là /100g)
    factor = weight / 100.0

    return {
        "food": food,
        "weight": weight,
        "calories": round(base_nutrients["calories"] * factor, 2),
        "protein": round(base_nutrients["protein"] * factor, 2),
        "fat": round(base_nutrients["fat"] * factor, 2),
        "carbohydrates": round(base_nutrients["carbohydrates"] * factor, 2),
        "source": "USDA FoodData Central"
    }