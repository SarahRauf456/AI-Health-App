import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(page_title="AI Health & Nutrition Analyzer", layout="wide")

@st.cache_data
def load_food_data():
    """Load and combine foods.csv and foods2.csv safely."""
    # Load CSVs
    try:
        df1 = pd.read_csv("data/foods.csv")
    except FileNotFoundError:
        df1 = pd.DataFrame()
    try:
        df2 = pd.read_csv("data/foods2.csv")
    except FileNotFoundError:
        df2 = pd.DataFrame()

    # Convert columns to string and strip whitespace
    df1.columns = df1.columns.map(str).str.strip()
    df2.columns = df2.columns.map(str).str.strip()

    # Ensure 'Food' and 'Category' columns exist
    for col in ["Food", "Category"]:
        if col not in df1.columns:
            df1[col] = "Unknown"
        if col not in df2.columns:
            df2[col] = "Unknown"

    # Combine datasets
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Clean string columns
    combined_df["Food"] = combined_df["Food"].astype(str).str.strip()
    combined_df["Category"] = combined_df["Category"].astype(str).str.strip()

    return combined_df

@st.cache_data
def load_exercise_data():
    """Load exercises.csv safely."""
    try:
        df = pd.read_csv("data/exercises.csv")
    except FileNotFoundError:
        df = pd.DataFrame()

    # Convert columns to string and strip whitespace
    df.columns = df.columns.map(str).str.strip()

    # Ensure required columns exist
    for col in ["Exercise", "Category"]:
        if col not in df.columns:
            df[col] = "Unknown"

    # Clean string columns
    df["Exercise"] = df["Exercise"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()

    return df

# -----------------------------
# Load datasets
# -----------------------------
foods_df = load_food_data()
ex_df = load_exercise_data()

# -----------------------------
# Streamlit UI
# -----------------------------

st.title("AI Health & Nutrition Analyzer")

# Food Search Section
st.header("Search for Food")
query = st.text_input("Enter food name:")

if query:
    # Safe search
    results = foods_df[foods_df["Food"].str.contains(query, case=False, na=False)]
    if results.empty:
        st.info("No foods found matching your query.")
    else:
        st.dataframe(results)

# Food Category Dropdown
st.header("Filter Foods by Category")
food_categories = foods_df["Category"].unique() if "Category" in foods_df.columns else ["Unknown"]
selected_food_category = st.selectbox("Choose food category", food_categories)
filtered_foods = foods_df[foods_df["Category"] == selected_food_category]
st.dataframe(filtered_foods)

# Exercise Category Dropdown
st.header("Filter Exercises by Category")
exercise_categories = ex_df["Category"].unique() if "Category" in ex_df.columns else ["Unknown"]
selected_ex_category = st.selectbox("Choose exercise category", exercise_categories)
filtered_exercises = ex_df[ex_df["Category"] == selected_ex_category]
st.dataframe(filtered_exercises)



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
    Sharfia
    Novesh
    Akash
    Ahana
    Harsh
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

