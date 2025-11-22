import os
import pandas as pd
from src.config import FILES


def initialize_databases():
    """Creates necessary files if they don't exist."""

    # 1. Logs
    if not os.path.exists(FILES["water_log"]):
        pd.DataFrame(columns=["Date", "Time", "Beverage", "Volume_ml", "Effective_Hydration_ml"]).to_csv(
            FILES["water_log"], index=False)

    if not os.path.exists(FILES["weight_log"]):
        pd.DataFrame(columns=["Date", "Weight"]).to_csv(FILES["weight_log"], index=False)

    if not os.path.exists(FILES["food_log"]):
        pd.DataFrame(
            columns=["Date", "Time", "Dish", "Meal Type", "Quantity", "Calories", "Protein", "Carbs", "Fats"]).to_csv(
            FILES["food_log"], index=False)

    # if not os.path.exists(FILES["exercise_log"]):
    #     pd.DataFrame(columns=["Date", "Time", "Activity", "Duration", "Calories Burnt"]).to_csv(FILES["exercise_log"],
    #                                                                                             index=False)
    #
    # # 2. Databases (Defaults)
    # if not os.path.exists(FILES["symptom_db"]):
    #     data = {
    #         "Symptom": ["Headache", "Fever", "Cold", "Indigestion", "Sore Throat", "Fatigue", "Acidity", "Insomnia",
    #                     "Muscle Pain"],
    #         "Possible Causes": ["Dehydration, Stress", "Viral Infection", "Virus", "Overeating", "Infection",
    #                             "Lack of Sleep", "Spicy Food", "Stress/Screen Time", "Overexertion"],
    #         "Remedies": ["Drink Water, Rest", "Paracetamol", "Steam", "Ginger Tea", "Salt Gargle", "Sleep", "Cold Milk",
    #                      "Meditation", "Hot Compress"],
    #         "Foods to Avoid": ["Caffeine", "Cold Water", "Ice Cream", "Oily Food", "Cold Drinks", "Sugar", "Fried Food",
    #                            "Caffeine at night", "Processed Food"],
    #         "Preferred Indian Meal": ["Khichdi", "Moong Dal Soup", "Hot Soup", "Curd Rice", "Warm Turmeric Milk",
    #                                   "Dal Chawal", "Banana/Toast", "Warm Milk", "Protein Salad"],
    #         "Tips / General Medicine": ["Sleep well", "Monitor temp", "Stay warm", "Walk after meal", "Rest voice",
    #                                     "Avoid screens", "Sit upright", "No screens 1hr before bed", "Stretch gently"],
    #         "Screen Time Link": ["High impact (Eye strain)", "No direct link", "No direct link",
    #                              "Snacking while watching TV", "No direct link", "Blue light disrupts sleep",
    #                              "Sedentary lifestyle", "Blue light blocks melatonin", "Poor posture"],
    #         "Severity Level": ["Mild", "Moderate", "Mild", "Mild", "Mild", "Moderate", "Mild", "Moderate", "Mild"],
    #         "Time to Relief": ["2-4 hours", "3-5 days", "1 week", "1 day", "2 days", "2 days", "2 hours", "Varies",
    #                            "2-3 days"],
    #         "Home Remedy Option": ["Lemon water", "Tulsi Tea", "Turmeric Milk", "Ajwain Water", "Honey Ginger",
    #                                "Ashwagandha", "Fennel Seeds", "Chamomile Tea", "Turmeric Paste"]
    #     }
    #     pd.DataFrame(data).to_csv(FILES["symptom_db"], index=False)
    #
    # if not os.path.exists(FILES["food_db"]):
    #     data = {
    #         "Dish Name": ["Roti", "Dal Fry", "Rice", "Paneer Butter Masala", "Chicken Curry", "Egg Curry", "Dosa",
    #                       "Idli", "Upma", "Poha", "Sandwich (Veg)", "Oats"],
    #         "Calories per Serving": [120, 150, 130, 350, 400, 250, 180, 60, 200, 180, 220, 150],
    #         "Protein per Serving (g)": [3, 8, 2, 12, 25, 14, 4, 2, 5, 4, 6, 5],
    #         "Carbohydrates (g)": [20, 15, 28, 10, 5, 3, 25, 12, 30, 35, 30, 25],
    #         "Fats (g)": [1, 5, 0, 25, 20, 18, 6, 0, 7, 5, 8, 3],
    #         "Diet": ["Veg", "Veg", "Veg", "Veg", "Non-Veg", "Non-Veg", "Veg", "Veg", "Veg", "Veg", "Veg", "Veg"],
    #         "Serving Unit": ["1 piece", "1 bowl", "1 bowl", "1 bowl", "1 bowl", "1 bowl", "1 piece", "1 piece",
    #                          "1 plate", "1 plate", "1 piece", "1 bowl"],
    #         "Serving Weight (g)": [40, 150, 150, 200, 250, 200, 80, 40, 150, 150, 120, 150]
    #     }
    #     pd.DataFrame(data).to_csv(FILES["food_db"], index=False)
    #
    # if not os.path.exists(FILES["exercise_db"]):
    #     data = {"Description": ["Running (6mph)", "Walking (brisk)", "Yoga", "Cycling", "Weight Lifting", "Swimming"],
    #             "MET Value": [9.8, 3.5, 2.5, 7.5, 3.5, 8.0]}
    #     pd.DataFrame(data).to_csv(FILES["exercise_db"], index=False)

