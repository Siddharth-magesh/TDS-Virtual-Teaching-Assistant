import os
import json
import faiss
import numpy as np
from openai import OpenAI
from pinecone import Pinecone
from tqdm import tqdm
from pathlib import Path

# === 1. CONFIG ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
PINECONE_INDEX = "tds-va"

# Create index if it doesn't exist
if PINECONE_INDEX not in pc.list_indexes().names():
    print(f"Creating Pinecone index '{PINECONE_INDEX}'...")
    pc.create_index(name=PINECONE_INDEX, dimension=1536, metric="cosine")

pinecone_index = pc.Index(PINECONE_INDEX)

faiss_index = faiss.IndexFlatL2(1536)
faiss_metadata = []

# === 2. LOAD DATA ===
def load_json(path):
    print(f"🔍 Loading data from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

course_data = load_json("processed_data/tds-course-content.json")
discourse_data = load_json("rawdata/discourse_contents/discourse-posts.json")

docs = []
for entry in course_data:
    if entry["content"].strip():
        docs.append({
            "source": "course",
            "text": entry["content"].strip(),
            "meta": {
                "filename": entry["filename"],
                "title": entry["title"],
                "chunk_id": entry["chunk_id"]
            }
        })

for post in discourse_data:
    if post["text"].strip():
        docs.append({
            "source": "discourse",
            "text": post["text"].strip(),
            "meta": {
                "url": post["url"],
                "username": post["username"],
                "created_at": post["created_at"]
            }
        })

print(f"📚 Total documents to embed: {len(docs)}")

# === 3. EMBED & STORE ===
batch_size = 100
for i in tqdm(range(0, len(docs), batch_size), desc="Embedding docs"):
    batch = docs[i:i + batch_size]
    texts = [doc["text"] for doc in batch]

    try:
        response = client.embeddings.create(input=texts, model="text-embedding-3-small")
        embeddings = response.data
    except Exception as e:
        print(f"❌ Embedding failed at batch {i}: {e}")
        continue

    pinecone_vectors = []
    faiss_batch = []

    for j, embed_obj in enumerate(embeddings):
        vec = np.array(embed_obj.embedding, dtype="float32")  # ✅ fix
        metadata = batch[j]["meta"] | {"source": batch[j]["source"]}
        vec_id = f"{batch[j]['source']}-{i+j}"

        pinecone_vectors.append({"id": vec_id, "values": vec.tolist(), "metadata": metadata})
        faiss_batch.append(vec)
        faiss_metadata.append(metadata)

    try:
        faiss_index.add(np.vstack(faiss_batch))  # ✅ batch add
        pinecone_index.upsert(vectors=pinecone_vectors)
        print(f"✅ Embedded and stored batch {i}–{i+batch_size}")
    except Exception as e:
        print(f"⚠️ Failed storing batch {i}: {e}")

# === 4. SAVE FAISS LOCALLY ===
Path("vectorstore").mkdir(exist_ok=True)
faiss.write_index(faiss_index, "vectorstore/tds_faiss.index")
with open("vectorstore/tds_faiss_meta.json", "w", encoding="utf-8") as f:
    json.dump(faiss_metadata, f, indent=2)

print("✅ All embeddings saved to Pinecone and FAISS.")
