import os
import json

def load_config(config_path='config.json'):
    """
    Đọc file JSON cấu hình.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file {config_path} not found")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_dir(path):
    """
    Tạo thư mục nếu chưa tồn tại.
    """
    os.makedirs(path, exist_ok=True)