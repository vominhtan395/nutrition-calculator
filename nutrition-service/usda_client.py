import httpx
from rapidfuzz import process, fuzz
from config import USDA_API_KEY

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# ID Dinh dưỡng chuẩn theo USDA
NUTRIENT_IDS = {
    "calories": 1008, # Năng lượng (kcal)
    "protein": 1003,  # Protein (g)
    "fat": 1004,      # Total lipid (fat) (g)
    "carbs": 1005     # Carbohydrate (g)
}

async def fetch_nutrition_from_usda(query: str):
    """
    Gọi USDA API, tìm danh sách thức ăn và phân tích chọn kết quả sát nhất.
    """
    params = {
        "api_key": USDA_API_KEY,
        "query": query,
        "pageSize": 10,  # Lấy 10 kết quả đầu
        "dataType": "Foundation,SR Legacy,Survey (FNDDS)" # Ưu tiên thực phẩm cơ bản
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(USDA_SEARCH_URL, params=params)
        
        if response.status_code == 429:
            raise Exception("USDA Rate Limit Exceeded (Quá giới hạn gọi API).")
        if response.status_code != 200:
            raise Exception(f"USDA API Error: {response.status_code}")
            
        data = response.json()
        foods = data.get("foods", [])

        if not foods:
            return None

        # --- YÊU CẦU 7: Chọn kết quả phù hợp nhất bằng Fuzzy Match ---
        # USDA có thể trả về: "Apple raw", "Apple juice", "Apple pie".
        # Ta cần chọn item có description giống với 'query' nhất.
        choices = {food["fdcId"]: food["description"].lower() for food in foods}
        best_match = process.extractOne(query.lower(), choices, scorer=fuzz.token_sort_ratio)
        
        best_food = foods[0] # Fallback lấy cái đầu tiên
        if best_match and best_match[1] > 50: # Nếu độ tương đồng > 50%
            matched_id = best_match[2] # key trong dict
            for f in foods:
                if f["fdcId"] == matched_id:
                    best_food = f
                    break

        # Bóc tách dinh dưỡng (USDA mặc định tính trên 100g)
        nutrients_data = {
            "calories": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0
        }

        for nutrient in best_food.get("foodNutrients", []):
            nid = nutrient.get("nutrientId")
            val = float(nutrient.get("value", 0.0))
            
            if nid == NUTRIENT_IDS["calories"]:
                nutrients_data["calories"] = val
            elif nid == NUTRIENT_IDS["protein"]:
                nutrients_data["protein"] = val
            elif nid == NUTRIENT_IDS["fat"]:
                nutrients_data["fat"] = val
            elif nid == NUTRIENT_IDS["carbs"]:
                nutrients_data["carbohydrates"] = val

        return nutrients_data