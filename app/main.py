from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import numpy as np
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# === SETUP ===
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index("tds-va")

# === MODELS ===
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini" #gpt-4o-mini #gpt-3.5-turbo

# === Request Model ===
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

# === Vector Search ===
def get_top_matches(query: str, top_k=5):
    print(f"\n🔍 Embedding query: {query}")
    embed = client.embeddings.create(input=[query], model=EMBED_MODEL)
    vec = np.array(embed.data[0].embedding, dtype="float32")

    print("🌐 Searching Pinecone...")
    results = pinecone_index.query(vector=vec.tolist(), top_k=top_k, include_metadata=True)
    return [match.metadata for match in results.matches]

# === Prompt Construction ===
def build_prompt(contexts: List[Dict], question: str):
    context_texts = []
    links = []

    for ctx in contexts:
        title = ctx.get("title", "Discourse")
        text = ctx.get("text", "")
        context_texts.append(f"[{title}] {text}")

        if "url" in ctx:
            links.append({"url": ctx["url"], "text": ctx.get("text", "Discourse post")})

    context_str = "\n\n".join(context_texts)
    prompt = f"""Use the following course and student discussion content to answer the question.
Do NOT make up exam dates or use assumptions if the answer is not in the context. Be concise and helpful.

{context_str}

Question: {question}

Answer:"""
    return prompt, links

# === Main Endpoint ===
@app.post("/api/")
def answer_question(req: QueryRequest):
    print(f"📨 Received question: {req.question}")
    contexts = get_top_matches(req.question, top_k=5)
    prompt, links = build_prompt(contexts, req.question)

    print("🧠 Sending prompt to LLM...")
    try:
        chat = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful TA for the IITM Tools in Data Science course. Avoid making up information. If not found in context, say so clearly."
                },
                {"role": "user", "content": prompt}
            ]
        )
        answer = chat.choices[0].message.content.strip()
        print("✅ LLM answered successfully.")
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return {"error": str(e)}

    return {
        "answer": answer,
        "links": links
    }
