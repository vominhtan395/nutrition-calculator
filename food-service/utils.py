import unicodedata
import re

def normalize_vietnamese(text: str) -> str:
    """
    Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu, viết thường,
    loại bỏ ký tự đặc biệt và khoảng trắng thừa.
    """
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'đ', 'd', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()