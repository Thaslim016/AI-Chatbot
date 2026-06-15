import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE_DIR, 'data', 'users.db')

def authenticate_user(username, password):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"username": result[1], "role": result[3]}  # (id, username, password, role)
    return None

def create_user(username, password, role="user"):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def add_faq(question, answer):
    faq_path = os.path.join(BASE_DIR, 'data', 'responses.csv')
    faq_df = pd.read_csv(faq_path)
    new_row = pd.DataFrame([{"question": question, "answer": answer}])
    faq_df = pd.concat([faq_df, new_row], ignore_index=True)
    faq_df.to_csv(faq_path, index=False)

def get_all_faqs():
    faq_path = os.path.join(BASE_DIR, 'data', 'responses.csv')
    faq_df = pd.read_csv(faq_path)
    return faq_df.to_dict(orient='records')

def get_analytics():
    return {"status": "Analytics feature coming soon."}
