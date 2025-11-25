import streamlit as st
import pandas as pd
import numpy as np
import pandas as pd
import requests
from io import StringIO

CSV_URL = "https://raw.githubusercontent.com/SarahRauf456/AI-Health-App/refs/heads/main/data/users.csv"
def log_activity(event, details=""):
    new_entry = {
        "timestamp": pd.Timestamp.now(),
        "event": event,
        "details": details
    }
    append_to_csv(new_entry)  
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()


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
    ["📈 Dashboard", "🏠 Home", "📝 Input Data", "📊 Nutrition Plan", "🤖 Diet Chatbot",
     "💧 Hydration Tracker", "🏋 Simple Exercises", "📅 Meal Forecasting", "💡 Smart Tips"]
)


@st.cache_data
def load_food_data():
    """Load and combine foods.csv and foods2.csv safely."""
    try:
        df1 = pd.read_csv("data/foods.csv")
    except FileNotFoundError:
        df1 = pd.DataFrame()
    try:
        df2 = pd.read_csv("data/foods2.csv")
    except FileNotFoundError:
        df2 = pd.DataFrame()

    
    df1.columns = df1.columns.map(str).str.strip()
    df2.columns = df2.columns.map(str).str.strip()

    
    for col in ["Food", "Category"]:
        if col not in df1.columns:
            df1[col] = "Unknown"
        if col not in df2.columns:
            df2[col] = "Unknown"

    combined_df = pd.concat([df1, df2], ignore_index=True)

    
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

    df.columns = df.columns.map(str).str.strip()

    for col in ["Exercise", "Category"]:
        if col not in df.columns:
            df[col] = "Unknown"

    df["Exercise"] = df["Exercise"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()

    return df

foods_df = load_food_data()
ex_df = load_exercise_data()


if page == "🏠 Home":
    st.header("Welcome! 👋")
    st.write("""
    Our AI system generates personalized nutrition plans, hydration tracking,
    workout suggestions and weekly meal planning based on your profile.
    PROJECT BY : GROUP 1 SHARFIA, AKASH, AHANA, NOVESH, HARSH.
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



TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "https://github.com/SarahRauf456/AI-Health-App"
FILE_PATH = "data/users.csv"

def read_csv_from_github():
    file = repo.get_contents(FILE_PATH)
    df = pd.read_csv(StringIO(file.decoded_content.decode()))
    return df, file.sha

def update_csv_in_github(csv_string, sha):
    repo.update_file(FILE_PATH, "update stats", csv_string, sha)

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
        st.write("🤖 AI Suggestion:")
        st.success("Maintain balance between protein, carbs, fats & stay hydrated. Avoid junk & processed foods.")

if page == "💧 Hydration Tracker":
    st.header("Daily Hydration Tracker")
    water = st.slider("How many glasses of water did you drink today?", 0, 20, 8)
    st.progress(water / 20)
    if water < 8:
        st.warning("⚠ Drink more water to reach your daily hydration target.")
    else:
        st.success("💧 Excellent! Stay consistent.")
 if st.button("Save Hydration"):
    log_activity("hydration_saved", f"Water: {water_intake} ml")
    st.success("Hydration saved!")
     

if page == "🏋 Simple Exercises":
    st.header("Simple Exercises by Category")
    exercise_categories = ex_df["Category"].unique() if "Category" in ex_df.columns else ["Unknown"]
    selected_ex_category = st.selectbox("Choose Exercise Category", exercise_categories)
    filtered_exercises = ex_df[ex_df["Category"] == selected_ex_category]
    st.dataframe(filtered_exercises)
    st.warning("⚠ DISCLAIMER: Perform exercises carefully. Stop if uncomfortable.")
if st.button("Save Workout"):
    log_activity("workout_saved", f"Workout: {selected_workout}, Duration: {duration} mins")
    st.success("Workout saved!")


if page == "📅 Meal Forecasting":
    st.header("Weekly Balanced Diet & Meal Schedule")
    schedule = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Meals": ["High protein", "Balanced carbs", "Hydration focus", "Fiber rich",
                  "Lean meat/Paneer", "Cheat lite day", "Fruit + Salad Day"]
    })
    st.table(schedule)
if st.button("Save Meal Plan"):
    log_activity("meal_plan_saved", f"Meal: {meal_result}")
    st.success("Meal data saved!")

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
        


if page == "📊 Nutrition Plan":  
    st.subheader("Search Foods")
    food_query = st.text_input("Search for a food:", key="food_search")
    if food_query:
        results = foods_df[foods_df["Food"].str.contains(food_query, case=False, na=False)]
        if results.empty:
            st.info("No foods found matching your query.")
        else:
            st.dataframe(results)

# --------------------- Dashboard Page ---------------------

if page == "📈 Dashboard":
    st.header("📊 Activity Dashboard")

    # Convert the GitHub CSV data to DataFrame
    df = pd.DataFrame(records)

    if df.empty:
        st.info("No activity recorded yet.")
    else:
        # Show last 10 actions
        st.subheader("🕒 Last 10 Activities")
        st.dataframe(df.tail(10))

        # ------------ Pie Chart: Activity Breakdown ------------
        st.subheader("📦 Activity Breakdown")
        event_counts = df["event"].value_counts()

        fig, ax = plt.subplots()
        ax.pie(event_counts, labels=event_counts.index, autopct="%1.1f%%")
        ax.set_facecolor("#0f0f0f")
        fig.patch.set_facecolor("#0f0f0f")
        st.pyplot(fig)

        # ------------ Hydration Chart ------------
        hydration_data = df[df["event"] == "hydration_saved"].copy()
        if not hydration_data.empty:
            hydration_data["timestamp"] = pd.to_datetime(hydration_data["timestamp"])
            hydration_data["water_ml"] = (
                hydration_data["details"].str.extract(r"(\d+)").astype(int)
            )

            st.subheader("💧 Hydration History")
            fig2, ax2 = plt.subplots()
            ax2.plot(hydration_data["timestamp"], hydration_data["water_ml"])
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Water (ml)")
            ax2.set_facecolor("#0f0f0f")
            fig2.patch.set_facecolor("#0f0f0f")
            st.pyplot(fig2)
        else:
            st.info("No hydration data yet.")

        # ------------ Exercise Chart ------------
        exercise_data = df[df["event"] == "workout_saved"].copy()
        if not exercise_data.empty:
            exercise_data["timestamp"] = pd.to_datetime(exercise_data["timestamp"])
            exercise_data["duration"] = (
                exercise_data["details"].str.extract(r"(\d+)").astype(int)
            )

            st.subheader("🏋️ Exercise Duration Over Time")
            fig3, ax3 = plt.subplots()
            ax3.plot(exercise_data["timestamp"], exercise_data["duration"])
            ax3.set_xlabel("Time")
            ax3.set_ylabel("Minutes")
            ax3.set_facecolor("#0f0f0f")
            fig3.patch.set_facecolor("#0f0f0f")
            st.pyplot(fig3)
        else:
            st.info("No workout data yet.")

        # ------------ Meal Data Table ------------
        meal_data = df[df["event"] == "meal_plan_saved"]
        st.subheader("🍱 Saved Meal Plans")
        if not meal_data.empty:
            st.dataframe(meal_data[["timestamp", "details"]])
        else:
            st.info("No meal plans saved yet.")


