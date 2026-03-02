"""
Application configuration and constants
"""
import os

# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/user_behavior'
)
DATABASE_TIMEOUT = float(os.getenv('DATABASE_TIMEOUT', '10.0'))

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'douyin_videos.xlsx')
VIDEO_DIR = os.path.join(BASE_DIR, 'douyin_videos')

# Category mapping from Chinese to Excel categories
CATEGORY_MAPPING = {
    "日常生活记录(vlog)": "daily_vlog",
    "服装穿搭": "dressing",
    "运动健身": "fitness",
    "美食烹饪": "gourmet",
    "发型": "hair_braided",
    "自制饮料": "homemade_drinks",
    "孩童": "kids",
    "音乐现场": "livehouse",
    "化妆美容": "makeup",
    "绘画": "painting",
    "宠物": "pets",
    "摄影": "photography",
    "科普知识": "popular_science",
    "自然风景": "scenery",
    "街拍": "street_snap"
}

# Video distribution per round
ROUND_VIDEO_COUNTS = {
    1: [10, 6, 4],  # Round 1: 20 videos total
    2: [2, 2, 2]    # Round 2: 6 videos total
}
