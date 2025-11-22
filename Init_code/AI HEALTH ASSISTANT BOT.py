import pandas as pd
import os
from thefuzz import process
from spellchecker import SpellChecker

CSV_FILE = "health_recommendations.csv"

required_columns = ["Condition","Detected_Disease","Home_Remedy","Meal","What_Not_To_Eat","Sleep","Doctor_Advice , "]

#  Load dataset or create if not exists
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    # Fix missing columns
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=required_columns)
    df.to_csv(CSV_FILE, index=False)

# Spell checker
spell = SpellChecker()

def clean_text(text):
    words = text.split()
    corrected = [spell.correction(word) if word not in spell else word for word in words]
    return " ".join(corrected)

def chatbot():
    global df
    print("🤖 AI Health Assistant Ready! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip().lower()
        if user_input == "exit":
            print("Bot: Take care! 💙 Goodbye.")
            break

        # Auto correct input
        cleaned_input = clean_text(user_input)

        choices = df["Condition"].astype(str).tolist()
        match, score = process.extractOne(cleaned_input, choices)

        if score > 70:
            row = df[df["Condition"] == match].iloc[0]
            print(f"\nBot: Based on what you said, it looks like *{row['Detected_Disease']}* 🌿")
            print(f"👉 Home Remedy: {row['Home_Remedy']}")
            print(f"👉 Meal Advice: {row['Meal']}")
            print(f"🚫 Avoid: {row['What_Not_To_Eat']}")
            print(f"😴 Sleep Advice: {row['Sleep']}")
            print(f"⚠️ Doctor Advice: {row['Doctor_Advice']}\n")
        else:
            print("\nBot: Hmm 🤔 I don’t recognize that condition yet.")
            add = input("Would you like to teach me a remedy for it (YES/NO)? ").strip().lower()
            if add == "yes":
                disease = input("Detected Disease: ")
                remedy = input("Home Remedy: ")
                meal = input("Meal advice: ")
                avoid = input("What should not be eaten: ")
                sleep = input("Sleep advice: ")
                doctor = input("Doctor advice: ")
                new_row = {
                    "Condition": cleaned_input,
                    "Detected_Disease": disease,
                    "Home_Remedy": remedy,
                    "Meal": meal,
                    "What_Not_To_Eat": avoid,
                    "Sleep": sleep,
                    "Doctor_Advice": doctor
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                print("Bot: Thanks! I’ll remember this from now on 🌟\n")
            if add == "no":
                print("Bot: Okay, maybe next time 💡\n")
            else:
                print("BOT : PLESE CHOOSE SOME THING FROM YES OR NO ")
if __name__ == "__main__":
    chatbot()
