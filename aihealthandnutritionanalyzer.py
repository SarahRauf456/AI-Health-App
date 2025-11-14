import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Health & Nutrition Analyzer", layout="wide")


st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #0f0f0f, #1a1a1a, #202020);
            color: white;
        }
        .stButton button {
            background-color: #1DB954;
            color: white;
            border-radius: 10px;
        }
        .stTextInput>div>div>input,
        .stSelectbox>div>div>select,
        .stNumberInput>div>div>input {
            background-color: #1e1e1e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)


st.title("🩺 AI Health & Nutrition Analyzer")
st.write("Personalized health, diet, hydration and exercise recommendations.")


page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Home", "📝 Input Data", "📊 Nutrition Plan", "🤖 Diet Chatbot",
     "💧 Hydration Tracker", "🏋️ Simple Exercises", "📅 Meal Forecasting", "💡 Smart Tips"]
)


if page == "🏠 Home":
    st.header("Welcome! 👋")
    st.write("""
    Our AI system generates personalized nutrition plans, hydration tracking,
    workout suggestions and weekly meal planning based on your profile.
    PROJECT BY : GROUP 1 IIT PATNA Sharfia,Novesh, Akash, Ahana, Harsh.   
    """)


if page == "📝 Input Data":
    st.header("Enter Your Details")
    name = st.text_input("Name")
    age = st.number_input("Age", 1, 100, 25)
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 170)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    diet_type = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"])

    if st.button("Save Data"):
        st.session_state['user_data'] = {"name": name, "age": age, "weight": weight,
                                         "height": height, "activity": activity, "diet_type": diet_type}
        st.success("✅ Data saved successfully!")


def generate_nutrition_plan(data):
    bmi = data['weight'] / ((data['height'] / 100) ** 2)

    if data['activity'] == "Low":
        calories = data['weight'] * 25
    elif data['activity'] == "Moderate":
        calories = data['weight'] * 30
    else:
        calories = data['weight'] * 35

    protein = data['weight'] * 1.2
    carbs = calories * 0.5 / 4
    fats = calories * 0.25 / 9
    tips = []
    if bmi < 18.5:
        tips.append("Increase calorie intake with nutrient-dense foods.")
    elif bmi > 25:
        tips.append("Include more vegetables and lean protein for fat loss.")
    else:
        tips.append("Maintain balanced meals & steady exercise.")

    return {"Calories": round(calories), "Protein (g)": round(protein),
            "Carbs (g)": round(carbs), "Fats (g)": round(fats), "Tips": tips}
if page == "📊 Nutrition Plan":
    st.header("Your AI-Powered Nutrition Plan")
    if 'user_data' not in st.session_state:
        st.warning("⚠ Please enter your data in Input Page First.")
    else:
        plan = generate_nutrition_plan(st.session_state['user_data'])
        df = pd.DataFrame({
            "Nutrient": ["Calories", "Protein (g)", "Carbs (g)", "Fats (g)"],
            "Target": [plan["Calories"], plan["Protein (g)"], plan["Carbs (g)"], plan["Fats (g)"]]
        })
        st.table(df)
        st.subheader("Personalized Tips")
        for tip in plan["Tips"]:
            st.info("💡 " + tip)
if page == "🤖 Diet Chatbot":
    st.header("💬 Nutritional & Balanced Diet Chatbot")
    user_q = st.text_input("Ask any diet, nutrition or healthy eating question:")
    if st.button("Ask"):
        st.write("🤖 *AI Suggestion:*")
        st.success("Maintain balance between protein, carbs, fats & stay hydrated. Avoid junk & processed foods.")
if page == "💧 Hydration Tracker":
    st.header("Daily Hydration Tracker")
    water = st.slider("How many glasses of water did you drink today?", 0, 20, 8)
    st.progress(water / 20)
    if water < 8:
        st.warning("⚠ Drink more water to reach your daily hydration target.")
    else:
        st.success("💧 Excellent! Stay consistent.")
if page == "🏋️ Simple Exercises":
    st.header("Simple Exercises by Category")
    category = st.selectbox("Choose Body Area", ["Arms", "Legs", "Core", "Full Body"])
    if category == "Arms":
        st.write("💪 Pushups, Arm Circles, Tricep dips")
    elif category == "Legs":
        st.write("🏃 Squats, Lunges, Leg Raises")
    elif category == "Core":
        st.write("🔥 Plank, Crunches, Mountain Climbers")
    else:
        st.write("💥 Jumping Jacks, Burpees, Skipping Rope")
    st.warning("⚠ DISCLAIMER: Perform exercises carefully. Stop if uncomfortable.")
if page == "📅 Meal Forecasting":
    st.header("Weekly Balanced Diet & Meal Schedule")
    schedule = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Meals": ["High protein", "Balanced carbs", "Hydration focus", "Fiber rich",
                  "Lean meat/Paneer", "Cheat lite day", "Fruit + Salad Day"]
    })
    st.table(schedule)
if page == "💡 Smart Tips":
    st.header("AI Smart Recommendations")
    tips = [
        "Drink 2–3 liters of water daily.",
        "Sleep 7–8 hours for recovery.",
        "Combine cardio & strength training.",
        "Avoid sugary drinks.",
        "Eat whole grains & fresh vegetables."
    ]
    for t in tips:
        st.success("✅ " + t)

