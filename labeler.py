
import requests
import streamlit as st

# ---- Settings ----------------------------------------------------------
BUSINESS = "a high-end, fine-dining restaurant"
LABELS = ["food", "pricing", "service", "atmosphere"]
GUIDE = """Label the comment with exactly one word: food, pricing, service, or atmosphere.
If the comment has to do with the taste, quality, presentation, portions, drinks, or the menu / menu items, label it food.
If the comment has to do with the cost, value for money, bill, or prices, label it pricing.
If the comment has to do with the staff, waiting time, reservations, or mistakes with the order or service, label it service.
If the comment has to do with the noise, music, decor, cleanliness, seating, or lighting, label it atmosphere.
If the comment mentions more than one, choose the one the customer seems most bothered by or most focused on."""
MODEL = "openai/gpt-oss-20b"   # if you get a 404, the model was retired: see console.groq.com/docs/models
URL = "https://api.groq.com/openai/v1/chat/completions"
# ------------------------------------------------------------------------


def label_comment(text):
    key = st.secrets["GROQ_API_KEY"]
    prompt = f"You label customer comments for {BUSINESS}.\n{GUIDE}\n\nComment: {text}"
    response = requests.post(
        URL,
        headers={"Authorization": f"Bearer {key}"},
        json={"model": MODEL, "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    label = answer.strip().lower()
    return label if label in LABELS else "unclear"
