import os

# Get the absolute path of the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# File System Paths (Updated to point to DATA_DIR)
FILES = {
    "profile": os.path.join(DATA_DIR, "user_profile.json"),
    "food_log": os.path.join(DATA_DIR, "food_log.csv"),
    "exercise_log": os.path.join(DATA_DIR, "exercise_log.csv"),
    "water_log": os.path.join(DATA_DIR, "water_log_detailed.csv"),
    "weight_log": os.path.join(DATA_DIR, "weight_log.csv"),
    "custom_food": os.path.join(DATA_DIR, "custom_foods.csv"),
    "food_db": os.path.join(DATA_DIR, "Enhanced_Indian_Food_Nutrition.csv"),
    "exercise_db": os.path.join(DATA_DIR, "Compendium_of_Physical_Activities_2024.csv"),
    "symptom_db": os.path.join(DATA_DIR, "symptom_database.csv")
}

# Hydration Constants
HYDRATION_FACTORS = {
    "Water": 1.0, "Milk": 0.99, "Tea": 0.98, "Coffee": 0.90,
    "Juice": 0.95, "Soda": 0.90, "Alcohol": 0.80, "Sports Drink": 1.0
}