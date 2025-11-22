import pandas as pd
import json
import os
import streamlit as st
from datetime import datetime, timedelta
from src.config import FILES, HYDRATION_FACTORS

def load_data_safe(filepath):
    """Safely loads CSVs handling empty files."""
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            if df.empty: return None
            return df
        except pd.errors.EmptyDataError:
            return None
    return None

def save_profile(name, age, gender, height, weight, activity, goal, water_goal):
    # BMR Calculation (Mifflin-St Jeor)
    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    act_map = {"Sedentary": 1.2, "Lightly": 1.375, "Moderately": 1.55, "Very": 1.725, "Super": 1.9}
    tdee = bmr * act_map.get(activity.split()[0], 1.2)

    # Goal Adjustment
    if goal == "Weight Loss":
        target, macros = tdee - 500, (40, 40, 20)
    elif goal == "Weight Gain":
        target, macros = tdee + 500, (50, 25, 25)
    elif goal == "Muscle Gain":
        target, macros = tdee + 250, (45, 35, 20)
    else:
        target, macros = tdee, (50, 20, 30)

    rec_prot = int((target * (macros[1] / 100)) / 4)

    profile = {
        "Name": name, "Age": age, "Gender": gender, "Height": height,
        "Start_Weight": weight, "Current_Weight": weight,
        "Activity": activity, "Goal": goal,
        "Targets": {"Calories": int(target), "Protein": rec_prot, "Water": water_goal, "Macros_Split": macros}
    }

    with open(FILES["profile"], "w") as f:
        json.dump(profile, f)

    # Initialize Weight Log
    if not os.path.exists(FILES["weight_log"]) or os.stat(FILES["weight_log"]).st_size == 0:
        pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Weight": weight}]).to_csv(FILES["weight_log"],
                                                                                               index=False)
    return profile

def load_profile():
    if os.path.exists(FILES["profile"]):
        with open(FILES["profile"], "r") as f:
            profile = json.load(f)
        # Auto-Fix for old profiles
        if "Start_Weight" not in profile:
            profile["Start_Weight"] = profile.get("Weight", 70)
            profile["Current_Weight"] = profile.get("Weight", 70)
            with open(FILES["profile"], "w") as f: json.dump(profile, f)
        return profile
    return None

def log_data(file, data_dict):
    df_new = pd.DataFrame([data_dict])
    if not os.path.exists(file) or os.stat(file).st_size == 0:
        df_new.to_csv(file, index=False)
    else:
        df_new.to_csv(file, mode='a', header=False, index=False)

def log_beverage_advanced(date_obj, time_obj, beverage, volume):
    factor = HYDRATION_FACTORS.get(beverage, 1.0)
    eff_vol = volume * factor
    log_data(FILES["water_log"], {
        "Date": date_obj.strftime("%Y-%m-%d"),
        "Time": time_obj.strftime("%H:%M:%S"),
        "Beverage": beverage, "Volume_ml": volume, "Effective_Hydration_ml": eff_vol
    })
    st.success("Logged!")

def calculate_streak(df_food):
    """Calculates consecutive days logged, handling NaT errors."""
    if df_food is None or df_food.empty: return 0

    # Convert to datetime and drop invalid dates
    df_food["DateObj"] = pd.to_datetime(df_food["Date"], errors='coerce')
    valid_dates = df_food["DateObj"].dropna().dt.date.unique()

    if len(valid_dates) == 0:
        return 0

    valid_dates.sort()

    streak = 0
    check_date = datetime.now().date()

    # Check today or yesterday to start streak
    if check_date not in valid_dates:
        check_date -= timedelta(days=1)
        if check_date not in valid_dates: return 0

    while check_date in valid_dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak

def get_daily_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {"eaten": 0, "protein": 0, "burnt": 0}

    df_food = load_data_safe(FILES["food_log"])
    if df_food is not None:
        day = df_food[df_food["Date"] == today]
        stats["eaten"] = day["Calories"].sum()
        stats["protein"] = day["Protein"].sum()

    df_ex = load_data_safe(FILES["exercise_log"])
    if df_ex is not None:
        day = df_ex[df_ex["Date"] == today]
        stats["burnt"] = day["Calories Burnt"].sum()
    return stats

def generate_meal_plan(df_food, target_cals, goal, diet_pref, days=3):
    plan = {}
    budgets = {"Breakfast": 0.25, "Lunch": 0.35, "Dinner": 0.30, "Snack": 0.10}

    if diet_pref == "Vegetarian":
        df_food = df_food[df_food["Diet"] == "Veg"]

    if goal == "Muscle Gain":
        df_food = df_food.sort_values(by="Protein per Serving (g)", ascending=False)
    elif goal == "Weight Loss":
        df_food = df_food.sort_values(by="Calories per Serving", ascending=True)

    for day in range(1, days + 1):
        day_meals = []
        total_day = 0
        for meal, ratio in budgets.items():
            budget = target_cals * ratio
            candidates = df_food[
                (df_food["Calories per Serving"] >= budget - 150) & (df_food["Calories per Serving"] <= budget + 150)]
            if candidates.empty: candidates = df_food  # Fallback

            selected = candidates.sample(1).iloc[0]
            qty = max(0.5, min(round(budget / selected["Calories per Serving"], 1), 3.0))
            cals = int(selected["Calories per Serving"] * qty)

            day_meals.append({
                "Type": meal, "Dish": selected["Dish Name"], "Qty": qty,
                "Unit": selected.get("Serving Unit", "svg"), "Cals": cals, "Diet": selected.get("Diet", "Veg")
            })
            total_day += cals
        plan[f"Day {day}"] = {"Meals": day_meals, "Total": total_day}
    return plan

def load_all_databases():
    df_food = load_data_safe(FILES["food_db"])
    df_custom = load_data_safe(FILES["custom_food"])

    if df_food is not None and df_custom is not None:
        df_food = pd.concat([df_custom, df_food], ignore_index=True)
    elif df_custom is not None:
        df_food = df_custom

    df_ex = load_data_safe(FILES["exercise_db"])
    df_sym = load_data_safe(FILES["symptom_db"])

    # Ensure Diet column exists
    if df_food is not None and "Diet" not in df_food.columns:
        df_food["Diet"] = df_food["Dish Name"].apply(
            lambda x: "Non-Veg" if any(k in str(x).lower() for k in ["chicken", "egg", "fish", "mutton"]) else "Veg")

    return df_food, df_ex, df_sym