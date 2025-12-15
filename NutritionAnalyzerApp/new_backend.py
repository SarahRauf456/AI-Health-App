
import pandas as pd
import json
import os
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go


BAS_DIR=os.path.dirname(os.path.abspath(__file__))
def get_path(filename):
    return os.path.join(BAS_DIR,filename)

FILES={"profile":get_path("user_profile.json"),
       "food_log":get_path("food_log.csv"),
       "food_log":get_path("food_log.csv"),
       "exercise_log":get_path("exercise_log.csv"),
       "water_log":get_path("water_log_detailed.csv"),
       "weight_log":get_path("weight_log.csv"),
       "custom_food":get_path("custom_log.csv"),
       "food_db": get_path("Enhanced_Indian_Food_Nutrition.csv"),
    "exercise_db": get_path("Compendium_of_Physical_Activities_2024.csv"),
    "symptom_db": get_path("symptom_database.csv"),
}

HYDRATION_FACTORS = {
    "Water": 1.0, "Milk": 0.99, "Tea": 0.98, "Coffee": 0.90,
    "Juice": 0.95, "Soda": 0.90, "Alcohol": 0.80, "Sports Drink": 1.0
}

def initialize_databases():
    if not os.path.exists(FILES["food_log"]):
        pd.DataFrame(columns=["Date","Time","Dish","Meal Type","Qunatity","Calories","Protein", "Carbs", "Fats"].to_csv(FILES["food_log"],index=False))
    if not os.path.exists(FILES["water_log"]):  
        pd.DataFrame(columns=["Date","Time","Beverage","Volume_ml","Effective_Hydration_ml"].to_csv(FILES["water_log"],index=False))
    if not os.path.exists(FILES["weight_log"]):
        pd.DataFrame(columns=["Date","weight"].to_csv(FILES["weight_log"],index=False))
    if not os.path.exists(FILES["exercise_log"]):
        pd.DataFrame(columns=["Date","Time","Activity","Duration","Calories Burnt"].to_csv(FILES["exercise_log"],index=False))                            

def load_data_safe(filepath):
    if os.path.exists(filepath):
        try:
            return pd.read_csv(filepath)
        except pd.errors.EmptyDataError:
            return None
        

def log_data(filename,data_dict):
    df_new=pd.DataFrame([data_dict])
    if not os.path.exists(filename):
        df_new.to_csv(filename,index=False)

    else:
        df_new.to_csv(filename,mode="a",header=False,index=False) 


def save_profile(name, age, gender, height, weight, activity, goal, water_goal):
    if gender=="Male":
        bmr=(10*weight)+(6.25*height)-(5*age)+5
    else:
        bmr=(10*weight)+(6.25*height)-(5*age)-161

    
    if activity=="Sedentary (Office)":
        act=1.2
    elif activity==  "Lightly Active"  :
        act=1.375

    elif activity==   "Moderately Active" :
        act=1.55

    elif activity==  "Very Active"  :  
        act=1.725

    elif activity==   "Super Active" :    
        act=1.9  
    tdee=bmr*act
    if goal == "Weight Loss":
        target, macros = tdee - 500, (40, 40, 20)
    elif goal == "Weight Gain":
        target, macros = tdee + 500, (50, 25, 25)
    elif goal == "Muscle Gain":
        target, macros = tdee + 250, (45, 35, 20)
    else:
        target, macros = tdee, (50, 20, 30)

    rec_prot= int(target*(macros[1]/100)/4)    

    profile={"Name":name,"Age":age,"Gender":gender,"Height":height,
                  "Start_Weight":weight,"Current_Weight":weight,
                  "Activity":activity,"Goal":goal,
                  "Targets":{"Calories":int(target),"Protein":rec_prot,
                             "Water":water_goal,"Macros_split":macros}}

    
    with open(FILES["profile"], "w") as f:
        json.dump(profile, f)

      # Initialize Weight Log
    if not os.path.exists(FILES["weight_log"]) or os.stat(FILES["weight_log"]).st_size == 0:
        pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Weight": weight}]).to_csv(FILES["weight_log"],
                                                                                               index=False)
    return profile
def load_profile():
    if os.path.exists(FILES["profile"]):
        with open(FILES["profile"],"r") as f:
            profile=json.load(f)

        return profile        
    return None


def log_data(file,data_dict):
    df_new=pd.DataFrame(data_dict)

    if not os.path.exists(file) or os.stat(file).st_size==0:
        df_new.to_csv(file,index=False)
    else:
        df_new.to_csv(file,mode="a",header=False,index=False)    



def log_beverage_advanced(date_obj,time_obj,beverage,vol):
    factor=HYDRATION_FACTORS.get(beverage,1.0)
    eff_vol=factor*vol
    log_data(FILES["water_log"],[{"Date":date_obj.strftime("%Y-%m-%d")
                                 ,"Time":time_obj.strftime("%H:%M:%S"),
                                 "Beverage":beverage,"Volume":vol,
                                 "Effective_volume":eff_vol}])

    st.success("Logged!")


def load_all_databases():
    df_food=load_data_safe(FILES["food_db"])    
    df_custom=load_data_safe(FILES["custom_food"])
    if df_food is not None and df_custom is not None:
        df_food= pd.concat([df_food,df_custom],ignore_index=True)
    if df_custom is not None:
        df_food=df_custom
    df_ex=load_data_safe(FILES["exercise_db"])   
    df_sym=load_data_safe(FILES["symptom_db"]) 

    return df_food,df_ex,df_sym

def get_daily_stats():
    today=datetime.now().strftime("%Y-%m-%d")
    stats={"eaten":0,"protein":0,"burnt":0}
    df_food=load_data_safe(FILES["food_log"])
    if df_food is not None:
        day=df_food[df_food["Date"]==today]
        stats["eaten"]=day["Calories"].sum()
        stats["protein"]=day["Protein"].sum()
    df_ex=load_data_safe(FILES["exercise_log"])   
    if df_ex is not None:
        day=df_ex[df_ex["Date"]==today]
        stats["burnt"]=day["Calories Burnt"].sum()

    return stats

def get_streak(df_food):
    log_dates=set(pd.to_datetime(df_food["Date"]).dt.date)
    today=datetime.now().date()
    yesterday=today-timedelta(days=1)
    if today not in log_dates and yesterday  not in log_dates:
        return 0
    if today in log_dates:
        current_date=today

    else :current_date=yesterday    
    streak=0
    while current_date in log_dates:
        streak+=1
        current_date=current_date-timedelta(days=1)    
    return streak   
def show_dashboard(user):
    st.title("Your Daily Snapshot")
    stats=get_daily_stats()
    net=stats["eaten"]-stats["burnt"]
    target=user["Targets"]["Calories"]
    c1,c2,c3,c4 =st.columns(4)
    with c1:
        st.metric("Calories Eaten", f"{stats['eaten']:.0f}", f"Target: {target}")
    with c2:
        st.metric("Calories Burnt",f"{stats["burnt"]:.0f}","Active" )

    with c3:
        st.metric("Protein",f"{stats["protein"]}",f"Goal: {user["Targets"]["Protein"]}g  ")
    df_w = load_data_safe(FILES["water_log"])
    w_today = 0
    if df_w is not None:
        df_w["Date"] = pd.to_datetime(df_w["Date"], errors='coerce')
        today = datetime.now().strftime("%Y-%m-%d")
        w_today = df_w[df_w["Date"] == today]["Effective_Hydration_ml"].sum()
    with c4:
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
        streak = get_streak(df_f)
        st.subheader("🔥 Streak")
        st.metric("Consecutive Days", f"{streak} 🔥")

        st.subheader("⚖️ Weight")
        cw = user.get("Current_Weight", user["Start_Weight"])
        st.metric("Current", f"{cw} kg", delta=f"{cw - user['Start_Weight']:.1f} kg")


def show_analytics_ad():
    st.title("Nutrition Analytics")
    food_log=load_data_safe(FILES["food_log"])
    if food_log is None or food_log.empty:
        st.write("No food data available")


    st.subheader("Daily Calorie Intake")
    food_log["Date"]=pd.to_datetime(food_log["Date"])
    daily_stats=food_log.groupby("Date")["Calories"].sum().reset_index()
    fig=px.bar(daily_stats,x="Date",y="Calories",title="Daily Calorie Intake")
    st.plotly_chart(fig,use_container_width=True)
    st.divider()
    st.subheader("🍰 Daily Macro Breakdown")
    selected_date=st.date_input("Select Date",datetime.now())
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### **Actual Intake**")
        filter=food_log["Date"]==pd.to_datetime(selected_date)
        day_data=food_log[filter]
        if day_data is not None and not day_data.empty:
            day_prot=day_data["Protein"].sum()
            day_carbs=day_data["Carbs"].sum()
            day_fat=day_data["Fats"].sum()
            if day_prot+day_carbs+day_fat>0:
                fig2=px.pie(names=["Protein","Carbs","Fat"],
                values=[day_prot,day_carbs,day_fat],
            title=f"Actual:{selected_date}",hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig2,use_container_width=True)
        else:
            st.warning(f"No data available for the {selected_date.strftime('%Y-%m-%d')}")
    with c2:
        st.markdown("#### **Target Intake**")
        target=generate_nutrition_plan()
        prot=target["Protein (g)"]
        carbs=target["Carbs (g)"]
        fats=target["Fats (g)"]
        fig3=px.pie(names=["Protein","Carbs","Fat"],
        values=[prot,carbs,fats],
        title="Reccomended Goal",hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig3,use_container_width=True)
        

    st.divider()
    st.subheader("wk Weekly Summaries")


    weekly_stats = food_log.set_index("Date").resample('W')["Calories"].sum().reset_index()

    weekly_stats["Week"] = weekly_stats["Date"].dt.strftime("Week of %Y-%m-%d")

    fig_weekly = px.bar(weekly_stats, x="Week", y="Calories",
                        title="Total Calories per Week",
                        text_auto=True,  
                        color="Calories", color_continuous_scale="Greens")

    st.plotly_chart(fig_weekly, use_container_width=True)

def generate_nutrition_plan():
    with open(FILES["profile"],"r") as f:
        data=json.load(f)
        w=data["Current_Weight"]
        h=data["Height"]
        h_m=h/100
        bmi= (w/(h_m)**2)
        act =data["Activity"]
        calories = data["Targets"]["Calories"]
        protein = data["Targets"]["Protein"]
        macros_split = data["Targets"]["Macros_split"]
        carb_per,prot_per,fats_per=macros_split

        protein_g = (calories * prot_per / 100) / 4  # 4 kcal per gram
        carbs_g = (calories * carb_per / 100) / 4
        fats_g = (calories * fats_per / 100) / 9  # 9 kcal per gram

        tips = []
        if bmi < 18.5:
            tips.append("Increase calorie intake with nutrient-dense foods.")
        elif bmi > 25:
            tips.append("Include more vegetables and lean protein for fat loss.")
        else:
            tips.append("Maintain balanced meals & steady exercise.")

        return {"Calories": round(calories), "Protein (g)": round(protein_g),
                "Carbs (g)": round(carbs_g), "Fats (g)": round(fats_g), "Tips": tips}

def show_fitness(user,df_ex):
    st.title("🏃 Fitness Tracker")

    c1,c2 =st.columns(2)
    with c1:
        st.subheader("Log workout")
        date=st.date_input("Date",datetime.now())
        time=st.time_input("Time",datetime.now())
        search=st.text_input("Search Activity")
        if search and df_ex is not None:
            matches=df_ex[df_ex["Description"].str.lower().str.contains(search.lower())]
            if not matches.empty:
                act=st.selectbox("Choose Activity",matches["Description"].unique())
                mins=st.number_input("Duration (Mins)",10,180,30)
                duration=mins/60

                final=matches[matches["Description"]==act].iloc[0]["MET Value"]
                burn=final*duration*user["Current_Weight"]
                st.success(f"Estimated Burnt:{burn:.0f}kcal")
                if st.button("Log Workout"):
                    data_dict={"Date":date.strftime("%Y-%m-%d"),"Time":time.strftime("%H:%M:%S"),"Activity":act,"Duration":mins,"Calories Burnt":burn}
                    log_data(FILES["exercise_log"],[data_dict])
                    st.success("Logged!")

    with c2:
        st.subheader("History")
        exercise_log=load_data_safe(FILES["exercise_log"]) 
        if exercise_log is not None and not exercise_log.empty:
            st.dataframe(exercise_log.sort_index(ascending=False),use_container_width=True)


def show_food_log(df_food):
    st.title("🍎 Nutrition Logger") 
    t1,t2=st.tabs(["Log Meal","Add Custom Food"])
    with t1:
        c1,c2,c3=st.columns(3) 
        with c1:
            log_date=st.date_input("Date",datetime.now())
        with c2:
            log_time=st.time_input("Time",datetime.now())
        with c3:
            meal_type=st.selectbox("Meal Type",["Breakfast","Lunch","Dinner","Snack"])
        st.divider()
        search=st.text_input("Search Database",placeholder="Type 'Paneer','Rice','Chicken'")  
        if search and df_food is not None:
            matches=df_food[df_food["Dish Name"].str.lower().str.contains(search.lower())] 
            if not matches.empty  :
                dish=st.selectbox("Select Dish",matches["Dish Name"].unique())
                sel=df_food[df_food["Dish Name"]==dish].iloc[0]
                qty=st.number_input("Quantity (Servings)",0.5,10.0,1.0)
                cals=sel.get("Calories per Serving",0)*qty
                st.info(f"Total:{cals:.0f} kcal | Diet : {sel.get('Diet','Veg')}")
                if st.button("Add to Log"):
                    data_dict={"Date":log_date.strftime("%Y-%m-%d"),
                    "Time":log_time.strftime("%H:%M:%S"),"Dish":dish,"Meal Type":meal_type,
                    "Quantity":qty,"Calories":cals,"Protein":sel.get("Protein per Serving (g)",0)*qty,
                    "Carbs":sel.get("Carbohydrates (g)",0)*qty,"Fats":sel.get("Fats (g)",0)*qty}
                    log_data(FILES["food_log"],[data_dict])
                    st.success("Logged Successfully!")
    with t2:
        with st.form("new _food"):
            nm=st.text_input("Name")
            diet=st.radio("Type",["Veg","Non-Veg"])
            c1,c2,c3,c4=st.columns(4)
            cal=c1.number_input("Calories",0.0)
            prot=c2.number_input("Protein",0.0)
            carbs=c3.number_input("Carbs",0.0)
            fats=c4.number_input("Fats",0.0)
            if st.form_submit_button("Save Food"):
                data_dict={"Dish Name": nm,"Calories per Serving":cal,"Protein per Serving (g)": prot,
                "Carbohydrates (g)":carbs,"Fats (g)":fats,"Diet":diet}
                df=pd.DataFrame(data_dict,index=[0])
                if os.path.exists(FILES["custom_food"]):
                    df.to_csv(FILES["custom_food"],mode="a",header=False,index=False)
                else:
                    df.to_csv(FILES["custom_food"],mode="w",index=False,header=True)   
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
        if st.button("Log Drink"):
            log_beverage_advanced(h_date, h_time, h_bev, h_vol)

        st.markdown("#### Quick Add")
        if st.button("💧 250ml Water"): 
            log_beverage_advanced(datetime.now(), datetime.now(), "Water", 250)

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


def show_health_advisor(user,df_sym):
    st.title("🩺 Advanced Symptom Checker")
    if df_sym is not None:
        name= user.get("Name")
        st.subheader(f"Hello {name}")
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
            if "db" not in f and os.path.exists(f): os.remove(f)
        del st.session_state["user"]
        st.rerun()
