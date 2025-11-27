import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from new_backend import FILES,initialize_databases, load_profile, save_profile, get_daily_stats, load_all_databases, show_food_log,show_hydration, show_health_advisor,show_fitness, show_analytics_ad,show_settings,generate_nutrition_plan,show_dashboard


initialize_databases()
if "user" not in st.session_state:
    st.session_state["user"] = load_profile()
user=st.session_state["user"]

#View1
if user is None:
    st.title("🤖🩺 AI Health & Nutrition Analyzer")
    st.markdown("### Let's build your personalized health plan.")

    with st.form("setup_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("First Name")
        gender = c1.radio("Gender", ["Male", "Female"], horizontal=True)
        age = c1.number_input("Age", 10, 100, 25)
        weight = c2.number_input("Weight (kg)", 30, 200, 70)
        height = c2.number_input("Height (cm)", 100, 250, 170)
        st.markdown("---")
        act = st.selectbox("Activity Level",
                           ["Sedentary (Office)", "Lightly Active", "Moderately Active", "Very Active", "Super Active"])
        goal = st.selectbox("Your Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain"])
        w_goal = st.number_input("Daily Water Goal (ml)", 1000, 5000, 2500)

        if st.form_submit_button("Start My Journey"):
            if name:
                new_profile = save_profile(name, age, gender, height, weight, act, goal, w_goal)
                st.session_state["user"] = new_profile
                st.rerun()
            else:
                st.error("Please enter your name.")
else: #Load Databases

    df_food, df_ex, df_sym = load_all_databases()


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


    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Home", "📝 Input Meal Logs", "📊 Nutrition Plan","🩺 Health Advisor",
         "💧 Hydration Tracker", "🏋 Exercise Tracker", "📅 Meal Forecasting", "💡 Smart Tips","📊 Analytics","⚙️ Settings"]
    )

    if page == "🏠 Home":
        st.title("🤖🩺 AI Health & Nutrition Analyzer")
        st.write("Personalized health, diet, hydration and exercise recommendations.")

        st.header(f"Welcome! 👋")
        st.write("""
        Our AI system generates personalized nutrition plans, hydration tracking,
        workout suggestions and weekly meal planning based on your profile.
        PROJECT BY : GROUP 1 SHARFIA, AKASH, AHANA, NOVESH, HARSH.
        """)
        st.divider()
        show_dashboard(user)
    if page == "📝 Input Meal Logs":
        show_food_log(df_food)

    if page == "📊 Nutrition Plan":
        st.header("Your AI-Powered Nutrition Plan")
        if 'user' not in st.session_state:
            st.warning("⚠ Please enter your data in Input Page First.")
        else:
            plan = generate_nutrition_plan()
            df = pd.DataFrame({
                "Nutrient": ["Calories", "Protein (g)", "Carbs (g)", "Fats (g)"],
                "Target": [plan["Calories"], plan["Protein (g)"], plan["Carbs (g)"], plan["Fats (g)"]]
            })
            st.table(df)
            st.subheader("Personalized Tips")
            for tip in plan["Tips"]:
                st.info("💡 " + tip)

    if page =="🩺 Health Advisor":
        show_health_advisor(user,df_sym)

    if page == "💧 Hydration Tracker":
        show_hydration(user)
    if page == "🏋 Exercise Tracker":
        show_fitness(user, df_ex)

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


    if page == "📊 Nutrition Plan":  # example: reuse foods_df if needed
        st.subheader("Search Foods")
        food_query = st.text_input("Search for a food:", key="food_search")
        if food_query:
            results = df_food[df_food["Dish Name"].str.contains(food_query, case=False, na=False)]
            if results.empty:
                st.info("No foods found matching your query.")
            else:
                st.dataframe(results)
    if page=="📊 Analytics":
        show_analytics_ad()
    if page=="⚙️ Settings":
        show_settings(user)





