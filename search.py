## TODO: edmund please help me to integrate this with qwen api

def semantic_search(description, messages):
    # Dummy fuzzy match - simulate searching through message texts
    description_lower = description.lower()
    for msg in messages:
        if description_lower in msg["text"].lower():
            return msg
    
    # fallback: return first message
    if messages:
        return messages[0]
    else:
        return None