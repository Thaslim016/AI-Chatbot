from sentence_transformers import SentenceTransformer, util
import torch
import pandas as pd
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'responses.csv')
SETTINGS_PATH = os.path.join(BASE_DIR, 'data', 'settings.json')

model = SentenceTransformer('all-MiniLM-L6-v2')
responses_df = None

from llama_cpp import Llama
llm = Llama(model_path=os.path.join(BASE_DIR, "models", "phi-2.Q4_K_M.gguf"))

def load_responses():
    global responses_df
    responses_df = pd.read_csv(CSV_PATH)

load_responses()

def is_ai_enabled():
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            return settings.get("use_ai", False)
    except:
        return False

def ask_ai(prompt):
    response = llm(f"Q: {prompt}\nA:", max_tokens=200)
    return response["choices"][0]["text"].strip()

def match_from_csv(user_input):
    user_input = user_input.lower().strip()
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    goodbyes = ["bye", "goodbye", "see you", "take care"]

    if any(greet in user_input for greet in greetings):
        return "👋 Hello! How can I help you today?"
    if any(bye in user_input for bye in goodbyes):
        return "👋 Goodbye! Have a great day ahead."

    user_embedding = model.encode(user_input, convert_to_tensor=True)
    embeddings = model.encode(responses_df['question'].tolist(), convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, embeddings)
    top_score, top_index = torch.max(cosine_scores, dim=1)

    if top_score.item() < 0.6:
        return "🤖 I'm not sure how to answer that. Please try asking something else."
    return responses_df['answer'].iloc[top_index.item()]

def get_response(user_input):
    if is_ai_enabled():
        return ask_ai(user_input)
    else:
        return match_from_csv(user_input)
