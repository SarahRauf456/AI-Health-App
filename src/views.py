import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from src.utils import log_data, log_beverage_advanced, calculate_streak, get_daily_stats, generate_meal_plan, save_profile, load_data_safe
from src.config import FILES, HYDRATION_FACTORS

def show_dashboard(user):
    st.title("🏠 Your Daily Snapshot")
    stats = get_daily_stats()
    target = user['Targets']['Calories']
    net = stats['eaten'] - stats['burnt']

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Calories Eaten", f"{stats['eaten']:.0f}", f"Target: {target}")
    with col2:
        st.metric("Calories Burnt", f"{stats['burnt']:.0f}", "Active")
    with col3:
        st.metric("Protein", f"{stats['protein']:.0f}g", f"Goal: {user['Targets']['Protein']}g")

    df_w = load_data_safe(FILES["water_log"])
    w_today = 0
    if df_w is not None:
        df_w["Date"] = pd.to_datetime(df_w["Date"], errors='coerce')
        today = datetime.now().strftime("%Y-%m-%d")
        w_today = df_w[df_w["Date"] == today]["Effective_Hydration_ml"].sum()
    with col4:
        st.metric("Hydration", f"{w_today:.0f} ml", f"Goal: {user['Targets']['Water']} ml")

    st.divider()

    c_ring, c_streak = st.columns([2, 1])
    with c_ring:
        st.subheader("🎯 Today's Progress")
        fig = go.Figure(go.Pie(
            labels=['Eaten', 'Remaining'],
            values=[net, max(0, target - net)],
            hole=.7, marker_colors=['#FF4B4B', '#F0F2F6'], sort=False
        ))
        fig.update_layout(
            annotations=[dict(text=f"{int(net)}<br>kcal", x=0.5, y=0.5, font_size=20, showarrow=False)],
            showlegend=False, height=220, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c_streak:
        df_f = load_data_safe(FILES["food_log"])
        streak = calculate_streak(df_f)
        st.subheader("🔥 Streak")
        st.metric("Consecutive Days", f"{streak} 🔥")

        st.subheader("⚖️ Weight")
        cw = user.get("Current_Weight", user["Start_Weight"])
        st.metric("Current", f"{cw} kg", delta=f"{cw - user['Start_Weight']:.1f} kg")

def show_food_log(df_food):
    st.title("🍎 Nutrition Logger")
    tab1, tab2 = st.tabs(["Log Meal", "Add Custom Food"])

    with tab1:
        c_d, c_t, c_m = st.columns(3)
        with c_d: log_date = st.date_input("Date", datetime.now())
        with c_t: log_time = st.time_input("Time", datetime.now())
        with c_m: meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        st.divider()

        search = st.text_input("Search Database", placeholder="Type 'Paneer', 'Rice', 'Chicken'...")
        if search and df_food is not None:
            matches = df_food[df_food["Dish Name"].str.lower().str.contains(search.lower())]
            if not matches.empty:
                dish = st.selectbox("Select Dish", matches["Dish Name"].unique())
                sel = df_food[df_food["Dish Name"] == dish].iloc[0]
                qty = st.number_input("Quantity (Servings)", 0.5, 10.0, 1.0)
                cals = sel.get("Calories per Serving", 0) * qty
                st.info(f"Total: {cals:.0f} kcal | Diet: {sel.get('Diet', 'Veg')}")

                if st.button("Add to Log"):
                    log_data(FILES["food_log"], {
                        "Date": log_date.strftime("%Y-%m-%d"),
                        "Time": log_time.strftime("%H:%M:%S"),
                        "Dish": dish, "Meal Type": meal_type, "Quantity": qty,
                        "Calories": cals, "Protein": sel.get("Protein per Serving (g)", 0) * qty,
                        "Carbs": sel.get("Carbohydrates (g)", 0) * qty, "Fats": sel.get("Fats (g)", 0) * qty
                    })
                    st.success("Logged Successfully!")

    with tab2:
        with st.form("new_food"):
            nm = st.text_input("Name")
            diet = st.radio("Type", ["Veg", "Non-Veg"])
            c1, c2 = st.columns(2)
            cal = c1.number_input("Calories", 0)
            prot = c2.number_input("Protein", 0.0)
            c3, c4 = st.columns(2)
            carb = c3.number_input("Carbs", 0.0)
            fat = c4.number_input("Fats", 0.0)
            if st.form_submit_button("Save Food"):
                df = pd.DataFrame([{"Dish Name": nm, "Calories per Serving": cal, "Protein per Serving (g)": prot,
                                    "Carbohydrates (g)": carb, "Fats (g)": fat, "Diet": diet}])
                mode = 'a' if os.path.exists(FILES["custom_food"]) else 'w'
                header = not os.path.exists(FILES["custom_food"])
                df.to_csv(FILES["custom_food"], mode=mode, header=header, index=False)
                st.success("Saved!")
                st.cache_data.clear()

def show_hydration(user):
    st.title("💧 Hydration Tracker")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Log Drink")
        h_date = st.date_input("Date", datetime.now())
        h_time = st.time_input("Time", datetime.now())
        h_bev = st.selectbox("Beverage", list(HYDRATION_FACTORS.keys()))
        h_vol = st.number_input("Volume (ml)", 50, 2000, 250, step=50)
        if st.button("Log Drink"): log_beverage_advanced(h_date, h_time, h_bev, h_vol)

        st.markdown("#### Quick Add")
        if st.button("💧 250ml Water"): log_beverage_advanced(datetime.now(), datetime.now(), "Water", 250)

    with c2:
        st.subheader("History")
        df_w = load_data_safe(FILES["water_log"])
        if df_w is not None:
            d_str = h_date.strftime("%Y-%m-%d")
            df_w["Date"] = df_w["Date"].astype(str)
            day_data = df_w[df_w["Date"] == d_str]
            if not day_data.empty:
                tot = day_data["Effective_Hydration_ml"].sum()
                st.metric("Effective Hydration", f"{tot:.0f} ml", f"Goal: {user['Targets']['Water']} ml")
                st.progress(min(tot / user['Targets']['Water'], 1.0))
                st.plotly_chart(px.pie(day_data, values="Volume_ml", names="Beverage", hole=0.4),
                                use_container_width=True)
            else:
                st.info("No data for this date.")

def show_fitness(user, df_ex):
    st.title("🏃 Fitness Tracker")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Log Workout")
        ex_date = st.date_input("Date", datetime.now())
        ex_time = st.time_input("Time", datetime.now())
        search_ex = st.text_input("Search Activity")
        if search_ex and df_ex is not None:
            matches = df_ex[df_ex["Description"].str.lower().str.contains(search_ex.lower())]
            if not matches.empty:
                act = st.selectbox("Activity", matches["Description"].unique())
                met = matches[matches["Description"] == act].iloc[0]["MET Value"]
                mins = st.number_input("Duration (Mins)", 10, 180, 30)
                burn = met * user["Current_Weight"] * (mins / 60)
                st.success(f"Estimated Burn: {burn:.0f} kcal")
                if st.button("Log Workout"):
                    log_data(FILES["exercise_log"],
                             {"Date": ex_date.strftime("%Y-%m-%d"), "Time": ex_time.strftime("%H:%M:%S"),
                              "Activity": act, "Duration": mins, "Calories Burnt": burn})
                    st.success("Logged!")
    with c2:
        st.subheader("History")
        df_ex_log = load_data_safe(FILES["exercise_log"])
        if df_ex_log is not None:
            st.dataframe(df_ex_log.sort_index(ascending=False), use_container_width=True)

def show_meal_planner(user, df_food):
    st.title("🔮 AI Meal Planner")
    c1, c2 = st.columns([1, 3])
    with c1:
        days = st.slider("Days", 1, 7, 3)
        pref = st.radio("Diet", ["Vegetarian", "Non-Vegetarian"])
        if st.button("Generate Plan"):
            st.session_state["plan"] = generate_meal_plan(df_food, user['Targets']['Calories'], user['Goal'], pref,
                                                          days)
    with c2:
        if "plan" in st.session_state:
            for day, det in st.session_state["plan"].items():
                with st.expander(f"📅 {day} - {det['Total']} kcal"):
                    for m in det["Meals"]:
                        st.write(f"**{m['Type']}**: {m['Qty']} x {m['Dish']} ({m['Diet']})")
                        st.caption(f"{m['Cals']} kcal")

def show_health_advisor(df_sym):
    st.title("🩺 Advanced Symptom Checker")
    if df_sym is not None:
        sym = st.selectbox("I am feeling...", ["Select..."] + sorted(df_sym["Symptom"].unique().tolist()))
        if sym != "Select...":
            res = df_sym[df_sym["Symptom"] == sym].iloc[0]
            st.info(
                f"**Severity:** {res.get('Severity Level', 'N/A')} | **Recovery:** {res.get('Time to Relief', 'N/A')}")
            c1, c2 = st.columns(2)
            with c1:
                st.warning(f"**Causes:** {res['Possible Causes']}")
                st.info(f"**Remedies:** {res['Remedies']}")
            with c2:
                st.error(f"**Avoid:** {res['Foods to Avoid']}")
                st.success(f"**Diet:** {res['Preferred Indian Meal']}")
            with st.expander("💡 Lifestyle & Home Remedies"):
                st.write(f"**Home Remedy:** {res.get('Home Remedy Option', 'N/A')}")
                st.write(f"**Tip:** {res['Tips / General Medicine']}")
                st.write(f"**Screen Time:** {res.get('Screen Time Link', 'N/A')}")

def show_analytics():
    st.title("📈 Comprehensive Analytics")
    df_f = load_data_safe(FILES["food_log"])

    if df_f is not None:
        df_f["DateObj"] = pd.to_datetime(df_f["Date"], errors='coerce')

        # Weekly Summary
        st.subheader("📅 Weekly Summary")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        df_f = df_f.dropna(subset=["DateObj"])
        weekly = df_f[df_f["DateObj"] >= start_date]

        if not weekly.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Cals (7d)", f"{weekly['Calories'].sum():.0f}")
            c2.metric("Avg Daily Cals", f"{weekly['Calories'].sum() / 7:.0f}")
            c3.metric("Total Protein", f"{weekly['Protein'].sum():.0f}g")

        st.divider()
        c_bar, c_pie = st.columns([2, 1])
        with c_bar:
            st.subheader("🔥 Daily Calories")
            daily_sum = df_f.groupby("Date")["Calories"].sum().reset_index()
            st.plotly_chart(px.bar(daily_sum, x="Date", y="Calories", color="Calories"), use_container_width=True)

        with c_pie:
            st.subheader("🥗 Macro Split")
            d = st.date_input("Select Date", datetime.now())
            d_str = d.strftime("%Y-%m-%d")
            d_df = df_f[df_f["Date"] == d_str]
            if not d_df.empty:
                c, p, f = d_df.get("Carbs", 0).sum(), d_df.get("Protein", 0).sum(), d_df.get("Fats", 0).sum()
                if c + p + f > 0: st.plotly_chart(px.pie(values=[c, p, f], names=["Carb", "Prot", "Fat"], hole=0.4),
                                                  use_container_width=True)
            else:
                st.info("No logs for date.")

        st.divider()
        st.subheader("💧 Hydration History")
        df_w = load_data_safe(FILES["water_log"])
        if df_w is not None:
            st.plotly_chart(px.bar(df_w.groupby("Date")["Effective_Hydration_ml"].sum().reset_index(), x="Date",
                                   y="Effective_Hydration_ml"), use_container_width=True)
    else:
        st.info("Start logging food to see analytics.")

def show_settings(user):
    st.title("⚙️ Settings")
    with st.expander("✏️ Edit Profile"):
        new_w = st.number_input("Update Weight (kg)", value=float(user['Current_Weight']))
        new_h = st.number_input("Update Height (cm)", value=float(user['Height']))
        new_age = st.number_input("Update Age", value=int(user['Age']))
        new_act = st.selectbox("Update Activity",
                               ["Sedentary (Office)", "Lightly Active", "Moderately Active", "Very Active",
                                "Super Active"], index=0)
        new_goal = st.selectbox("Update Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain"], index=0)

        if st.button("Save Profile Changes"):
            new_profile = save_profile(user['Name'], new_age, user['Gender'], new_h, new_w, new_act, new_goal,
                         user['Targets']['Water'])
            st.session_state["user"] = new_profile
            st.success("Profile Updated!")
            st.rerun()

    st.divider()
    st.subheader("⬇️ Export Data")
    c1, c2, c3 = st.columns(3)
    if os.path.exists(FILES["food_log"]):
        with open(FILES["food_log"], "rb") as f: c1.download_button("Download Food Log", f, "food_log.csv")
    if os.path.exists(FILES["exercise_log"]):
        with open(FILES["exercise_log"], "rb") as f: c2.download_button("Download Exercise Log", f,
                                                                        "exercise_log.csv")
    if os.path.exists(FILES["weight_log"]):
        with open(FILES["weight_log"], "rb") as f: c3.download_button("Download Weight Log", f, "weight_log.csv")

    st.divider()
    if st.button("🗑️ Reset All Data (Irreversible)", type="primary"):
        for f in FILES.values():
            # Only delete if it's not one of the database files (checking filename)
            if "db" not in f and os.path.exists(f): os.remove(f)
        del st.session_state["user"]
        st.rerun()