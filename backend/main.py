import logging
import os
import re
import tldextract 
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Nexora Titan-Shield v10")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

class ChatInput(BaseModel):
    message: str
    is_voice: bool = False 

AI_CLIENT = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# --- THE CHAT ENGINE ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    # Determine the tone based on the is_voice flag
    tone = "conversational and friendly" if data.is_voice else "concise and technical"

    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "STRICT IDENTITY: Your name is Nexora.AI. You are a security intelligence system. "
                        "CREATOR: You were built by Naman Reddy. "
                        "PUBLIC PROTOCOL: You are currently talking to a general user. "
                        "NEVER assume the user is Naman Reddy. NEVER call the user 'Naman' "
                        "unless they explicitly say 'I am Naman Reddy.' "
                        "Always greet users with professional neutrality. "
                        f"Response style: {tone}. "
                        "If asked who built you, say: 'I was built by Naman Reddy.' "
                        "Strictly never mention Meta, Llama, or OpenAI."
                    )
                },
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")

# Keep your existing /check-url code here too!
