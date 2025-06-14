# 📚 TDS Virtual Teaching Assistant

This project is a virtual assistant built to answer student questions from the **Tools in Data Science (TDS)** course of the **IIT Madras Online BSc in Data Science** program.

It provides an intelligent API endpoint that can:
- Understand student queries
- Search both course content and Discourse discussions
- Provide clear, concise, and accurate answers
- Include relevant source links to help students explore further

---

## 🚀 Features

- 🔍 **Semantic Search** using OpenAI embeddings + Pinecone vector DB
- 📚 **Dual-source indexing**: course markdown files + Discourse threads
- 🧠 **GPT-powered answering** with `gpt-3.5-turbo` or `gpt-4o`
- ✅ **Promptfoo evaluation compatible** (for grading the TDS Project)
- 🛠️ Built with **FastAPI**, **FAISS**, **Pinecone**, and **OpenAI APIs**

---

## 📁 Project Structure

```

TDS-Virtual-Teaching-Assistant/
│
├── app/
│   ├── main.py                # FastAPI app for the API endpoint
│   ├── embed\_and\_store.py     # Script to embed content into Pinecone & FAISS
│   ├── discourse\_scraper.py   # Scraper for IITM Discourse threads (auth required)
│
├── processed\_data/
│   ├── tds-course-content.json      # Extracted & chunked markdown content
│   ├── discourse-posts.json         # Posts scraped from Discourse
│
├── rawdata/
│   └── \*.md                   # All markdown files from [https://tds.s-anand.net/](https://tds.s-anand.net/)
│
├── vectorstore/
│   ├── tds\_faiss.index        # Local FAISS index (for fast lookup)
│   └── tds\_faiss\_meta.json    # Metadata for FAISS
│
├── project-tds-virtual-ta-promptfoo.yaml   # Config for Promptfoo test cases
├── requirements.txt
└── README.md

````

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/TDS-Virtual-Teaching-Assistant.git
cd TDS-Virtual-Teaching-Assistant
````

### 2. Install dependencies

```bash
uv venv tdsprj
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file with:

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENV=gcp-starter
```

---

## 📊 Data Preparation

### Scrape & preprocess:

```bash
uv run app/discourse_scraper.py
```

### Embed and store:

```bash
uv run app/embed_and_store.py
```

---

## 🧪 Run the API

```bash
uvicorn app.main:app --reload
```

Test with `curl`:

```bash
curl -X POST http://localhost:8000/api/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Which model should I use: gpt-4o-mini or gpt-3.5-turbo?"}'
```

---

## 🧠 Evaluation (Promptfoo)

Make sure the API is running, then run:

```bash
npx promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
```

Check your score, correctness, and links returned.

---

## 🌐 Deploying

To make your endpoint public, run:

```bash
ngrok http 8000
```

Then update the URL in `project-tds-virtual-ta-promptfoo.yaml`.

---

## ✅ Submission

Submit:

* Your GitHub repo URL
* Your public API endpoint

At: [https://exam.sanand.workers.dev/tds-project-virtual-ta](https://exam.sanand.workers.dev/tds-project-virtual-ta)

---

## 📄 License

This project is licensed under the MIT License.
