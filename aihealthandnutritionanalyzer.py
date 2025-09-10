# AI-Health-Appimport streamlit as st
import pandas as pd

# -------------------------
# CONFIG (Dark Theme)
# -------------------------
st.set_page_config(page_title="AI Health & Nutrition Analyzer", layout="wide")

# Inject custom CSS for dark theme
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
        }
        .stButton button {
            background-color: #1DB954;
            color: white;
            border-radius: 10px;
        }
        .stTextInput>div>div>input {
            background-color: #1e1e1e;
            color: white;
        }
        .stSelectbox>div>div>select {
            background-color: #1e1e1e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# APP TITLE
# -------------------------
st.title("🩺 AI Health & Nutrition Analyzer")
st.write("Personalized health and nutrition insights using AI-powered recommendations.")

# -------------------------
# Sidebar Navigation
# -------------------------
page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Home", "📝 Input Data", "📊 Nutrition Plan", "💡 Smart Tips"]
)

# -------------------------
# PAGE 1 - Home
# -------------------------
if page == "🏠 Home":
    st.header("Welcome! 👋")
    st.write("""
    Our project introduces an **AI-powered Health & Nutrition Analyzer** that takes user inputs 
    like age, weight, diet, and lifestyle, and instantly generates customized nutrition plans 
    and health insights.
    
    Unlike generic apps, our system uses AI to provide smart, science-backed recommendations 
    tailored to each individual.  Project By : Group 1
    """)

# -------------------------
# PAGE 2 - Input Data
# -------------------------
if page == "📝 Input Data":
    st.header("Enter Your Details")

    # Collect user data
    name = st.text_input("Name")
    age = st.number_input("Age", 1, 100, 25)
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 170)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    diet_type = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"])

    # Save input to session state
    if st.button("Save Data"):
        st.session_state['user_data'] = {
            "name": name,
            "age": age,
            "weight": weight,
            "height": height,
            "activity": activity,
            "diet_type": diet_type
        }
        st.success("✅ Data saved! Now go to Nutrition Plan page.")

# -------------------------
# Helper Function: Generate Nutrition Plan
# -------------------------
def generate_nutrition_plan(data):
    bmi = data['weight'] / ((data['height'] / 100) ** 2)
    plan = []

    # Basic calorie estimate
    if data['activity'] == "Low":
        calories = data['weight'] * 25
    elif data['activity'] == "Moderate":
        calories = data['weight'] * 30
    else:
        calories = data['weight'] * 35

    # Macronutrient breakdown
    protein = data['weight'] * 1.2  # grams
    carbs = calories * 0.5 / 4
    fats = calories * 0.25 / 9

    # Add personalized tips
    if bmi < 18.5:
        plan.append("Increase calorie intake with nutrient-dense foods.")
    elif bmi > 25:
        plan.append("Focus on a calorie deficit with more vegetables and lean protein.")
    else:
        plan.append("Maintain your current calorie intake with balanced macros.")

    if data['diet_type'] == "Vegan":
        plan.append("Ensure adequate B12 and iron intake.")
    elif data['diet_type'] == "Vegetarian":
        plan.append("Include dairy/eggs for complete proteins.")

    return {
        "Calories": round(calories),
        "Protein (g)": round(protein),
        "Carbs (g)": round(carbs),
        "Fats (g)": round(fats),
        "Tips": plan
    }

# -------------------------
# PAGE 3 - Nutrition Plan
# -------------------------
if page == "📊 Nutrition Plan":
    st.header("Your AI-Powered Nutrition Plan")
    if 'user_data' not in st.session_state:
        st.warning("⚠️ Please enter your details in the Input Data page first.")
    else:
        plan = generate_nutrition_plan(st.session_state['user_data'])

        st.subheader("Daily Targets")
        df = pd.DataFrame({
            "Nutrient": ["Calories", "Protein (g)", "Carbs (g)", "Fats (g)"],
            "Target": [plan["Calories"], plan["Protein (g)"], plan["Carbs (g)"], plan["Fats (g)"]]
        })
        st.table(df)

        st.subheader("Personalized Tips")
        for tip in plan["Tips"]:
            st.info(tip)

# -------------------------
# PAGE 4 - Smart Tips
# -------------------------
if page == "💡 Smart Tips":
    st.header("AI Smart Recommendations")
    st.write("💡 Here are some science-backed health & nutrition tips:")
    tips = [
        "Drink at least 2–3 liters of water daily.",
        "Get 7–8 hours of quality sleep for optimal recovery.",
        "Include a mix of cardio and strength training for best results.",
        "Plan your meals ahead to avoid unhealthy snacking.",
        "Track your progress weekly, not daily, for better motivation."
    ]
    for t in tips:
        st.success("✅ " + t)
