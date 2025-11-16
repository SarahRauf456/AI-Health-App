import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Health & Nutrition Analyzer", layout="wide")
@st.cache_data
def load_food_data():
    return pd.read_csv("data/foods.csv")

@st.cache_data
def load_exercise_data():
    return pd.read_csv("data/exercises.csv")

foods_df = load_food_data()
ex_df = load_exercise_data()

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
page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Home", "📝 Input Data", "📊 Nutrition Plan", "🍎 Food Finder", "🤖 Diet Chatbot",
     "💧 Hydration Tracker", "🏋️ Simple Exercises", "📅 Meal Forecasting", "💡 Smart Tips"]
)

st.title("🩺 AI Health & Nutrition Analyzer")
if page == "🏠 Home":
    st.header("Welcome! 👋")
    st.write("""
    Our AI system generates personalized nutrition plans, hydration tracking,
    exercise recommendations and weekly meal planning.
    PROJECT BY : GROUP 1  
    """)
if page == "📝 Input Data":
    st.header("Enter Your Details")
    name = st.text_input("Name")
    age = st.number_input("Age", 1, 100, 25)
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 170)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    diet = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])

    if st.button("Save Data"):
        st.session_state['user'] = {"name": name, "age": age, "weight": weight,
                                    "height": height, "activity": activity, "diet": diet}
        st.success("Data Saved Successfully!")



def generate_plan(data):
    bmi = data['weight'] / ((data['height'] / 100) ** 2)
    calories = data['weight'] * (25 if data['activity']=="Low" else 30 if data['activity']=="Moderate" else 35)
    return {
        "Calories": int(calories),
        "Protein(g)": round(data['weight'] * 1.2),
        "Carbs(g)": round(calories*0.5/4),
        "Fats(g)": round(calories*0.25/9),
        "BMI": round(bmi,2)
    }

if page == "📊 Nutrition Plan":
    st.header("Your AI Nutrition Plan")
    if "user" not in st.session_state:
        st.warning("Please enter your details in Input Data page.")
    else:
        plan = generate_plan(st.session_state["user"])
        st.table(pd.DataFrame(plan.items(), columns=["Metric", "Value"]))



if page == "🍎 Food Finder":
    st.header("Search Nutrition From Database")

    query = st.text_input("Type a food name (e.g., Banana, Rice, Egg):")

    if query:
        results = foods_df[foods_df["Food"].str.contains(query, case=False)]
        if results.empty:
            st.error("No matching foods found.")
        else:
            st.success("Food Found in Dataset:")
            st.dataframe(results)

        
            avg_cal = np.mean(results["Calories"])
            st.info(f"💡 Suggestion: Average calories of searched items = **{avg_cal:.1f} kcal**")
if page == "🤖 Diet Chatbot":
    st.header("Ask Nutrition / Diet Question")
    user_q = st.text_input("Question:")
    if st.button("Ask"):
        st.success("Eat whole foods, manage portion size, stay hydrated & exercise regularly.")
if page == "💧 Hydration Tracker":
    st.header("Daily Water Intake")
    glasses = st.slider("Glasses of water today", 0, 20, 6)
    st.progress(glasses/20)
    st.write("Daily Goal: 8–12 glasses")
if page == "🏋️ Simple Exercises":
    st.header("Exercise Suggestions from Dataset")

    muscle = st.selectbox("Choose category", ex_df["Category"].unique())

    selected = ex_df[ex_df["Category"] == muscle]
    st.table(selected[["Exercise", "Duration(min)", "Calories Burned"]])
if page == "📅 Meal Forecasting":
    st.header("Weekly Diet Schedule")
    schedule = pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                             "Meals":["High Protein","Veg Balanced","Hydration","Fiber Rich",
                                      "Lean Protein","Light Cheat","Smoothies/Fruits"]})
    st.table(schedule)
if page == "💡 Smart Tips":
    st.header("Smart Recommendations")
    tips = ["Drink 2-3 liters water daily","7-8 hrs sleep","Add protein to every meal",
            "Avoid sugary foods","Exercise 30 mins daily"]
    for t in tips:
        st.success("✔ " + t)

