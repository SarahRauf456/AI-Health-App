import pandas as pd
import os

# Optional dependencies (for fuzzy matching & spell correction)
try:
    from thefuzz import process as fuzz_process
except Exception:
    fuzz_process = None

try:
    from spellchecker import SpellChecker
except Exception:
    SpellChecker = None

CSV_FILE = "health_recommendations.csv"

# ✅ Exact column order (General_Medicines removed)
required_columns = [
    "Condition",
    "Detected_Disease",
    "Home_Remedy",
    "Meal",
    "What_Not_To_Eat",
    "Sleep",
    "Doctor_Advice",
    "Possible_Causes",
    "Screen_Time_Guide",
    "Sleep_Cycle_Guide",
    "Preferred_Indian_Meal",
    "Severity_Level",
    "Time_to_Relief",
]

# Load or create dataset
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    df = df[required_columns]
else:
    df = pd.DataFrame(columns=required_columns)
    df.to_csv(CSV_FILE, index=False)

# Optional spell checker
spell = SpellChecker() if SpellChecker else None

def clean_text(text):
    """Lowercase, strip, and optionally spell-correct input."""
    text = (text or "").strip().lower()
    if not spell:
        return text
    words = text.split()
    unknown = spell.unknown(words)
    corrected = [(spell.correction(w) if w in unknown else w) for w in words]
    return " ".join(corrected)

def best_match(cleaned_input, choices):
    """Fuzzy match user input to condition list."""
    choices = [str(c) if pd.notna(c) else "" for c in choices]

    if fuzz_process is not None:
        match, score = fuzz_process.extractOne(cleaned_input, choices) if choices else (None, 0)
        return match, (score or 0)

    # Fallback if thefuzz not installed
    import difflib
    best, best_score = None, 0.0
    for c in choices:
        s = difflib.SequenceMatcher(None, cleaned_input, c.lower()).ratio() * 100
        if s > best_score:
            best, best_score = c, s
    return best, int(best_score)

def pretty_print_row(row):
    """Formatted output for chatbot replies."""
    print(f"\nBot: Based on what you said, it looks like *{row['Detected_Disease']}* 🌿")
    if str(row.get('Possible_Causes', '')).strip():
        print(f"🧩 Possible Causes: {row['Possible_Causes']}")
    print(f"🏠 Home Remedy: {row['Home_Remedy']}")
    print(f"🍽️ Meal Advice: {row['Meal']}")
    if str(row.get('Preferred_Indian_Meal','')).strip():
        print(f"🇮🇳 Preferred Indian Meal: {row['Preferred_Indian_Meal']}")
    print(f"🚫 Avoid: {row['What_Not_To_Eat']}")
    if str(row.get('Screen_Time_Guide','')).strip():
        print(f"📱 Screen Time Guide: {row['Screen_Time_Guide']}")
    if str(row.get('Sleep_Cycle_Guide','')).strip():
        print(f"🛌 Sleep Cycle Guide: {row['Sleep_Cycle_Guide']}")
    print(f"😴 Sleep Advice: {row['Sleep']}")
    if str(row.get('Severity_Level','')).strip():
        print(f"📈 Severity Level: {row['Severity_Level']}")
    if str(row.get('Time_to_Relief','')).strip():
        print(f"⏱️ Time to Relief: {row['Time_to_Relief']}")
    print(f"⚠️ Doctor Advice: {row['Doctor_Advice']}\n")

def prompt_yes_no(msg):
    """Get a YES/NO response."""
    while True:
        ans = input(f"{msg} (YES/NO): ").strip().lower()
        if ans in ("yes", "y"): return True
        if ans in ("no", "n"): return False
        print("BOT: Please choose YES or NO.")

def chatbot():
    global df
    print("🤖 AI Health Assistant Ready! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Bot: Take care! 💙 Goodbye.")
            break

        cleaned_input = clean_text(user_input)
        choices = df["Condition"].astype(str).str.lower().tolist()
        match, score = best_match(cleaned_input, choices)

        if match is not None and score >= 70:
            row = df[df["Condition"].astype(str).str.lower() == match.lower()].iloc[0]
            pretty_print_row(row)
        else:
            print("\nBot: Hmm 🤔 I don’t recognize that condition yet.")
            if prompt_yes_no("Would you like to teach me a remedy for it"):
                print("Great — please provide the details below:")
                detected = input("Detected Disease: ").strip()
                home_rem = input("Home Remedy: ").strip()
                meal = input("Meal advice: ").strip()
                avoid = input("What should not be eaten: ").strip()
                sleep = input("Sleep advice: ").strip()
                doctor = input("Doctor advice: ").strip()
                causes = input("Possible Causes: ").strip()
                screen_guide = input("Screen Time Guide: ").strip()
                sleep_cycle = input("Sleep Cycle Guide: ").strip()
                pref_ind_meal = input("Preferred Indian Meal: ").strip()
                severity = input("Severity Level: ").strip()
                relief_time = input("Time to Relief: ").strip()

                new_row = {
                    "Condition": cleaned_input,
                    "Detected_Disease": detected,
                    "Home_Remedy": home_rem,
                    "Meal": meal,
                    "What_Not_To_Eat": avoid,
                    "Sleep": sleep,
                    "Doctor_Advice": doctor,
                    "Possible_Causes": causes,
                    "Screen_Time_Guide": screen_guide,
                    "Sleep_Cycle_Guide": sleep_cycle,
                    "Preferred_Indian_Meal": pref_ind_meal,
                    "Severity_Level": severity,
                    "Time_to_Relief": relief_time
                }

                df = pd.concat([df, pd.DataFrame([new_row])[required_columns]], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                print("Bot: Thanks! I’ll remember this from now on 🌟\n")
            else:
                print("Bot: Okay, maybe next time 💡\n")

if __name__ == "__main__":
    chatbot()
