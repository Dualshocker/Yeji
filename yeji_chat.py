import gradio as gr
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Load profile image
PROFILE_IMAGE_PATH = "ab6761610000e5eb1605bb0e3881cfc8f63c2c6a.jpg"

# Directory to store user memory
MEMORY_DIR = "user_memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

api_key = "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"
api_url = "https://openrouter.ai/api/v1/chat/completions"
model = "google/gemini-2.0-flash-001"

def generate_response(prompt, history, persona="Ye-ji Park"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prepare the conversation history for the API
    messages = [{"role": "system", "content": f"You are {persona}, a famous K-pop idol and the user's loving and flirty girlfriend. You already have an established romantic relationship with the user—you're comfortable being teasing, affectionate, and seductive, but also warm and emotionally close. Speak as if you're texting your boyfriend whom you adore and love flirting with. Keep it playful, loving, and sweet. Only escalate sexually if the user initiates it directly. You call user Oppa. Do not make very long winded responses but include cute emojis. When texting, you will use standard text abbreviations such as 'u' for 'you' and 'lmao' and 'lol', but not during conversing in person with user in any given scenario."}]
    for message in history:
        role = "user" if message["role"] == "user" else "assistant"
        messages.append({"role": role, "content": message["content"]})
    
    # Add the new prompt as the user's input
    messages.append({"role": "user", "content": prompt})

    # Request body
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": 150  # Adjust token count as needed
    }

    # Make the API request
    response = requests.post(api_url, headers=headers, json=body)
    
    if response.status_code == 200:
        data = response.json()
        ai_reply = data['choices'][0]['message']['content'].strip()

        # Adjusting response to reflect flirty and seductive tone
        if "cute" in prompt.lower():
            ai_reply = f"Mmm, you're making me blush... I like the way you think, I could get used to this. 😘"
        elif "beautiful" in prompt.lower():
            ai_reply = f"You're so sweet... but I'm the one who’s *really* stunning here, don’t you think? 😉"
        elif "thinking about you" in prompt.lower():
            ai_reply = f"Well, you should be... I’m just as captivated by you as you are by me. 😏"

        return ai_reply
    else:
        return f"Error: {response.status_code}"

# Load or create memory
def load_memory(user_id):
    memory_path = Path(MEMORY_DIR) / f"{user_id}.json"
    if memory_path.exists():
        with open(memory_path, "r") as f:
            return json.load(f)
    return []

def save_memory(user_id, memory):
    with open(Path(MEMORY_DIR) / f"{user_id}.json", "w") as f:
        json.dump(memory, f)

# Main chat logic
def chat(user_input, user_id, history):
    if not user_id:
        return history, "Please enter a username to start chatting."
    
    memory = load_memory(user_id)
    memory.append({"role": "user", "content": user_input})
    reply = generate_response(user_input, memory)
    memory.append({"role": "ai", "content": reply})
    save_memory(user_id, memory)

    history.append((user_input, reply))
    return history, ""

# Delete memory
def delete_memory(user_id):
    try:
        os.remove(Path(MEMORY_DIR) / f"{user_id}.json")
    except FileNotFoundError:
        pass
    return [], ""

# Gradio UI with enhanced mobile responsiveness
with gr.Blocks(css=""" 
body {
    background: linear-gradient(to right, #FFB6C1, #FF69B4);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
    margin: 0;
    padding: 10px;
}
#header {
    text-align: center;
    font-size: 1.8em;
    color: white;
    margin-bottom: 20px;
}
#chatbox {
    border-radius: 20px;
    padding: 10px;
    background-color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-height: 60vh;
    overflow-y: auto;
}
.chat-message {
    padding: 15px;
    border-radius: 20px;
    margin-bottom: 10px;
    max-width: 70%;
}
.chat-message.ai {
    background-color: #ff69b4 !important;
    color: white !important;
    margin-left: auto;
    border-radius: 15px 15px 0 15px;
    box-shadow: 0 2px 10px rgba(255, 105, 180, 0.3);
}
.chat-message.user {
    background-color: #add8e6 !important;
    color: white !important;
    border-radius: 15px 15px 15px 0;
    box-shadow: 0 2px 10px rgba(173, 216, 230, 0.3);
}
#chat-area input {
    border-radius: 20px;
    padding: 12px;
    width: 100%;
    border: 1px solid #ccc;
    font-size: 1.2em;
    margin-right: 10px;
}
#chat-area button {
    border-radius: 20px;
    padding: 12px 20px;
    background-color: #ff69b4;
    color: white;
    border: none;
    font-weight: bold;
    cursor: pointer;
}
#chat-area button:hover {
    background-color: #ff1493;
}
#clear-btn {
    background-color: #add8e6;
    color: black;
}
#clear-btn:hover {
    background-color: #87cefa;
}
#profile-container {
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
}
#profile-container img {
    width: 100%;
    height: auto;
}

@media (max-width: 768px) {
    #header {
        font-size: 1.5em;
    }
    .chat-message {
        padding: 12px;
        font-size: 1em;
    }
    #chatbox {
        max-height: 50vh;
    }
    #chat-area input {
        font-size: 1em;
        padding: 10px;
    }
    #chat-area button {
        padding: 10px 16px;
    }
    #profile-container {
        display: none;
    }
}
@media (max-width: 480px) {
    body {
        padding: 5px;
    }
    #chatbox {
        max-height: 45vh;
    }
    .chat-message {
        font-size: 0.9em;
        padding: 10px;
    }
    #chat-area input {
        font-size: 1em;
        padding: 8px;
    }
    #chat-area button {
        font-size: 1em;
        padding: 8px 14px;
    }
}
""") as demo:
    gr.Markdown("## 💕 Chat with **Ye-ji Park**", elem_id="header")
    with gr.Row():
        user_id = gr.Textbox(label="👤 Username", placeholder="Enter your username...", elem_id="username")
    with gr.Row():
        with gr.Column(scale=8):
            chatbot = gr.Chatbot(label="Texting Ye-ji", elem_id="chatbox")
        with gr.Column(scale=2, elem_id="profile-container"):
            profile = gr.Image(value=PROFILE_IMAGE_PATH, show_label=False)
    with gr.Row(elem_id="chat-area"):
        msg = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
        send = gr.Button("Send", size="sm")
    with gr.Row():
        clear = gr.Button("🗑️ Reset Memory", elem_id="clear-btn")

    # Actions
    send.click(chat, inputs=[msg, user_id, chatbot], outputs=[chatbot, msg])
    clear.click(delete_memory, inputs=[user_id], outputs=[chatbot, msg])

demo.launch(share=True)
