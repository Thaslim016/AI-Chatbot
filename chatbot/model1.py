from sentence_transformers import SentenceTransformer, util
import torch
import pandas as pd
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

# Handle absolute path to responses.csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'responses.csv')
responses_df = pd.read_csv(CSV_PATH)

def get_response(user_input):
    user_input = user_input.lower().strip()

    # Greeting patterns
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    goodbyes = ["bye", "goodbye", "see you", "take care"]

    if any(greet in user_input for greet in greetings):
        return "👋 Hello! How can I help you today?"

    if any(bye in user_input for bye in goodbyes):
        return "👋 Goodbye! Have a great day ahead."

    # Continue with semantic matching
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    embeddings = model.encode(responses_df['question'].tolist(), convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, embeddings)

    top_score, top_index = torch.max(cosine_scores, dim=1)

    if top_score.item() < 0.6:
        return "🤖 I'm not sure how to answer that. Please try asking something else."

    return responses_df['answer'].iloc[top_index.item()]
