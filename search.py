## TODO: edmund please help me to integrate this with qwen api

# def semantic_search(description, messages):
#     # Dummy fuzzy match - simulate searching through message texts
#     description_lower = description.lower()
#     for msg in messages:
#         if description_lower in msg["text"].lower():
#             return msg
    
#     # fallback: return first message
#     if messages:
#         return None
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Load SBERT model manually from HF
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element is the hidden states
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

def compute_embedding(text):
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded_input)
    return mean_pooling(model_output, encoded_input["attention_mask"]).numpy()

def semantic_search(query, messages, top_k=1):
    texts = [msg["text"] for msg in messages]
    corpus_embeddings = np.vstack([compute_embedding(text) for text in texts])
    query_embedding = compute_embedding(query)

    similarities = cosine_similarity(query_embedding, corpus_embeddings).flatten()
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return messages[top_indices[0]] if len(top_indices) > 0 else None