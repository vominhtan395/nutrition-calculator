# Nutrition Calculator - Cloud Computing Demo

Hệ thống tính toán dinh dưỡng dựa trên kiến trúc Microservices.

## Kiến trúc (Architecture)
- **Frontend:** Vanilla JS/HTML/CSS
- **API Gateway:** FastAPI, đóng vai trò Reverse Proxy & Error Handling.
- **Food Service:** FastAPI, đóng vai trò Translator, dịch từ khóa tiếng Việt sang tiếng Anh (chuẩn USDA) sử dụng thuật toán Fuzzy Matching (`rapidfuzz`).
- **Nutrition Service:** FastAPI, kết nối tới **USDA FoodData Central API** để lấy dữ liệu thực tế. Tích hợp In-memory Cache (`cachetools`) để tối ưu tốc độ.

## Cách chạy dự án
1. Đảm bảo file `.env` đã có `USDA_API_KEY`.
2. Chạy lệnh: `docker-compose up --build -d`
3. Mở file `frontend/index.html` trên trình duyệt.